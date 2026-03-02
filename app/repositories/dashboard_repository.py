# Repositorio del dashboard - queries contra vw_ResumenEjecutivo y tablas del sistema

from app.database.connection import get_connection


class DashboardRepository:

    def get_kpis(self):
        """Retorna un dict con los KPIs ejecutivos desde vw_ResumenEjecutivo."""
        conn = get_connection()
        cursor = conn.execute("SELECT * FROM vw_ResumenEjecutivo")
        row = cursor.fetchone()
        if not row:
            return {
                "ContactosActivos": 0,
                "EmpresasActivas": 0,
                "OportunidadesAbiertas": 0,
                "ValorPipeline": 0.0,
                "RevenueEsteMes": 0.0,
                "ActividadesPendientes": 0,
                "CampanasEnviadas": 0,
                "TasaConversionGlobal": 0.0,
            }
        return dict(row)

    def get_actividades_recientes(self, limit=8):
        """Retorna las actividades mas recientes del sistema."""
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT
                ta.Nombre   AS Tipo,
                a.Asunto,
                IFNULL(c.Nombre || ' ' || c.ApellidoPaterno, '—') AS Contacto,
                ea.Nombre   AS Estado,
                IFNULL(a.FechaFin, a.FechaInicio)                 AS Fecha
            FROM Actividades a
            INNER JOIN TiposActividad   ta ON a.TipoActividadID    = ta.TipoActividadID
            INNER JOIN EstadosActividad ea ON a.EstadoActividadID  = ea.EstadoActividadID
            LEFT  JOIN Contactos        c  ON a.ContactoID         = c.ContactoID
            ORDER BY a.FechaCreacion DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()

    def get_recordatorios_proximos(self, usuario_id, limit=8):
        """Retorna los recordatorios pendientes mas proximos del usuario."""
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT
                r.Titulo,
                r.FechaRecordatorio,
                CASE
                    WHEN c.ContactoID  IS NOT NULL THEN c.Nombre || ' ' || c.ApellidoPaterno
                    WHEN e.EmpresaID   IS NOT NULL THEN e.RazonSocial
                    WHEN o.OportunidadID IS NOT NULL THEN o.Nombre
                    ELSE '—'
                END AS Vinculado,
                IFNULL(r.TipoRecurrencia, '—') AS Recurrencia
            FROM Recordatorios r
            LEFT JOIN Contactos   c ON r.ContactoID    = c.ContactoID
            LEFT JOIN Empresas    e ON r.EmpresaID     = e.EmpresaID
            LEFT JOIN Oportunidades o ON r.OportunidadID = o.OportunidadID
            WHERE r.UsuarioID    = ?
              AND r.EsCompletado = 0
            ORDER BY r.FechaRecordatorio ASC
            LIMIT ?
            """,
            (usuario_id, limit),
        )
        return cursor.fetchall()
