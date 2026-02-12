# Manejo de la conexion a SQLite
# Usamos un singleton para no abrir multiples conexiones

import sqlite3
from app.config.settings import DB_PATH

_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH)
        _connection.execute("PRAGMA foreign_keys = ON")   # para que respete las FK
        _connection.execute("PRAGMA journal_mode = WAL")   # mejor rendimiento en escrituras
        _connection.row_factory = sqlite3.Row  # para acceder a columnas por nombre
    return _connection

def close_connection():
    global _connection
    if _connection:
        _connection.close()
        _connection = None
