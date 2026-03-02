# Repositorio de notificaciones - queries contra la tabla Notificaciones

from app.database.connection import get_connection
from app.models.Notificacion import Notificacion


class NotificacionRepository:

    def find_by_usuario(self, usuario_id, limit=100):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM Notificaciones
            WHERE UsuarioID = ?
            ORDER BY FechaCreacion DESC
            LIMIT ?
            """,
            (usuario_id, limit),
        )
        return [self._row_to_notificacion(row) for row in cursor.fetchall()]

    def find_unread_by_usuario(self, usuario_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM Notificaciones
            WHERE UsuarioID = ? AND EsLeida = 0
            ORDER BY FechaCreacion DESC
            """,
            (usuario_id,),
        )
        return [self._row_to_notificacion(row) for row in cursor.fetchall()]

    def count_unread(self, usuario_id):
        conn = get_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) FROM Notificaciones WHERE UsuarioID = ? AND EsLeida = 0",
            (usuario_id,),
        )
        return cursor.fetchone()[0]

    def mark_as_read(self, notificacion_id):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Notificaciones
            SET EsLeida = 1, FechaLectura = datetime('now', 'localtime')
            WHERE NotificacionID = ?
            """,
            (notificacion_id,),
        )
        conn.commit()

    def mark_all_read(self, usuario_id):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Notificaciones
            SET EsLeida = 1, FechaLectura = datetime('now', 'localtime')
            WHERE UsuarioID = ? AND EsLeida = 0
            """,
            (usuario_id,),
        )
        conn.commit()

    def create(self, tipo, titulo, mensaje, usuario_id, entidad_tipo=None, entidad_id=None):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Notificaciones (UsuarioID, Tipo, Titulo, Mensaje, EntidadTipo, EntidadID)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (usuario_id, tipo, titulo, mensaje, entidad_tipo, entidad_id),
        )
        conn.commit()
        return cursor.lastrowid

    def _row_to_notificacion(self, row):
        return Notificacion(
            notificacion_id=row["NotificacionID"],
            usuario_id=row["UsuarioID"],
            tipo=row["Tipo"],
            titulo=row["Titulo"],
            mensaje=row["Mensaje"],
            entidad_tipo=row["EntidadTipo"],
            entidad_id=row["EntidadID"],
            url=row["URL"],
            es_leida=row["EsLeida"],
            fecha_creacion=row["FechaCreacion"],
            fecha_lectura=row["FechaLectura"],
        )
