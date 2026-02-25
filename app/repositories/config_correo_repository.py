# Repositorio de configuracion de correo - queries contra ConfiguracionCorreo

from app.database.connection import get_connection
from app.models.ConfiguracionCorreo import ConfiguracionCorreo


class ConfigCorreoRepository:

    def _ensure_table(self):
        conn = get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ConfiguracionCorreo (
                ConfigID            INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre              TEXT NOT NULL,
                Proveedor           TEXT NOT NULL DEFAULT 'SMTP',
                Host                TEXT,
                Puerto              INTEGER DEFAULT 587,
                UsarTLS             INTEGER DEFAULT 1,
                UsarSSL             INTEGER DEFAULT 0,
                EmailRemitente      TEXT NOT NULL,
                NombreRemitente     TEXT,
                Usuario             TEXT,
                Contrasena          TEXT,
                ApiKey              TEXT,
                Activa              INTEGER DEFAULT 0,
                Notas               TEXT,
                FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
                FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        conn.commit()

    def __init__(self):
        self._ensure_table()

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM ConfiguracionCorreo ORDER BY Activa DESC, Nombre"
        )
        return [self._row_to_config(row) for row in cursor.fetchall()]

    def find_by_id(self, config_id):
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM ConfiguracionCorreo WHERE ConfigID = ?",
            (config_id,),
        )
        row = cursor.fetchone()
        return self._row_to_config(row) if row else None

    def find_activa(self):
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM ConfiguracionCorreo WHERE Activa = 1 LIMIT 1"
        )
        row = cursor.fetchone()
        return self._row_to_config(row) if row else None

    def create(self, config):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO ConfiguracionCorreo
                (Nombre, Proveedor, Host, Puerto, UsarTLS, UsarSSL,
                 EmailRemitente, NombreRemitente, Usuario, Contrasena,
                 ApiKey, Activa, Notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                config.nombre,
                config.proveedor,
                config.host,
                config.puerto,
                config.usar_tls,
                config.usar_ssl,
                config.email_remitente,
                config.nombre_remitente,
                config.usuario,
                config.contrasena,
                config.api_key,
                config.activa,
                config.notas,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, config):
        conn = get_connection()
        conn.execute(
            """
            UPDATE ConfiguracionCorreo SET
                Nombre = ?, Proveedor = ?, Host = ?, Puerto = ?,
                UsarTLS = ?, UsarSSL = ?, EmailRemitente = ?,
                NombreRemitente = ?, Usuario = ?, Contrasena = ?,
                ApiKey = ?, Activa = ?, Notas = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE ConfigID = ?
            """,
            (
                config.nombre,
                config.proveedor,
                config.host,
                config.puerto,
                config.usar_tls,
                config.usar_ssl,
                config.email_remitente,
                config.nombre_remitente,
                config.usuario,
                config.contrasena,
                config.api_key,
                config.activa,
                config.notas,
                config.config_id,
            ),
        )
        conn.commit()

    def activar(self, config_id):
        conn = get_connection()
        conn.execute("UPDATE ConfiguracionCorreo SET Activa = 0")
        conn.execute(
            "UPDATE ConfiguracionCorreo SET Activa = 1, "
            "FechaModificacion = datetime('now', 'localtime') WHERE ConfigID = ?",
            (config_id,),
        )
        conn.commit()

    def delete(self, config_id):
        conn = get_connection()
        conn.execute("DELETE FROM ConfiguracionCorreo WHERE ConfigID = ?", (config_id,))
        conn.commit()

    @staticmethod
    def _row_to_config(row):
        return ConfiguracionCorreo(
            config_id=row["ConfigID"],
            nombre=row["Nombre"],
            proveedor=row["Proveedor"],
            host=row["Host"],
            puerto=row["Puerto"],
            usar_tls=row["UsarTLS"],
            usar_ssl=row["UsarSSL"],
            email_remitente=row["EmailRemitente"],
            nombre_remitente=row["NombreRemitente"],
            usuario=row["Usuario"],
            contrasena=row["Contrasena"],
            api_key=row["ApiKey"],
            activa=row["Activa"],
            notas=row["Notas"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
        )
