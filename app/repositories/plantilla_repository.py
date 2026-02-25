# Repositorio de plantillas de correo - queries contra PlantillasCorreo

from app.database.connection import get_connection
from app.models.Plantilla import Plantilla


class PlantillaRepository:

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT p.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM PlantillasCorreo p
            LEFT JOIN Usuarios u ON p.CreadoPor = u.UsuarioID
            ORDER BY p.Nombre
            """
        )
        return [self._row_to_plantilla(row) for row in cursor.fetchall()]

    def find_all_activas(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT p.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM PlantillasCorreo p
            LEFT JOIN Usuarios u ON p.CreadoPor = u.UsuarioID
            WHERE p.Activa = 1
            ORDER BY p.Nombre
            """
        )
        return [self._row_to_plantilla(row) for row in cursor.fetchall()]

    def find_by_id(self, plantilla_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT p.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM PlantillasCorreo p
            LEFT JOIN Usuarios u ON p.CreadoPor = u.UsuarioID
            WHERE p.PlantillaID = ?
            """,
            (plantilla_id,),
        )
        row = cursor.fetchone()
        return self._row_to_plantilla(row) if row else None

    def create(self, plantilla):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO PlantillasCorreo
                (Nombre, Asunto, ContenidoHTML, ContenidoTexto, Categoria, Activa, CreadoPor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plantilla.nombre,
                plantilla.asunto,
                plantilla.contenido_html,
                plantilla.contenido_texto,
                plantilla.categoria,
                plantilla.activa,
                plantilla.creado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, plantilla):
        conn = get_connection()
        conn.execute(
            """
            UPDATE PlantillasCorreo SET
                Nombre = ?, Asunto = ?, ContenidoHTML = ?, ContenidoTexto = ?,
                Categoria = ?, Activa = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE PlantillaID = ?
            """,
            (
                plantilla.nombre,
                plantilla.asunto,
                plantilla.contenido_html,
                plantilla.contenido_texto,
                plantilla.categoria,
                plantilla.activa,
                plantilla.plantilla_id,
            ),
        )
        conn.commit()

    def delete(self, plantilla_id):
        conn = get_connection()
        conn.execute("DELETE FROM PlantillasCorreo WHERE PlantillaID = ?", (plantilla_id,))
        conn.commit()

    @staticmethod
    def _row_to_plantilla(row):
        def safe(key):
            try:
                return row[key]
            except (KeyError, IndexError):
                return None

        return Plantilla(
            plantilla_id=row["PlantillaID"],
            nombre=row["Nombre"],
            asunto=row["Asunto"],
            contenido_html=row["ContenidoHTML"],
            contenido_texto=row["ContenidoTexto"],
            categoria=row["Categoria"],
            activa=row["Activa"],
            creado_por=row["CreadoPor"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            nombre_creador=safe("NombreCreador"),
        )
