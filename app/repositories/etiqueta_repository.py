# Repositorio de etiquetas - queries contra Etiquetas, ContactoEtiquetas, EmpresaEtiquetas

from app.database.connection import get_connection
from app.models.Etiqueta import Etiqueta


class EtiquetaRepository:

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.*,
                   COUNT(DISTINCT ce.ContactoID) AS NumContactos,
                   COUNT(DISTINCT ee.EmpresaID)  AS NumEmpresas
            FROM Etiquetas e
            LEFT JOIN ContactoEtiquetas ce ON e.EtiquetaID = ce.EtiquetaID
            LEFT JOIN EmpresaEtiquetas  ee ON e.EtiquetaID = ee.EtiquetaID
            GROUP BY e.EtiquetaID
            ORDER BY e.Nombre
            """
        )
        return [self._row_to_etiqueta(row) for row in cursor.fetchall()]

    def find_by_id(self, etiqueta_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.*,
                   COUNT(DISTINCT ce.ContactoID) AS NumContactos,
                   COUNT(DISTINCT ee.EmpresaID)  AS NumEmpresas
            FROM Etiquetas e
            LEFT JOIN ContactoEtiquetas ce ON e.EtiquetaID = ce.EtiquetaID
            LEFT JOIN EmpresaEtiquetas  ee ON e.EtiquetaID = ee.EtiquetaID
            WHERE e.EtiquetaID = ?
            GROUP BY e.EtiquetaID
            """,
            (etiqueta_id,),
        )
        row = cursor.fetchone()
        return self._row_to_etiqueta(row) if row else None

    def create(self, etiqueta):
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO Etiquetas (Nombre, Color, Categoria) VALUES (?, ?, ?)",
            (etiqueta.nombre, etiqueta.color, etiqueta.categoria),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, etiqueta):
        conn = get_connection()
        conn.execute(
            "UPDATE Etiquetas SET Nombre = ?, Color = ?, Categoria = ? WHERE EtiquetaID = ?",
            (etiqueta.nombre, etiqueta.color, etiqueta.categoria, etiqueta.etiqueta_id),
        )
        conn.commit()

    def delete(self, etiqueta_id):
        conn = get_connection()
        conn.execute("DELETE FROM ContactoEtiquetas WHERE EtiquetaID = ?", (etiqueta_id,))
        conn.execute("DELETE FROM EmpresaEtiquetas  WHERE EtiquetaID = ?", (etiqueta_id,))
        conn.execute("DELETE FROM Etiquetas WHERE EtiquetaID = ?", (etiqueta_id,))
        conn.commit()

    # ---- Contactos asignados ----

    def get_contactos_asignados(self, etiqueta_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT c.ContactoID,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreCompleto,
                   e.RazonSocial AS Empresa
            FROM ContactoEtiquetas ce
            JOIN Contactos c ON ce.ContactoID = c.ContactoID
            LEFT JOIN Empresas e ON c.EmpresaID = e.EmpresaID
            WHERE ce.EtiquetaID = ?
            ORDER BY NombreCompleto
            """,
            (etiqueta_id,),
        )
        return cursor.fetchall()

    def asignar_contacto(self, etiqueta_id, contacto_id, usuario_id=None):
        conn = get_connection()
        conn.execute(
            """
            INSERT OR IGNORE INTO ContactoEtiquetas
                (ContactoID, EtiquetaID, AsignadoPor)
            VALUES (?, ?, ?)
            """,
            (contacto_id, etiqueta_id, usuario_id),
        )
        conn.commit()

    def quitar_contacto(self, etiqueta_id, contacto_id):
        conn = get_connection()
        conn.execute(
            "DELETE FROM ContactoEtiquetas WHERE EtiquetaID = ? AND ContactoID = ?",
            (etiqueta_id, contacto_id),
        )
        conn.commit()

    # ---- Empresas asignadas ----

    def get_empresas_asignadas(self, etiqueta_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.EmpresaID, e.RazonSocial
            FROM EmpresaEtiquetas ee
            JOIN Empresas e ON ee.EmpresaID = e.EmpresaID
            WHERE ee.EtiquetaID = ?
            ORDER BY e.RazonSocial
            """,
            (etiqueta_id,),
        )
        return cursor.fetchall()

    def asignar_empresa(self, etiqueta_id, empresa_id, usuario_id=None):
        conn = get_connection()
        conn.execute(
            """
            INSERT OR IGNORE INTO EmpresaEtiquetas
                (EmpresaID, EtiquetaID, AsignadoPor)
            VALUES (?, ?, ?)
            """,
            (empresa_id, etiqueta_id, usuario_id),
        )
        conn.commit()

    def quitar_empresa(self, etiqueta_id, empresa_id):
        conn = get_connection()
        conn.execute(
            "DELETE FROM EmpresaEtiquetas WHERE EtiquetaID = ? AND EmpresaID = ?",
            (etiqueta_id, empresa_id),
        )
        conn.commit()

    # ---- Etiquetas de un contacto/empresa especifico ----

    def get_etiquetas_de_contacto(self, contacto_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.EtiquetaID, e.Nombre, e.Color
            FROM ContactoEtiquetas ce
            JOIN Etiquetas e ON ce.EtiquetaID = e.EtiquetaID
            WHERE ce.ContactoID = ?
            ORDER BY e.Nombre
            """,
            (contacto_id,),
        )
        return cursor.fetchall()

    def get_etiquetas_de_empresa(self, empresa_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.EtiquetaID, e.Nombre, e.Color
            FROM EmpresaEtiquetas ee
            JOIN Etiquetas e ON ee.EtiquetaID = e.EtiquetaID
            WHERE ee.EmpresaID = ?
            ORDER BY e.Nombre
            """,
            (empresa_id,),
        )
        return cursor.fetchall()

    @staticmethod
    def _row_to_etiqueta(row):
        return Etiqueta(
            etiqueta_id=row["EtiquetaID"],
            nombre=row["Nombre"],
            color=row["Color"],
            categoria=row["Categoria"],
            fecha_creacion=row["FechaCreacion"],
            num_contactos=row["NumContactos"] if "NumContactos" in row.keys() else 0,
            num_empresas=row["NumEmpresas"] if "NumEmpresas" in row.keys() else 0,
        )
