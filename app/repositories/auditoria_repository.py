# Acceso a datos para log de auditoria

import json
from app.database.connection import get_connection


class AuditoriaRepository:
    def registrar_accion(self, usuario_id, accion, entidad_tipo, entidad_id, valores_anteriores=None, valores_nuevos=None, ip_origen=None):
        # registra una accion en el log de auditoria
        conn = get_connection()

        # convertir diccionarios a JSON
        valores_ant_json = json.dumps(valores_anteriores) if valores_anteriores else None
        valores_new_json = json.dumps(valores_nuevos) if valores_nuevos else None

        cursor = conn.execute(
            """
            INSERT INTO LogAuditoria (
                UsuarioID, Accion, EntidadTipo, EntidadID,
                ValoresAnteriores, ValoresNuevos, IPOrigen
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (usuario_id, accion, entidad_tipo, entidad_id, valores_ant_json, valores_new_json, ip_origen)
        )

        conn.commit()
        return cursor.lastrowid

    def obtener_logs(self, limit=100, offset=0, entidad_tipo=None, entidad_id=None, usuario_id=None):
        # obtiene logs de auditoria con filtros opcionales
        conn = get_connection()

        query = "SELECT * FROM LogAuditoria WHERE 1=1"
        params = []

        if entidad_tipo:
            query += " AND EntidadTipo = ?"
            params.append(entidad_tipo)

        if entidad_id:
            query += " AND EntidadID = ?"
            params.append(entidad_id)

        if usuario_id:
            query += " AND UsuarioID = ?"
            params.append(usuario_id)

        query += " ORDER BY FechaAccion DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.execute(query, params)
        return cursor.fetchall()

    def obtener_historial_entidad(self, entidad_tipo, entidad_id):
        # obtiene el historial completo de una entidad
        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT l.*, u.Nombre, u.ApellidoPaterno
            FROM LogAuditoria l
            LEFT JOIN Usuarios u ON l.UsuarioID = u.UsuarioID
            WHERE l.EntidadTipo = ? AND l.EntidadID = ?
            ORDER BY l.FechaAccion DESC
            """,
            (entidad_tipo, entidad_id)
        )

        return cursor.fetchall()
