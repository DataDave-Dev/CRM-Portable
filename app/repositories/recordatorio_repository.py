# Repositorio de recordatorios - queries contra la tabla Recordatorios

from app.database.connection import get_connection
from app.models.Recordatorio import Recordatorio


class RecordatorioRepository:

    def find_by_usuario(self, usuario_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT r.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad
            FROM Recordatorios r
            LEFT JOIN Contactos c ON r.ContactoID = c.ContactoID
            LEFT JOIN Empresas e ON r.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON r.OportunidadID = o.OportunidadID
            WHERE r.UsuarioID = ?
            ORDER BY r.FechaRecordatorio ASC
            """,
            (usuario_id,),
        )
        return [self._row_to_recordatorio(row) for row in cursor.fetchall()]

    def find_pending(self, usuario_id):
        """Retorna todos los recordatorios pendientes (no completados) del usuario."""
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT r.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad
            FROM Recordatorios r
            LEFT JOIN Contactos c ON r.ContactoID = c.ContactoID
            LEFT JOIN Empresas e ON r.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON r.OportunidadID = o.OportunidadID
            WHERE r.UsuarioID = ?
              AND r.EsCompletado = 0
            ORDER BY r.FechaRecordatorio ASC
            """,
            (usuario_id,),
        )
        return [self._row_to_recordatorio(row) for row in cursor.fetchall()]

    def find_due(self, usuario_id):
        """Retorna recordatorios vencidos no completados y no leidos (notificacion pendiente)."""
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT r.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad
            FROM Recordatorios r
            LEFT JOIN Contactos c ON r.ContactoID = c.ContactoID
            LEFT JOIN Empresas e ON r.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON r.OportunidadID = o.OportunidadID
            WHERE r.UsuarioID = ?
              AND r.EsCompletado = 0
              AND r.EsLeido = 0
              AND r.FechaRecordatorio <= datetime('now', 'localtime')
            ORDER BY r.FechaRecordatorio ASC
            """,
            (usuario_id,),
        )
        return [self._row_to_recordatorio(row) for row in cursor.fetchall()]

    def find_by_id(self, recordatorio_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT r.*,
                   (c.Nombre || ' ' || c.ApellidoPaterno) AS NombreContacto,
                   e.RazonSocial AS NombreEmpresa,
                   o.Nombre AS NombreOportunidad
            FROM Recordatorios r
            LEFT JOIN Contactos c ON r.ContactoID = c.ContactoID
            LEFT JOIN Empresas e ON r.EmpresaID = e.EmpresaID
            LEFT JOIN Oportunidades o ON r.OportunidadID = o.OportunidadID
            WHERE r.RecordatorioID = ?
            """,
            (recordatorio_id,),
        )
        row = cursor.fetchone()
        return self._row_to_recordatorio(row) if row else None

    def create(self, recordatorio):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Recordatorios (
                UsuarioID, Titulo, Descripcion, FechaRecordatorio,
                ContactoID, EmpresaID, OportunidadID, ActividadID,
                TipoRecurrencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recordatorio.usuario_id,
                recordatorio.titulo,
                recordatorio.descripcion,
                recordatorio.fecha_recordatorio,
                recordatorio.contacto_id,
                recordatorio.empresa_id,
                recordatorio.oportunidad_id,
                recordatorio.actividad_id,
                recordatorio.tipo_recurrencia,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, recordatorio):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Recordatorios SET
                Titulo = ?, Descripcion = ?, FechaRecordatorio = ?,
                ContactoID = ?, EmpresaID = ?, OportunidadID = ?,
                ActividadID = ?, TipoRecurrencia = ?
            WHERE RecordatorioID = ?
            """,
            (
                recordatorio.titulo,
                recordatorio.descripcion,
                recordatorio.fecha_recordatorio,
                recordatorio.contacto_id,
                recordatorio.empresa_id,
                recordatorio.oportunidad_id,
                recordatorio.actividad_id,
                recordatorio.tipo_recurrencia,
                recordatorio.recordatorio_id,
            ),
        )
        conn.commit()

    def delete(self, recordatorio_id):
        conn = get_connection()
        conn.execute("DELETE FROM Recordatorios WHERE RecordatorioID = ?", (recordatorio_id,))
        conn.commit()

    def marcar_completado(self, recordatorio_id):
        conn = get_connection()
        conn.execute(
            "UPDATE Recordatorios SET EsCompletado = 1 WHERE RecordatorioID = ?",
            (recordatorio_id,),
        )
        conn.commit()

    def marcar_leido(self, recordatorio_id):
        conn = get_connection()
        conn.execute(
            "UPDATE Recordatorios SET EsLeido = 1 WHERE RecordatorioID = ?",
            (recordatorio_id,),
        )
        conn.commit()

    def _row_to_recordatorio(self, row):
        return Recordatorio(
            recordatorio_id=row["RecordatorioID"],
            usuario_id=row["UsuarioID"],
            titulo=row["Titulo"],
            descripcion=row["Descripcion"],
            fecha_recordatorio=row["FechaRecordatorio"],
            contacto_id=row["ContactoID"],
            empresa_id=row["EmpresaID"],
            oportunidad_id=row["OportunidadID"],
            actividad_id=row["ActividadID"],
            tipo_recurrencia=row["TipoRecurrencia"],
            es_leido=row["EsLeido"],
            es_completado=row["EsCompletado"],
            fecha_creacion=row["FechaCreacion"],
            nombre_contacto=row["NombreContacto"],
            nombre_empresa=row["NombreEmpresa"],
            nombre_oportunidad=row["NombreOportunidad"],
        )
