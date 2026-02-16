# Repositorio de notas de empresa - queries contra la tabla NotasEmpresa

from app.database.connection import get_connection
from app.models.NotaEmpresa import NotaEmpresa


class NotaEmpresaRepository:

    def find_by_empresa(self, empresa_id):
        # obtiene todas las notas de una empresa especifica
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT ne.*,
                   e.RazonSocial AS NombreEmpresa,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM NotasEmpresa ne
            LEFT JOIN Empresas e ON ne.EmpresaID = e.EmpresaID
            LEFT JOIN Usuarios u ON ne.CreadoPor = u.UsuarioID
            WHERE ne.EmpresaID = ?
            ORDER BY ne.FechaCreacion DESC
            """,
            (empresa_id,),
        )
        rows = cursor.fetchall()
        return [self._row_to_nota(row) for row in rows]

    def find_by_id(self, nota_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT ne.*,
                   e.RazonSocial AS NombreEmpresa,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM NotasEmpresa ne
            LEFT JOIN Empresas e ON ne.EmpresaID = e.EmpresaID
            LEFT JOIN Usuarios u ON ne.CreadoPor = u.UsuarioID
            WHERE ne.NotaID = ?
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
            INSERT INTO NotasEmpresa (
                EmpresaID, Titulo, Contenido, EsPrivada, CreadoPor
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                nota.empresa_id,
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
            UPDATE NotasEmpresa
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
        conn.execute("DELETE FROM NotasEmpresa WHERE NotaID = ?", (nota_id,))
        conn.commit()

    def _row_to_nota(self, row):
        nombre_empresa = None
        nombre_creador = None
        try:
            nombre_empresa = row["NombreEmpresa"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_creador = row["NombreCreador"]
        except (KeyError, IndexError):
            pass

        return NotaEmpresa(
            nota_id=row["NotaID"],
            empresa_id=row["EmpresaID"],
            titulo=row["Titulo"],
            contenido=row["Contenido"],
            es_privada=row["EsPrivada"],
            fecha_creacion=row["FechaCreacion"],
            creado_por=row["CreadoPor"],
            nombre_empresa=nombre_empresa,
            nombre_creador=nombre_creador,
        )
