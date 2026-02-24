# Repositorio de segmentos - queries contra la tabla Segmentos

from app.database.connection import get_connection
from app.models.Segmento import Segmento


class SegmentoRepository:

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        conn = get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS SegmentoContactos (
                SegmentoContactoID  INTEGER PRIMARY KEY AUTOINCREMENT,
                SegmentoID          INTEGER NOT NULL,
                ContactoID          INTEGER NOT NULL,
                FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
                AsignadoPor         INTEGER,
                FOREIGN KEY (SegmentoID) REFERENCES Segmentos(SegmentoID) ON DELETE CASCADE,
                FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID) ON DELETE CASCADE,
                UNIQUE (SegmentoID, ContactoID)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS SegmentoEmpresas (
                SegmentoEmpresaID   INTEGER PRIMARY KEY AUTOINCREMENT,
                SegmentoID          INTEGER NOT NULL,
                EmpresaID           INTEGER NOT NULL,
                FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
                AsignadoPor         INTEGER,
                FOREIGN KEY (SegmentoID) REFERENCES Segmentos(SegmentoID) ON DELETE CASCADE,
                FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID) ON DELETE CASCADE,
                UNIQUE (SegmentoID, EmpresaID)
            )
            """
        )
        conn.commit()

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT s.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM Segmentos s
            LEFT JOIN Usuarios u ON s.CreadoPor = u.UsuarioID
            ORDER BY s.Nombre
            """
        )
        return [self._row_to_segmento(row) for row in cursor.fetchall()]

    def find_by_id(self, segmento_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT s.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM Segmentos s
            LEFT JOIN Usuarios u ON s.CreadoPor = u.UsuarioID
            WHERE s.SegmentoID = ?
            """,
            (segmento_id,),
        )
        row = cursor.fetchone()
        return self._row_to_segmento(row) if row else None

    def create(self, segmento):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Segmentos
                (Nombre, Descripcion, TipoEntidad, CreadoPor)
            VALUES (?, ?, ?, ?)
            """,
            (
                segmento.nombre,
                segmento.descripcion,
                segmento.tipo_entidad,
                segmento.creado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, segmento):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Segmentos SET
                Nombre = ?, Descripcion = ?, TipoEntidad = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE SegmentoID = ?
            """,
            (
                segmento.nombre,
                segmento.descripcion,
                segmento.tipo_entidad,
                segmento.segmento_id,
            ),
        )
        conn.commit()

    def delete(self, segmento_id):
        conn = get_connection()
        conn.execute("DELETE FROM Segmentos WHERE SegmentoID = ?", (segmento_id,))
        conn.commit()

    def update_cantidad_registros(self, segmento_id, cantidad):
        conn = get_connection()
        conn.execute(
            "UPDATE Segmentos SET CantidadRegistros = ? WHERE SegmentoID = ?",
            (cantidad, segmento_id),
        )
        conn.commit()

    def get_miembros(self, segmento):
        """Retorna la lista de miembros asignados manualmente al segmento."""
        conn = get_connection()

        if segmento.tipo_entidad == "Contactos":
            cursor = conn.execute(
                """
                SELECT c.ContactoID AS ID,
                       (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreCompleto,
                       c.Email,
                       c.Puesto,
                       c.Departamento,
                       e.RazonSocial AS Empresa,
                       ci.Nombre AS Ciudad
                FROM SegmentoContactos sc
                INNER JOIN Contactos c ON sc.ContactoID = c.ContactoID
                LEFT JOIN Empresas e ON c.EmpresaID = e.EmpresaID
                LEFT JOIN Ciudades ci ON c.CiudadID = ci.CiudadID
                WHERE sc.SegmentoID = ?
                ORDER BY c.Nombre, c.ApellidoPaterno
                """,
                (segmento.segmento_id,),
            )
        else:  # Empresas
            cursor = conn.execute(
                """
                SELECT e.EmpresaID AS ID,
                       e.RazonSocial AS NombreCompleto,
                       e.Email,
                       e.Telefono,
                       i.Nombre AS Industria,
                       te.Nombre AS Tamano,
                       ci.Nombre AS Ciudad
                FROM SegmentoEmpresas se
                INNER JOIN Empresas e ON se.EmpresaID = e.EmpresaID
                LEFT JOIN Industrias i ON e.IndustriaID = i.IndustriaID
                LEFT JOIN TamanosEmpresa te ON e.TamanoID = te.TamanoID
                LEFT JOIN Ciudades ci ON e.CiudadID = ci.CiudadID
                WHERE se.SegmentoID = ?
                ORDER BY e.RazonSocial
                """,
                (segmento.segmento_id,),
            )

        return [dict(row) for row in cursor.fetchall()]

    def add_miembro(self, segmento_id, entidad_id, tipo_entidad, usuario_id):
        conn = get_connection()
        if tipo_entidad == "Contactos":
            conn.execute(
                """
                INSERT OR IGNORE INTO SegmentoContactos (SegmentoID, ContactoID, AsignadoPor)
                VALUES (?, ?, ?)
                """,
                (segmento_id, entidad_id, usuario_id),
            )
        else:
            conn.execute(
                """
                INSERT OR IGNORE INTO SegmentoEmpresas (SegmentoID, EmpresaID, AsignadoPor)
                VALUES (?, ?, ?)
                """,
                (segmento_id, entidad_id, usuario_id),
            )
        conn.commit()

    def remove_miembro(self, segmento_id, entidad_id, tipo_entidad):
        conn = get_connection()
        if tipo_entidad == "Contactos":
            conn.execute(
                "DELETE FROM SegmentoContactos WHERE SegmentoID = ? AND ContactoID = ?",
                (segmento_id, entidad_id),
            )
        else:
            conn.execute(
                "DELETE FROM SegmentoEmpresas WHERE SegmentoID = ? AND EmpresaID = ?",
                (segmento_id, entidad_id),
            )
        conn.commit()

    def find_all_by_tipo(self, tipo_entidad):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT s.*,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreCreador
            FROM Segmentos s
            LEFT JOIN Usuarios u ON s.CreadoPor = u.UsuarioID
            WHERE s.TipoEntidad = ?
            ORDER BY s.Nombre
            """,
            (tipo_entidad,),
        )
        return [self._row_to_segmento(row) for row in cursor.fetchall()]

    def get_segmentos_de_contacto(self, contacto_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT s.SegmentoID, s.Nombre, s.Descripcion, s.TipoEntidad
            FROM SegmentoContactos sc
            INNER JOIN Segmentos s ON sc.SegmentoID = s.SegmentoID
            WHERE sc.ContactoID = ?
            ORDER BY s.Nombre
            """,
            (contacto_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_segmentos_de_empresa(self, empresa_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT s.SegmentoID, s.Nombre, s.Descripcion, s.TipoEntidad
            FROM SegmentoEmpresas se
            INNER JOIN Segmentos s ON se.SegmentoID = s.SegmentoID
            WHERE se.EmpresaID = ?
            ORDER BY s.Nombre
            """,
            (empresa_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_segmento(row):
        def safe(key):
            try:
                return row[key]
            except (KeyError, IndexError):
                return None

        return Segmento(
            segmento_id=row["SegmentoID"],
            nombre=row["Nombre"],
            descripcion=row["Descripcion"],
            tipo_entidad=row["TipoEntidad"],
            cantidad_registros=row["CantidadRegistros"],
            creado_por=row["CreadoPor"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            nombre_creador=safe("NombreCreador"),
        )
