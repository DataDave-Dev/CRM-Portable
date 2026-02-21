# Repositorio de actividades - queries contra la tabla Actividades

from app.database.connection import get_connection
from app.models.Actividad import Actividad


class ActividadRepository:

    def find_all(self, limit=None, offset=0):
        conn = get_connection()
        query = """
            SELECT a.*,
                   ta.Nombre AS NombreTipoActividad,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario,
                   p.Nombre AS NombrePrioridad,
                   ea.Nombre AS NombreEstadoActividad
            FROM Actividades a
            LEFT JOIN TiposActividad ta ON a.TipoActividadID = ta.TipoActividadID
            LEFT JOIN Contactos ct ON a.ContactoID = ct.ContactoID
            LEFT JOIN Empresas e ON a.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON a.OportunidadID = o.OportunidadID
            LEFT JOIN Usuarios u ON a.PropietarioID = u.UsuarioID
            LEFT JOIN Prioridades p ON a.PrioridadID = p.PrioridadID
            LEFT JOIN EstadosActividad ea ON a.EstadoActividadID = ea.EstadoActividadID
            ORDER BY a.FechaCreacion DESC
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor = conn.execute(query)
        rows = cursor.fetchall()
        return [self._row_to_actividad(row) for row in rows]

    def count_all(self):
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) AS total FROM Actividades")
        return cursor.fetchone()["total"]

    def find_by_id(self, actividad_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT a.*,
                   ta.Nombre AS NombreTipoActividad,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario,
                   p.Nombre AS NombrePrioridad,
                   ea.Nombre AS NombreEstadoActividad
            FROM Actividades a
            LEFT JOIN TiposActividad ta ON a.TipoActividadID = ta.TipoActividadID
            LEFT JOIN Contactos ct ON a.ContactoID = ct.ContactoID
            LEFT JOIN Empresas e ON a.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON a.OportunidadID = o.OportunidadID
            LEFT JOIN Usuarios u ON a.PropietarioID = u.UsuarioID
            LEFT JOIN Prioridades p ON a.PrioridadID = p.PrioridadID
            LEFT JOIN EstadosActividad ea ON a.EstadoActividadID = ea.EstadoActividadID
            WHERE a.ActividadID = ?
            """,
            (actividad_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_actividad(row)

    def create(self, actividad):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Actividades (
                TipoActividadID, Asunto, Descripcion,
                ContactoID, EmpresaID, OportunidadID,
                PropietarioID, PrioridadID, EstadoActividadID,
                FechaInicio, FechaFin, FechaVencimiento,
                DuracionMinutos, Ubicacion, Resultado,
                CreadoPor, ModificadoPor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actividad.tipo_actividad_id,
                actividad.asunto,
                actividad.descripcion,
                actividad.contacto_id,
                actividad.empresa_id,
                actividad.oportunidad_id,
                actividad.propietario_id,
                actividad.prioridad_id,
                actividad.estado_actividad_id,
                actividad.fecha_inicio,
                actividad.fecha_fin,
                actividad.fecha_vencimiento,
                actividad.duracion_minutos,
                actividad.ubicacion,
                actividad.resultado,
                actividad.creado_por,
                actividad.modificado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, actividad):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Actividades SET
                TipoActividadID = ?, Asunto = ?, Descripcion = ?,
                ContactoID = ?, EmpresaID = ?, OportunidadID = ?,
                PropietarioID = ?, PrioridadID = ?, EstadoActividadID = ?,
                FechaInicio = ?, FechaFin = ?, FechaVencimiento = ?,
                DuracionMinutos = ?, Ubicacion = ?, Resultado = ?,
                ModificadoPor = ?
            WHERE ActividadID = ?
            """,
            (
                actividad.tipo_actividad_id,
                actividad.asunto,
                actividad.descripcion,
                actividad.contacto_id,
                actividad.empresa_id,
                actividad.oportunidad_id,
                actividad.propietario_id,
                actividad.prioridad_id,
                actividad.estado_actividad_id,
                actividad.fecha_inicio,
                actividad.fecha_fin,
                actividad.fecha_vencimiento,
                actividad.duracion_minutos,
                actividad.ubicacion,
                actividad.resultado,
                actividad.modificado_por,
                actividad.actividad_id,
            ),
        )
        conn.commit()

    @staticmethod
    def _row_to_actividad(row):
        def safe(key):
            try:
                return row[key]
            except (KeyError, IndexError):
                return None

        return Actividad(
            actividad_id=row["ActividadID"],
            tipo_actividad_id=row["TipoActividadID"],
            asunto=row["Asunto"],
            descripcion=row["Descripcion"],
            contacto_id=row["ContactoID"],
            empresa_id=row["EmpresaID"],
            oportunidad_id=row["OportunidadID"],
            propietario_id=row["PropietarioID"],
            prioridad_id=row["PrioridadID"],
            estado_actividad_id=row["EstadoActividadID"],
            fecha_inicio=row["FechaInicio"],
            fecha_fin=row["FechaFin"],
            fecha_vencimiento=row["FechaVencimiento"],
            duracion_minutos=row["DuracionMinutos"],
            ubicacion=row["Ubicacion"],
            resultado=row["Resultado"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            creado_por=row["CreadoPor"],
            modificado_por=row["ModificadoPor"],
            nombre_tipo_actividad=safe("NombreTipoActividad"),
            nombre_contacto=safe("NombreContacto"),
            nombre_empresa=safe("NombreEmpresa"),
            nombre_oportunidad=safe("NombreOportunidad"),
            nombre_propietario=safe("NombrePropietario"),
            nombre_prioridad=safe("NombrePrioridad"),
            nombre_estado_actividad=safe("NombreEstadoActividad"),
        )
