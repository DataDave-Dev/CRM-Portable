# Se encarga de crear las tablas y meter datos iniciales la primera vez

import bcrypt
from app.config.settings import SCHEMA_PATH
from app.database.connection import get_connection


def initialize_database():
    conn = get_connection()
    # leer y ejecutar el .sql con la estructura de tablas
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    _seed_default_data(conn)


def _seed_default_data(conn):
    # solo insertar datos si la tabla Roles esta vacia (primera ejecucion)
    cursor = conn.execute("SELECT COUNT(*) FROM Roles")
    if cursor.fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO Roles (NombreRol, Descripcion) VALUES (?, ?)",
            ("Administrador", "Acceso total al sistema"),
        )

        # usuario admin por default para poder entrar al sistema
        hashed = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute(
            "INSERT INTO Usuarios (Nombre, ApellidoPaterno, Email, ContrasenaHash, RolID) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Admin", "Sistema", "admin@crm.com", hashed, 1),
        )
        conn.commit()
