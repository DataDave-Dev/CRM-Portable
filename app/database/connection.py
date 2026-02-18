# Manejo de la conexion a SQLite
# Usamos thread-local storage para que cada hilo tenga su propia conexion.
# SQLite no permite compartir un objeto de conexion entre hilos distintos.

import sqlite3
import threading
from app.config.settings import DB_PATH

_local = threading.local()


def get_connection():
    if not hasattr(_local, "connection") or _local.connection is None:
        _local.connection = sqlite3.connect(DB_PATH)
        _local.connection.execute("PRAGMA foreign_keys = ON")   # para que respete las FK
        _local.connection.execute("PRAGMA journal_mode = WAL")  # mejor rendimiento en escrituras
        _local.connection.row_factory = sqlite3.Row  # para acceder a columnas por nombre
    return _local.connection


def close_connection():
    if hasattr(_local, "connection") and _local.connection:
        _local.connection.close()
        _local.connection = None
