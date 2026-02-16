# Repositorio de notas de contacto - queries contra la tabla NotasContacto

from app.database.connection import get_connection
from app.models.NotaContacto import NotaContacto


class NotaContactoRepository:

    def find_by_contacto(self, contacto_id):
        # obtiene todas las notas de un contacto especifico
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT nc.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM NotasContacto nc
            LEFT JOIN Contactos c ON nc.ContactoID = c.ContactoID
            LEFT JOIN Usuarios u ON nc.CreadoPor = u.UsuarioID
            WHERE nc.ContactoID = ?
            ORDER BY nc.FechaCreacion DESC
            """,
            (contacto_id,),
        )
        rows = cursor.fetchall()
        return [self._row_to_nota(row) for row in rows]

    def find_by_id(self, nota_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT nc.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM NotasContacto nc
            LEFT JOIN Contactos c ON nc.ContactoID = c.ContactoID
            LEFT JOIN Usuarios u ON nc.CreadoPor = u.UsuarioID
            WHERE nc.NotaID = ?
            """,
            (nota_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_nota(row)

    def create(self, nota):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO NotasContacto (
                ContactoID, Titulo, Contenido, EsPrivada, CreadoPor
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                nota.contacto_id,
                nota.titulo,
                nota.contenido,
                nota.es_privada,
                nota.creado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, nota):
        conn = get_connection()
        conn.execute(
            """
            UPDATE NotasContacto
            SET Titulo = ?, Contenido = ?, EsPrivada = ?
            WHERE NotaID = ?
            """,
            (
                nota.titulo,
                nota.contenido,
                nota.es_privada,
                nota.nota_id,
            ),
        )
        conn.commit()

    def delete(self, nota_id):
        conn = get_connection()
        conn.execute("DELETE FROM NotasContacto WHERE NotaID = ?", (nota_id,))
        conn.commit()

    def _row_to_nota(self, row):
        nombre_contacto = None
        nombre_creador = None
        try:
            nombre_contacto = row["NombreContacto"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_creador = row["NombreCreador"]
        except (KeyError, IndexError):
            pass

        return NotaContacto(
            nota_id=row["NotaID"],
            contacto_id=row["ContactoID"],
            titulo=row["Titulo"],
            contenido=row["Contenido"],
            es_privada=row["EsPrivada"],
            fecha_creacion=row["FechaCreacion"],
            creado_por=row["CreadoPor"],
            nombre_contacto=nombre_contacto,
            nombre_creador=nombre_creador,
        )
