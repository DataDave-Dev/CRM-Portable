# Repositorio de historial de etapas - queries contra HistorialEtapas (solo lectura)

from app.database.connection import get_connection


class HistorialEtapasRepository:

    def find_by_oportunidad(self, oportunidad_id):
        # retorna lista de dicts con el historial de etapas de una oportunidad
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT h.HistorialID, h.FechaCambio, h.Comentario,
                   ev_ant.Nombre AS EtapaAnterior,
                   ev_nva.Nombre AS EtapaNueva,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombreUsuario
            FROM HistorialEtapas h
            LEFT JOIN EtapasVenta ev_ant ON h.EtapaAnteriorID = ev_ant.EtapaID
            INNER JOIN EtapasVenta ev_nva ON h.EtapaNuevaID = ev_nva.EtapaID
            INNER JOIN Usuarios u ON h.UsuarioID = u.UsuarioID
            WHERE h.OportunidadID = ?
            ORDER BY h.FechaCambio DESC
            """,
            (oportunidad_id,),
        )
        rows = cursor.fetchall()
        return [
            {
                "historial_id": row["HistorialID"],
                "fecha_cambio": row["FechaCambio"],
                "etapa_anterior": row["EtapaAnterior"] or "Inicio",
                "etapa_nueva": row["EtapaNueva"],
                "nombre_usuario": row["NombreUsuario"],
                "comentario": row["Comentario"] or "",
            }
            for row in rows
        ]
