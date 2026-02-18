# Repositorio de oportunidades - queries contra la tabla Oportunidades

from app.database.connection import get_connection
from app.models.Oportunidad import Oportunidad


class OportunidadRepository:

    def find_all(self, limit=None, offset=0):
        # obtiene oportunidades con paginacion opcional
        conn = get_connection()
        query = """
            SELECT o.*,
                   e.RazonSocial AS NombreEmpresa,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   ev.Nombre AS NombreEtapa,
                   m.Nombre AS NombreMoneda,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario,
                   oc.Nombre AS NombreOrigen,
                   mp.Nombre AS NombreMotivoPerdida
            FROM Oportunidades o
            LEFT JOIN Empresas e ON o.EmpresaID = e.EmpresaID
            LEFT JOIN Contactos ct ON o.ContactoID = ct.ContactoID
            LEFT JOIN EtapasVenta ev ON o.EtapaID = ev.EtapaID
            LEFT JOIN Monedas m ON o.MonedaID = m.MonedaID
            LEFT JOIN Usuarios u ON o.PropietarioID = u.UsuarioID
            LEFT JOIN OrigenesContacto oc ON o.OrigenID = oc.OrigenID
            LEFT JOIN MotivosPerdida mp ON o.MotivosPerdidaID = mp.MotivoID
            ORDER BY o.FechaCreacion DESC
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor = conn.execute(query)
        rows = cursor.fetchall()
        return [self._row_to_oportunidad(row) for row in rows]

    def count_all(self):
        # cuenta total de oportunidades para calcular paginas
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) as total FROM Oportunidades")
        return cursor.fetchone()["total"]

    def find_by_id(self, oportunidad_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT o.*,
                   e.RazonSocial AS NombreEmpresa,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   ev.Nombre AS NombreEtapa,
                   m.Nombre AS NombreMoneda,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario,
                   oc.Nombre AS NombreOrigen,
                   mp.Nombre AS NombreMotivoPerdida
            FROM Oportunidades o
            LEFT JOIN Empresas e ON o.EmpresaID = e.EmpresaID
            LEFT JOIN Contactos ct ON o.ContactoID = ct.ContactoID
            LEFT JOIN EtapasVenta ev ON o.EtapaID = ev.EtapaID
            LEFT JOIN Monedas m ON o.MonedaID = m.MonedaID
            LEFT JOIN Usuarios u ON o.PropietarioID = u.UsuarioID
            LEFT JOIN OrigenesContacto oc ON o.OrigenID = oc.OrigenID
            LEFT JOIN MotivosPerdida mp ON o.MotivosPerdidaID = mp.MotivoID
            WHERE o.OportunidadID = ?
            """,
            (oportunidad_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_oportunidad(row)

    def create(self, oportunidad):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Oportunidades (
                Nombre, EmpresaID, ContactoID, EtapaID,
                MontoEstimado, MonedaID, ProbabilidadCierre,
                FechaCierreEstimada, FechaCierreReal, OrigenID,
                PropietarioID, MotivosPerdidaID, NotasPerdida,
                Descripcion, EsGanada, CreadoPor, ModificadoPor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                oportunidad.nombre,
                oportunidad.empresa_id,
                oportunidad.contacto_id,
                oportunidad.etapa_id,
                oportunidad.monto_estimado,
                oportunidad.moneda_id,
                oportunidad.probabilidad_cierre,
                oportunidad.fecha_cierre_estimada,
                oportunidad.fecha_cierre_real,
                oportunidad.origen_id,
                oportunidad.propietario_id,
                oportunidad.motivos_perdida_id,
                oportunidad.notas_perdida,
                oportunidad.descripcion,
                oportunidad.es_ganada,
                oportunidad.creado_por,
                oportunidad.modificado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, oportunidad):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Oportunidades SET
                Nombre = ?, EmpresaID = ?, ContactoID = ?, EtapaID = ?,
                MontoEstimado = ?, MonedaID = ?, ProbabilidadCierre = ?,
                FechaCierreEstimada = ?, FechaCierreReal = ?, OrigenID = ?,
                PropietarioID = ?, MotivosPerdidaID = ?, NotasPerdida = ?,
                Descripcion = ?, EsGanada = ?, ModificadoPor = ?
            WHERE OportunidadID = ?
            """,
            (
                oportunidad.nombre,
                oportunidad.empresa_id,
                oportunidad.contacto_id,
                oportunidad.etapa_id,
                oportunidad.monto_estimado,
                oportunidad.moneda_id,
                oportunidad.probabilidad_cierre,
                oportunidad.fecha_cierre_estimada,
                oportunidad.fecha_cierre_real,
                oportunidad.origen_id,
                oportunidad.propietario_id,
                oportunidad.motivos_perdida_id,
                oportunidad.notas_perdida,
                oportunidad.descripcion,
                oportunidad.es_ganada,
                oportunidad.modificado_por,
                oportunidad.oportunidad_id,
            ),
        )
        conn.commit()

    @staticmethod
    def _row_to_oportunidad(row):
        nombre_empresa = None
        nombre_contacto = None
        nombre_etapa = None
        nombre_moneda = None
        nombre_propietario = None
        nombre_origen = None
        nombre_motivo_perdida = None

        try:
            nombre_empresa = row["NombreEmpresa"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_contacto = row["NombreContacto"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_etapa = row["NombreEtapa"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_moneda = row["NombreMoneda"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_propietario = row["NombrePropietario"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_origen = row["NombreOrigen"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_motivo_perdida = row["NombreMotivoPerdida"]
        except (KeyError, IndexError):
            pass

        return Oportunidad(
            oportunidad_id=row["OportunidadID"],
            nombre=row["Nombre"],
            empresa_id=row["EmpresaID"],
            contacto_id=row["ContactoID"],
            etapa_id=row["EtapaID"],
            monto_estimado=row["MontoEstimado"],
            moneda_id=row["MonedaID"],
            probabilidad_cierre=row["ProbabilidadCierre"],
            fecha_cierre_estimada=row["FechaCierreEstimada"],
            fecha_cierre_real=row["FechaCierreReal"],
            origen_id=row["OrigenID"],
            propietario_id=row["PropietarioID"],
            motivos_perdida_id=row["MotivosPerdidaID"],
            notas_perdida=row["NotasPerdida"],
            descripcion=row["Descripcion"],
            es_ganada=row["EsGanada"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            creado_por=row["CreadoPor"],
            modificado_por=row["ModificadoPor"],
            nombre_empresa=nombre_empresa,
            nombre_contacto=nombre_contacto,
            nombre_etapa=nombre_etapa,
            nombre_moneda=nombre_moneda,
            nombre_propietario=nombre_propietario,
            nombre_origen=nombre_origen,
            nombre_motivo_perdida=nombre_motivo_perdida,
        )
