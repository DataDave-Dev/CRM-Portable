"""
Modulo de conexion a la base de datos SQLite.

Este modulo centraliza toda la logica de apertura y cierre de conexiones
a la base de datos. El diseno sigue el patron "thread-local storage" para
garantizar que cada hilo del sistema operativo tenga su propia conexion
independiente y segura a SQLite.

Por que se necesita thread-local storage:
    SQLite no permite compartir un mismo objeto de conexion entre varios
    hilos de ejecucion simultanea. Si dos hilos intentaran usar la misma
    conexion al mismo tiempo, podrian corromperse datos o lanzarse
    excepciones impredecibles. La solucion es darle a cada hilo su propia
    conexion privada. Para eso existe threading.local(): cualquier atributo
    que se guarde en ese objeto es invisible para los demas hilos.

    En la practica, PyQt puede usar hilos internos (por ejemplo para senales
    y slots). Al usar threading.local() nos aseguramos de que cada hilo
    creara su conexion la primera vez que la necesite, y la reutilizara en
    llamadas posteriores dentro del mismo hilo.

Uso tipico:
    from app.database.connection import get_connection, close_connection

    conn = get_connection()
    cursor = conn.execute("SELECT * FROM Clientes")
    ...
    close_connection()  # al cerrar la ventana o al terminar el hilo
"""

import sqlite3
import threading

# Importamos la ruta absoluta al archivo .db desde la configuracion central.
# Esto evita duplicar la ruta en varios lugares del proyecto.
from app.config.settings import DB_PATH

# ---------------------------------------------------------------------------
# Almacenamiento thread-local
# ---------------------------------------------------------------------------
# threading.local() crea un objeto especial cuyo estado es unico por hilo.
# Es decir, _local.connection en el hilo principal es una variable distinta
# a _local.connection en cualquier otro hilo, aunque compartan el mismo
# nombre de atributo. Python gestiona esta separacion de forma transparente.
_local = threading.local()


def get_connection():
    """
    Devuelve la conexion SQLite activa para el hilo actual.

    La primera vez que se llama desde un hilo determinado, esta funcion:
      1. Abre una nueva conexion al archivo de base de datos indicado en DB_PATH.
      2. Activa las restricciones de clave foranea (PRAGMA foreign_keys).
      3. Configura el modo de journal WAL para mejor rendimiento (PRAGMA journal_mode).
      4. Configura row_factory para acceder a columnas por nombre en lugar de indice.
      5. Guarda la conexion en el almacenamiento thread-local (_local.connection).

    En llamadas posteriores del mismo hilo, simplemente devuelve la conexion
    que ya fue creada, sin abrir una nueva. Esto evita el costo de reconectarse
    en cada operacion a la base de datos.

    Returns:
        sqlite3.Connection: El objeto de conexion configurado y listo para usar.
    """
    # Comprobamos si este hilo ya tiene una conexion abierta.
    # hasattr verifica si el atributo "connection" existe en el objeto thread-local.
    # La segunda condicion (_local.connection is None) cubre el caso en que
    # close_connection() haya puesto el atributo en None explicitamente.
    if not hasattr(_local, "connection") or _local.connection is None:

        # Primera vez en este hilo: abrimos la conexion al archivo SQLite.
        # Si el archivo no existe, SQLite lo crea automaticamente.
        _local.connection = sqlite3.connect(DB_PATH)

        # --- PRAGMA foreign_keys = ON ---
        # Por defecto, SQLite NO valida las restricciones de clave foranea (FK).
        # Esta instruccion activa la validacion para que:
        #   - No se puedan insertar filas con FK que apunten a IDs inexistentes.
        #   - No se puedan eliminar filas padre que tengan hijos referenciandolas
        #     (a menos que la tabla tenga ON DELETE CASCADE configurado).
        # Debe activarse en cada conexion porque SQLite no lo guarda en el archivo.
        _local.connection.execute("PRAGMA foreign_keys = ON")

        # --- PRAGMA journal_mode = WAL ---
        # WAL = Write-Ahead Logging. Es el modo de registro de cambios de SQLite.
        # En el modo por defecto (DELETE/ROLLBACK), SQLite bloquea el archivo
        # completo durante una escritura, lo que impide lecturas simultaneas.
        # Con WAL:
        #   - Los escritores no bloquean a los lectores.
        #   - Los lectores no bloquean a los escritores.
        #   - El rendimiento en aplicaciones con muchas lecturas mejora notablemente.
        #   - La durabilidad de los datos ante fallos del sistema es mejor.
        # Para una aplicacion de escritorio esto es especialmente util si PyQt
        # lanza operaciones en hilos separados.
        _local.connection.execute("PRAGMA journal_mode = WAL")

        # --- row_factory = sqlite3.Row ---
        # Por defecto, cada fila que devuelve SQLite es una tupla simple.
        # Para acceder a la columna "Nombre" habria que escribir fila[0],
        # lo cual depende del orden de las columnas y es fragil ante cambios.
        # Al asignar sqlite3.Row como row_factory, cada fila se convierte en
        # un objeto que soporta acceso por nombre:
        #   fila["Nombre"]   <- por nombre de columna (legible y robusto)
        #   fila[0]          <- por indice (sigue funcionando)
        # Esto hace el codigo mas claro y resistente a refactorizaciones del esquema.
        _local.connection.row_factory = sqlite3.Row

    # Devolvemos la conexion del hilo actual (nueva o ya existente).
    return _local.connection


def close_connection():
    """
    Cierra la conexion SQLite del hilo actual si esta abierta.

    Debe llamarse cuando el hilo ya no necesita acceso a la base de datos,
    por ejemplo al cerrar la ventana principal o al finalizar un hilo de trabajo.
    Cerrar la conexion libera el descriptor de archivo y los bloqueos internos
    que SQLite mantiene sobre el archivo .db.

    Despues de cerrar, el atributo thread-local se pone en None para que la
    proxima llamada a get_connection() sepa que debe abrir una nueva conexion.

    Si el hilo no tiene ninguna conexion abierta, la funcion no hace nada
    (es seguro llamarla multiples veces o llamarla sin haber llamado get_connection).
    """
    # Verificamos que este hilo tenga una conexion abierta antes de intentar cerrarla.
    # hasattr evita el AttributeError si nunca se llamo get_connection en este hilo.
    if hasattr(_local, "connection") and _local.connection:
        _local.connection.close()    # Cierra el archivo y libera recursos del SO.
        _local.connection = None     # Marca la conexion como inexistente para este hilo.
