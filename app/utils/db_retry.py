"""
Utilidades para manejo robusto de errores de base de datos.

Este modulo provee dos tipos de herramientas:
  1. Decoradores para reintentar operaciones de BD ante fallos transitorios.
  2. Funciones para convertir errores tecnicos de SQLite en mensajes amigables.

Por que necesitamos reintentos (retry):
    SQLite es una base de datos de archivo. En aplicaciones de escritorio con
    multiples ventanas abiertas al mismo tiempo (o con hilos en segundo plano),
    es posible que dos operaciones intenten escribir al mismo tiempo. SQLite
    maneja esto con bloqueos: si la BD esta bloqueada por otra operacion,
    lanza un sqlite3.OperationalError con el mensaje "database is locked".
    En vez de fallar inmediatamente, es mejor esperar un momento y reintentar.

Backoff exponencial:
    Para no sobrecargar la BD con reintentos rapidos, el tiempo de espera
    entre reintentos se multiplica por un factor (backoff) en cada intento:
    - Intento 1: esperar 0.1 segundos
    - Intento 2: esperar 0.2 segundos (0.1 * 2)
    - Intento 3: esperar 0.4 segundos (0.2 * 2)
    Este patron se llama "exponential backoff" y es un estandar en sistemas
    distribuidos para manejar contention de recursos.

Por que sanitizar errores:
    Los mensajes de error internos de SQLite pueden contener informacion
    sensible como nombres de tablas, columnas, o valores. Al mostrarle un
    error al usuario, se reemplaza el mensaje tecnico por uno generico
    y amigable, sin exponer detalles de la implementacion interna.
"""

import time
import sqlite3
from functools import wraps
from app.utils.logger import AppLogger

# Logger para este modulo. Usara 'app.utils.db_retry' como nombre en los logs.
logger = AppLogger.get_logger(__name__)


def retry_on_db_error(max_retries=3, delay=0.1, backoff=2):
    """
    Decorador de fabrica que agrega logica de reintento a funciones de BD.

    Un decorador de fabrica es una funcion que RETORNA un decorador.
    Se llama asi porque acepta parametros de configuracion y "fabrica"
    un decorador personalizado con esos parametros.

    Uso:
        @retry_on_db_error(max_retries=3, delay=0.1, backoff=2)
        def mi_funcion_de_bd():
            conn = get_connection()
            conn.execute("INSERT INTO ...")
            conn.commit()

    Comportamiento:
        - Si la funcion lanza sqlite3.OperationalError con "locked" o "busy":
          espera 'delay' segundos y reintenta hasta 'max_retries' veces.
        - Si se agotan los reintentos: relanza la excepcion original.
        - Si el error de SQLite NO es de bloqueo (ej. columna no existe):
          relanza inmediatamente sin reintentar.
        - Para cualquier otro tipo de excepcion (no SQLite): relanza sin reintentar.

    Parametros:
        max_retries (int): Maximo numero de intentos antes de rendirse. Default: 3.
        delay (float):     Segundos a esperar antes del primer reintento. Default: 0.1.
        backoff (int):     Factor multiplicador del delay entre reintentos. Default: 2.
                           Con delay=0.1 y backoff=2: esperas de 0.1, 0.2, 0.4 segundos.

    Returns:
        Decorador que envuelve la funcion con la logica de reintento.
    """
    def decorator(func):
        @wraps(func)  # preserva nombre, docstring y metadatos de la funcion original
        def wrapper(*args, **kwargs):
            retries = 0           # contador de intentos realizados
            current_delay = delay # delay actual (aumenta con backoff exponencial)

            while retries < max_retries:
                try:
                    # Intentar ejecutar la funcion original
                    return func(*args, **kwargs)

                except sqlite3.OperationalError as e:
                    retries += 1

                    # Si ya agotamos todos los reintentos, relanzar el error
                    if retries >= max_retries:
                        logger.error(f"Max reintentos alcanzados para {func.__name__}: {str(e)}")
                        raise

                    # Verificar si el error es de bloqueo (vale la pena reintentar)
                    error_msg = str(e).lower()
                    if 'locked' in error_msg or 'busy' in error_msg:
                        # BD bloqueada por otra operacion: esperar y reintentar
                        logger.warning(
                            f"BD bloqueada, reintento {retries}/{max_retries} "
                            f"para {func.__name__}"
                        )
                        time.sleep(current_delay)
                        # Backoff exponencial: multiplicar delay para el siguiente intento
                        current_delay *= backoff
                    else:
                        # Error de SQLite que NO es de bloqueo (ej: columna no existe,
                        # tabla no existe, violacion de constraint). No tiene sentido
                        # reintentar porque el problema no se resolvera solo.
                        raise

                except Exception as e:
                    # Cualquier otra excepcion (no SQLite): loguear y relanzar sin reintentar
                    logger.error(f"Error en {func.__name__}: {str(e)}")
                    raise

            # Este return None solo alcanzable en teoria si el while termina sin return/raise
            return None
        return wrapper
    return decorator


