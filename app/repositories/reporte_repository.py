from app.database.connection import get_connection


class ReporteRepository:

    def _rows_to_dicts(self, cursor):
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def get_pipeline_ventas(self, fecha_desde=None, fecha_hasta=None):
        conn = get_connection()
        query = "SELECT * FROM vw_PipelineVentas"
        params = []
        if fecha_desde and fecha_hasta:
            query += " WHERE date(FechaCreacion) BETWEEN date(?) AND date(?)"
            params = [str(fecha_desde), str(fecha_hasta)]
        query += " ORDER BY OrdenEtapa, ValorPonderado DESC"
        cur = conn.execute(query, params)
        return self._rows_to_dicts(cur)

    def get_rendimiento_vendedores(self):
        conn = get_connection()
        cur = conn.execute("SELECT * FROM vw_RendimientoVendedores ORDER BY MontoGanado DESC")
        return self._rows_to_dicts(cur)

    def get_conversion_por_etapa(self):
        conn = get_connection()
        cur = conn.execute("SELECT * FROM vw_ConversionPorEtapa ORDER BY Orden")
        return self._rows_to_dicts(cur)

    def get_analisis_campanas(self, fecha_desde=None, fecha_hasta=None):
        conn = get_connection()
        query = "SELECT * FROM vw_AnalisisCampanas"
        params = []
        if fecha_desde and fecha_hasta:
            # Incluir campañas sin fecha de envío (borradores) siempre
            query += " WHERE FechaEnvio IS NULL OR date(FechaEnvio) BETWEEN date(?) AND date(?)"
            params = [str(fecha_desde), str(fecha_hasta)]
        query += " ORDER BY FechaEnvio DESC"
        cur = conn.execute(query, params)
        return self._rows_to_dicts(cur)

    def get_actividad_contactos(self, fecha_desde=None, fecha_hasta=None):
        conn = get_connection()
        query = "SELECT * FROM vw_ActividadRecienteContacto"
        params = []
        if fecha_desde and fecha_hasta:
            # Incluir contactos sin actividad registrada siempre (UltimaActividad NULL)
            query += " WHERE UltimaActividad IS NULL OR date(UltimaActividad) BETWEEN date(?) AND date(?)"
            params = [str(fecha_desde), str(fecha_hasta)]
        query += " ORDER BY DiasSinContacto DESC"
        cur = conn.execute(query, params)
        return self._rows_to_dicts(cur)
