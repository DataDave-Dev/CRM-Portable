# Repositorio de segmentos - queries contra la tabla Segmentos

import json as _json
from app.database.connection import get_connection
from app.models.Segmento import Segmento


class SegmentoRepository:

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
                (Nombre, Descripcion, TipoEntidad, CriteriosJSON, EsDinamico, CreadoPor)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                segmento.nombre,
                segmento.descripcion,
                segmento.tipo_entidad,
                segmento.criterios_json,
                segmento.es_dinamico,
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
                CriteriosJSON = ?, EsDinamico = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE SegmentoID = ?
            """,
            (
                segmento.nombre,
                segmento.descripcion,
                segmento.tipo_entidad,
                segmento.criterios_json,
                segmento.es_dinamico,
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
        """Ejecuta los CriteriosJSON del segmento y retorna lista de dicts."""
        conn = get_connection()

        criterios = {}
        if segmento.criterios_json:
            try:
                parsed = _json.loads(segmento.criterios_json)
                if isinstance(parsed, dict):
                    criterios = parsed
            except (_json.JSONDecodeError, TypeError):
                criterios = {}

        params = []

        if segmento.tipo_entidad == "Contactos":
            base_sql = """
                SELECT c.ContactoID AS ID,
                       (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreCompleto,
                       c.Email,
                       c.Puesto,
                       c.Departamento,
                       e.RazonSocial AS Empresa,
                       ci.Nombre AS Ciudad
                FROM Contactos c
                LEFT JOIN Empresas e ON c.EmpresaID = e.EmpresaID
                LEFT JOIN Ciudades ci ON c.CiudadID = ci.CiudadID
                LEFT JOIN OrigenesContacto oc ON c.OrigenID = oc.OrigenID
            """
            joins_extra = ""
            where = ["c.Activo = 1"]

            if criterios.get("puesto"):
                where.append("c.Puesto LIKE ?")
                params.append(f"%{criterios['puesto']}%")
            if criterios.get("departamento"):
                where.append("c.Departamento LIKE ?")
                params.append(f"%{criterios['departamento']}%")
            if criterios.get("ciudad"):
                where.append("ci.Nombre LIKE ?")
                params.append(f"%{criterios['ciudad']}%")
            if criterios.get("empresa"):
                where.append("e.RazonSocial LIKE ?")
                params.append(f"%{criterios['empresa']}%")
            if criterios.get("origen"):
                where.append("oc.Nombre LIKE ?")
                params.append(f"%{criterios['origen']}%")
            if "etiqueta_id" in criterios:
                try:
                    etq_id = int(criterios["etiqueta_id"])
                    joins_extra = " INNER JOIN ContactoEtiquetas ce ON c.ContactoID = ce.ContactoID"
                    where.append("ce.EtiquetaID = ?")
                    params.append(etq_id)
                except (ValueError, TypeError):
                    pass

            sql = (
                base_sql + joins_extra
                + " WHERE " + " AND ".join(where)
                + " ORDER BY c.Nombre, c.ApellidoPaterno"
            )

        else:  # Empresas
            base_sql = """
                SELECT e.EmpresaID AS ID,
                       e.RazonSocial AS NombreCompleto,
                       e.Email,
                       e.Telefono,
                       i.Nombre AS Industria,
                       te.Nombre AS Tamano,
                       ci.Nombre AS Ciudad
                FROM Empresas e
                LEFT JOIN Industrias i ON e.IndustriaID = i.IndustriaID
                LEFT JOIN TamanosEmpresa te ON e.TamanoID = te.TamanoID
                LEFT JOIN Ciudades ci ON e.CiudadID = ci.CiudadID
                LEFT JOIN OrigenesContacto oc ON e.OrigenID = oc.OrigenID
            """
            joins_extra = ""
            where = ["e.Activo = 1"]

            if criterios.get("industria"):
                where.append("i.Nombre LIKE ?")
                params.append(f"%{criterios['industria']}%")
            if criterios.get("tamano"):
                where.append("te.Nombre LIKE ?")
                params.append(f"%{criterios['tamano']}%")
            if criterios.get("ciudad"):
                where.append("ci.Nombre LIKE ?")
                params.append(f"%{criterios['ciudad']}%")
            if criterios.get("origen"):
                where.append("oc.Nombre LIKE ?")
                params.append(f"%{criterios['origen']}%")
            if "etiqueta_id" in criterios:
                try:
                    etq_id = int(criterios["etiqueta_id"])
                    joins_extra = " INNER JOIN EmpresaEtiquetas ee ON e.EmpresaID = ee.EmpresaID"
                    where.append("ee.EtiquetaID = ?")
                    params.append(etq_id)
                except (ValueError, TypeError):
                    pass

            sql = (
                base_sql + joins_extra
                + " WHERE " + " AND ".join(where)
                + " ORDER BY e.RazonSocial"
            )

        cursor = conn.execute(sql, params)
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
            criterios_json=row["CriteriosJSON"],
            cantidad_registros=row["CantidadRegistros"],
            es_dinamico=row["EsDinamico"],
            creado_por=row["CreadoPor"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            nombre_creador=safe("NombreCreador"),
        )