def sanitize_error_message(error):
    """
    Convierte un error tecnico de base de datos en un mensaje amigable para el usuario.

    SQLite lanza errores con mensajes tecnicos como:
        "UNIQUE constraint failed: Contactos.Email"
        "FOREIGN KEY constraint failed"
        "no such table: Usuarios"

    Estos mensajes exponen detalles de la implementacion interna (nombres de tablas,
    columnas, etc.) que no deben mostrarse al usuario final. Esta funcion los
    reemplaza por mensajes claros y en espanol.

    Comportamiento:
        - Busca palabras clave del error de SQLite en el mensaje.
        - Si encuentra una coincidencia, retorna el mensaje amigable correspondiente.
        - Si no reconoce el error, retorna un mensaje generico.
        - En todos los casos, el error original se loguea por separado (en el servicio
          que llama a esta funcion) para facilitar la depuracion.

    Parametros:
        error: La excepcion capturada. Se convierte a str para buscar las palabras clave.

    Returns:
        str: Mensaje legible en espanol para mostrar en la interfaz de usuario.
    """
    error_str = str(error)

    # Tabla de mapeo: error tecnico de SQLite -> mensaje amigable en espanol
    # Las claves son subcadenas que pueden aparecer en el mensaje de error de SQLite.
    error_mappings = {
        # Se intento insertar un valor que ya existe en una columna con UNIQUE constraint
        'UNIQUE constraint failed': 'Este registro ya existe en el sistema',
        # Se intento insertar/actualizar un ID que no existe en la tabla referenciada
        'FOREIGN KEY constraint failed': 'No se puede completar la operacion debido a dependencias',
        # Se intento insertar NULL en una columna NOT NULL
        'NOT NULL constraint failed': 'Faltan campos requeridos',
        # Otro proceso tiene la BD bloqueada (puede pasar con WAL en condiciones extremas)
        'database is locked': 'La base de datos esta ocupada, intenta nuevamente',
        # La tabla no existe (error de configuracion, no deberia pasar en produccion)
        'no such table': 'Error de configuracion de base de datos',
        # La columna no existe (error de configuracion, no deberia pasar en produccion)
        'no such column': 'Error de configuracion de base de datos',
    }

    # Buscar si alguna clave del mapeo aparece en el mensaje de error
    # Se compara en minusculas para ser insensible a mayusculas
    for db_error, user_message in error_mappings.items():
        if db_error.lower() in error_str.lower():
            return user_message

    # Si no se reconocio el error, retornar un mensaje generico sin detalles tecnicos
    return 'Ocurrio un error al procesar la solicitud'


def validate_foreign_key(conn, table, column, value):
    """
    Valida que un valor de llave foranea existe en su tabla de referencia.

    Aunque los PRAGMAs de SQLite ya validan FK automaticamente al hacer INSERT/UPDATE,
    esta funcion permite verificar ANTES de intentar la operacion. Esto es util para
    dar mensajes de error mas descriptivos al usuario en lugar del generico
    "FOREIGN KEY constraint failed".

    Si 'value' es None, se considera valido (el campo es opcional/nullable).
    Si 'column' no esta en el mapeo, se asume valido (no se puede verificar).

    Parametros:
        conn   : Conexion SQLite activa (de get_connection()).
        table  : Nombre de la tabla que tendra la FK (actualmente no se usa, pero
                 se incluye para claridad semantica).
        column : Nombre de la columna FK (ej. "ContactoID", "EmpresaID").
        value  : Valor del ID a verificar. Si es None, retorna True sin consultar.

    Returns:
        bool: True si el valor existe en la tabla referenciada (o si no aplica),
              False si el ID no existe en la tabla correspondiente.
    """
    # None significa que el campo no fue proporcionado; es valido para campos opcionales
    if value is None:
        return True

    # Mapeo de nombres de columnas FK a su tabla referenciada.
    # Esto permite saber que tabla consultar para validar cada tipo de ID.
    fk_mappings = {
        'ContactoID': 'Contactos',       # FK hacia la tabla de contactos
        'EmpresaID': 'Empresas',         # FK hacia la tabla de empresas
        'UsuarioID': 'Usuarios',         # FK hacia la tabla de usuarios del sistema
        'RolID': 'Roles',               # FK hacia la tabla de roles de usuario
        'IndustriaID': 'Industrias',     # FK hacia el catalogo de industrias
        'TamanoID': 'TamanosEmpresa',   # FK hacia el catalogo de tamanos de empresa
        'OrigenID': 'OrigenesContacto', # FK hacia el catalogo de origenes de leads
        'PaisID': 'Paises',             # FK hacia el catalogo de paises
        'EstadoID': 'Estados',          # FK hacia el catalogo de estados/provincias
        'CiudadID': 'Ciudades',         # FK hacia el catalogo de ciudades
    }

    # Buscar la tabla de referencia para esta columna
    ref_table = fk_mappings.get(column)
    if not ref_table:
        # No conocemos esta columna FK: asumir que es valida (no podemos verificar)
        return True

    # Consultar si existe un registro con ese ID en la tabla referenciada
    # SELECT 1 es mas eficiente que SELECT * porque no carga datos de la fila
    # LIMIT 1 detiene la busqueda en cuanto encuentra el primer resultado
    cursor = conn.execute(
        f"SELECT 1 FROM {ref_table} WHERE {column} = ? LIMIT 1",
        (value,)
    )
    result = cursor.fetchone()

    # Si fetchone() retorna None, no existe ningun registro con ese ID
    return result is not None
