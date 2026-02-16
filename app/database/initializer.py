# Se encarga de crear las tablas y meter datos iniciales la primera vez

import os
from app.config.settings import DB_PATH, SCHEMA_PATH
from app.database.connection import get_connection


def initialize_database():
    # si la base de datos ya existe, no inicializar
    if os.path.exists(DB_PATH):
        return

    conn = get_connection()

    # leer y ejecutar el .sql con la estructura de tablas
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()

    # aplicar indices de rendimiento
    indexes_path = os.path.join(os.path.dirname(SCHEMA_PATH), 'add_indexes.sql')
    if os.path.exists(indexes_path):
        with open(indexes_path, "r", encoding="utf-8") as f:
            indexes_sql = f.read()
        conn.executescript(indexes_sql)
        conn.commit()


def has_users():
    # verifica si existe al menos un usuario en la base de datos
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM Usuarios")
    return cursor.fetchone()[0] > 0
