# utilidades para reintentos de operaciones de base de datos

import time
import sqlite3
from functools import wraps
from app.utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


def retry_on_db_error(max_retries=3, delay=0.1, backoff=2):
    # decorador para reintentar operaciones de BD en caso de error
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {str(e)}")
                        raise

                    # errores que vale la pena reintentar
                    error_msg = str(e).lower()
                    if 'locked' in error_msg or 'busy' in error_msg:
                        logger.warning(f"DB locked, retry {retries}/{max_retries} for {func.__name__}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # otro tipo de error, no reintentar
                        raise
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    raise

            return None
        return wrapper
    return decorator


def sanitize_error_message(error):
    # sanitiza mensajes de error para no exponer informacion sensible
    error_str = str(error)

    # errores comunes de BD con mensajes amigables
    error_mappings = {
        'UNIQUE constraint failed': 'Este registro ya existe en el sistema',
        'FOREIGN KEY constraint failed': 'No se puede completar la operacion debido a dependencias',
        'NOT NULL constraint failed': 'Faltan campos requeridos',
        'database is locked': 'La base de datos esta ocupada, intenta nuevamente',
        'no such table': 'Error de configuracion de base de datos',
        'no such column': 'Error de configuracion de base de datos',
    }

    for db_error, user_message in error_mappings.items():
        if db_error.lower() in error_str.lower():
            return user_message

    # mensaje generico si no se reconoce el error
    return 'Ocurrio un error al procesar la solicitud'


def validate_foreign_key(conn, table, column, value):
    # valida que una foreign key existe antes de insertarla
    if value is None:
        return True

    # mapeo de columnas a tablas referenciadas
    fk_mappings = {
        'ContactoID': 'Contactos',
        'EmpresaID': 'Empresas',
        'UsuarioID': 'Usuarios',
        'RolID': 'Roles',
        'IndustriaID': 'Industrias',
        'TamanoID': 'TamanosEmpresa',
        'OrigenID': 'OrigenesContacto',
        'PaisID': 'Paises',
        'EstadoID': 'Estados',
        'CiudadID': 'Ciudades',
    }

    ref_table = fk_mappings.get(column)
    if not ref_table:
        return True  # no se encontro mapeo, asumir valido

    # verificar que existe el registro
    cursor = conn.execute(f"SELECT 1 FROM {ref_table} WHERE {column} = ? LIMIT 1", (value,))
    result = cursor.fetchone()

    return result is not None
