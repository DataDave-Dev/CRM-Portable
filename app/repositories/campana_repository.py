# Repositorio de campanas - queries contra Campanas y CampanaDestinatarios

from app.database.connection import get_connection
from app.models.Campana import Campana


class CampanaRepository:

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT c.*,
                   p.Nombre AS NombrePlantilla,
                   s.Nombre AS NombreSegmento,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Campanas c
            LEFT JOIN PlantillasCorreo p ON c.PlantillaID = p.PlantillaID
            LEFT JOIN Segmentos s ON c.SegmentoID = s.SegmentoID
            LEFT JOIN Usuarios u ON c.PropietarioID = u.UsuarioID
            ORDER BY c.FechaCreacion DESC
            """
        )
        return [self._row_to_campana(row) for row in cursor.fetchall()]

    def find_by_id(self, campana_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT c.*,
                   p.Nombre AS NombrePlantilla,
                   s.Nombre AS NombreSegmento,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Campanas c
            LEFT JOIN PlantillasCorreo p ON c.PlantillaID = p.PlantillaID
            LEFT JOIN Segmentos s ON c.SegmentoID = s.SegmentoID
            LEFT JOIN Usuarios u ON c.PropietarioID = u.UsuarioID
            WHERE c.CampanaID = ?
            """,
            (campana_id,),
        )
        row = cursor.fetchone()
        return self._row_to_campana(row) if row else None

    def create(self, campana):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Campanas
                (Nombre, Descripcion, Tipo, Estado, PlantillaID, SegmentoID,
                 FechaProgramada, Presupuesto, MonedaID, PropietarioID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campana.nombre,
                campana.descripcion,
                campana.tipo,
                campana.estado,
                campana.plantilla_id,
                campana.segmento_id,
                campana.fecha_programada,
                campana.presupuesto,
                campana.moneda_id,
                campana.propietario_id,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, campana):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Campanas SET
                Nombre = ?, Descripcion = ?, Tipo = ?, Estado = ?,
                PlantillaID = ?, SegmentoID = ?, FechaProgramada = ?,
                Presupuesto = ?, MonedaID = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE CampanaID = ?
            """,
            (
                campana.nombre,
                campana.descripcion,
                campana.tipo,
                campana.estado,
                campana.plantilla_id,
                campana.segmento_id,
                campana.fecha_programada,
                campana.presupuesto,
                campana.moneda_id,
                campana.campana_id,
            ),
        )
        conn.commit()

    def update_estado(self, campana_id, estado):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Campanas SET
                Estado = ?,
                FechaModificacion = datetime('now', 'localtime')
            WHERE CampanaID = ?
            """,
            (estado, campana_id),
        )
        conn.commit()

    def update_metricas(self, campana_id, total_destinatarios=None, total_enviados=None):
        conn = get_connection()
        if total_destinatarios is not None:
            conn.execute(
                "UPDATE Campanas SET TotalDestinatarios = ? WHERE CampanaID = ?",
                (total_destinatarios, campana_id),
            )
        if total_enviados is not None:
            conn.execute(
                "UPDATE Campanas SET TotalEnviados = ? WHERE CampanaID = ?",
                (total_enviados, campana_id),
            )
        conn.commit()

    def sincronizar_metricas(self, campana_id):
        """Recalcula TotalDestinatarios y TotalEnviados contando directamente en CampanaDestinatarios."""
        conn = get_connection()
        conn.execute(
            """
            UPDATE Campanas SET
                TotalDestinatarios = (
                    SELECT COUNT(*) FROM CampanaDestinatarios WHERE CampanaID = ?
                ),
                TotalEnviados = (
                    SELECT COUNT(*) FROM CampanaDestinatarios
                    WHERE CampanaID = ? AND EstadoEnvio = 'Enviado'
                )
            WHERE CampanaID = ?
            """,
            (campana_id, campana_id, campana_id),
        )
        conn.commit()

    def delete(self, campana_id):
        conn = get_connection()
        conn.execute("DELETE FROM CampanaDestinatarios WHERE CampanaID = ?", (campana_id,))
        conn.execute("DELETE FROM Campanas WHERE CampanaID = ?", (campana_id,))
        conn.commit()

    # ---- Destinatarios ----

    def get_destinatarios(self, campana_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT cd.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   c.Email AS EmailContacto
            FROM CampanaDestinatarios cd
            LEFT JOIN Contactos c ON cd.ContactoID = c.ContactoID
            WHERE cd.CampanaID = ?
            ORDER BY cd.DestinatarioID
            """,
            (campana_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def agregar_destinatario(self, campana_id, contacto_id, email_destino):
        conn = get_connection()
        conn.execute(
            """
            INSERT OR IGNORE INTO CampanaDestinatarios
                (CampanaID, ContactoID, EmailDestino, EstadoEnvio)
            VALUES (?, ?, ?, 'Pendiente')
            """,
            (campana_id, contacto_id, email_destino),
        )
        conn.commit()

    def cargar_destinatarios_desde_segmento(self, campana_id, segmento_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT c.ContactoID, c.Email
            FROM SegmentoContactos sc
            INNER JOIN Contactos c ON sc.ContactoID = c.ContactoID
            WHERE sc.SegmentoID = ? AND c.Email IS NOT NULL AND c.Email != ''
            """,
            (segmento_id,),
        )
        rows = cursor.fetchall()
        for row in rows:
            conn.execute(
                """
                INSERT OR IGNORE INTO CampanaDestinatarios
                    (CampanaID, ContactoID, EmailDestino, EstadoEnvio)
                VALUES (?, ?, ?, 'Pendiente')
                """,
                (campana_id, row["ContactoID"], row["Email"]),
            )
        conn.commit()
        return len(rows)

    def eliminar_destinatario(self, destinatario_id):
        conn = get_connection()
        conn.execute(
            "DELETE FROM CampanaDestinatarios WHERE DestinatarioID = ?",
            (destinatario_id,),
        )
        conn.commit()

    def marcar_enviado(self, destinatario_id):
        conn = get_connection()
        conn.execute(
            """
            UPDATE CampanaDestinatarios SET
                EstadoEnvio = 'Enviado',
                FechaEnvio = datetime('now', 'localtime')
            WHERE DestinatarioID = ?
            """,
            (destinatario_id,),
        )
        conn.commit()

    def marcar_fallido(self, destinatario_id):
        conn = get_connection()
        conn.execute(
            """
            UPDATE CampanaDestinatarios SET
                EstadoEnvio = 'Fallido',
                FechaEnvio = datetime('now', 'localtime')
            WHERE DestinatarioID = ?
            """,
            (destinatario_id,),
        )
        conn.commit()

    @staticmethod
    def _row_to_campana(row):
        def safe(key):
            try:
                return row[key]
            except (KeyError, IndexError):
                return None

        return Campana(
            campana_id=row["CampanaID"],
            nombre=row["Nombre"],
            descripcion=row["Descripcion"],
            tipo=row["Tipo"],
            estado=row["Estado"],
            plantilla_id=row["PlantillaID"],
            segmento_id=row["SegmentoID"],
            fecha_programada=row["FechaProgramada"],
            fecha_envio=row["FechaEnvio"],
            fecha_finalizacion=row["FechaFinalizacion"],
            total_destinatarios=row["TotalDestinatarios"],
            total_enviados=row["TotalEnviados"],
            total_entregados=row["TotalEntregados"],
            total_abiertos=row["TotalAbiertos"],
            total_clics=row["TotalClics"],
            total_rebotados=row["TotalRebotados"],
            total_desuscripciones=row["TotalDesuscripciones"],
            presupuesto=row["Presupuesto"],
            moneda_id=row["MonedaID"],
            propietario_id=row["PropietarioID"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            nombre_plantilla=safe("NombrePlantilla"),
            nombre_segmento=safe("NombreSegmento"),
            nombre_propietario=safe("NombrePropietario"),
        )
