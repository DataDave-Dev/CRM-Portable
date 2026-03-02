"""
Servicio de notificaciones y recordatorios.

Responsabilidades:
    - CRUD de recordatorios del usuario.
    - Consultar notificaciones del sistema.
    - Detectar recordatorios vencidos y enviar correo electronico al usuario.
    - Reutiliza la configuracion SMTP activa del modulo de Comunicacion.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.repositories.notificacion_repository import NotificacionRepository
from app.repositories.recordatorio_repository import RecordatorioRepository
from app.repositories.config_correo_repository import ConfigCorreoRepository
from app.models.Recordatorio import Recordatorio
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

_TIPOS_RECURRENCIA = ("Sin recurrencia", "Diaria", "Semanal", "Mensual")


class NotificacionService:

    def __init__(self):
        self._notif_repo = NotificacionRepository()
        self._record_repo = RecordatorioRepository()
        self._config_repo = ConfigCorreoRepository()

    # ==========================================
    # NOTIFICACIONES
    # ==========================================

    def obtener_notificaciones(self, usuario_id):
        try:
            return self._notif_repo.find_by_usuario(usuario_id), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener notificaciones")
            return [], sanitize_error_message(e)

    def obtener_no_leidas(self, usuario_id):
        try:
            return self._notif_repo.find_unread_by_usuario(usuario_id), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener notificaciones no leidas")
            return [], sanitize_error_message(e)

    def count_no_leidas(self, usuario_id):
        try:
            return self._notif_repo.count_unread(usuario_id)
        except Exception:
            return 0

    def marcar_como_leida(self, notificacion_id):
        try:
            self._notif_repo.mark_as_read(notificacion_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al marcar notificacion {notificacion_id} como leida")
            return False, sanitize_error_message(e)

    def marcar_todas_como_leidas(self, usuario_id):
        try:
            self._notif_repo.mark_all_read(usuario_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al marcar todas las notificaciones como leidas")
            return False, sanitize_error_message(e)

    # ==========================================
    # RECORDATORIOS
    # ==========================================

    def obtener_recordatorios_popup(self, usuario_id):
        """Retorna recordatorios pendientes (no completados) para mostrar en el popup."""
        try:
            return self._record_repo.find_pending(usuario_id), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener recordatorios para popup")
            return [], sanitize_error_message(e)

    def obtener_recordatorios(self, usuario_id):
        try:
            return self._record_repo.find_by_usuario(usuario_id), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener recordatorios")
            return [], sanitize_error_message(e)

    def crear_recordatorio(self, datos, usuario_id):
        error = self._validar_recordatorio(datos)
        if error:
            return None, error

        nuevo = Recordatorio(
            usuario_id=usuario_id,
            titulo=datos["titulo"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            fecha_recordatorio=datos["fecha_recordatorio"],
            contacto_id=datos.get("contacto_id") or None,
            empresa_id=datos.get("empresa_id") or None,
            oportunidad_id=datos.get("oportunidad_id") or None,
            actividad_id=datos.get("actividad_id") or None,
            tipo_recurrencia=datos.get("tipo_recurrencia") or None,
        )
        try:
            nuevo.recordatorio_id = self._record_repo.create(nuevo)
            logger.info(f"Recordatorio {nuevo.recordatorio_id} creado para usuario {usuario_id}")
            return nuevo, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al crear recordatorio")
            return None, sanitize_error_message(e)

    def actualizar_recordatorio(self, recordatorio_id, datos):
        error = self._validar_recordatorio(datos)
        if error:
            return None, error

        record = Recordatorio(
            recordatorio_id=recordatorio_id,
            titulo=datos["titulo"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            fecha_recordatorio=datos["fecha_recordatorio"],
            contacto_id=datos.get("contacto_id") or None,
            empresa_id=datos.get("empresa_id") or None,
            oportunidad_id=datos.get("oportunidad_id") or None,
            actividad_id=datos.get("actividad_id") or None,
            tipo_recurrencia=datos.get("tipo_recurrencia") or None,
        )
        try:
            self._record_repo.update(record)
            logger.info(f"Recordatorio {recordatorio_id} actualizado")
            return record, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar recordatorio {recordatorio_id}")
            return None, sanitize_error_message(e)

    def eliminar_recordatorio(self, recordatorio_id):
        try:
            self._record_repo.delete(recordatorio_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar recordatorio {recordatorio_id}")
            return False, sanitize_error_message(e)

    def completar_recordatorio(self, recordatorio_id):
        try:
            self._record_repo.marcar_completado(recordatorio_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al completar recordatorio {recordatorio_id}")
            return False, sanitize_error_message(e)

    def _validar_recordatorio(self, datos):
        titulo = datos.get("titulo", "").strip()
        if not titulo:
            return "El titulo del recordatorio es requerido"
        if len(titulo) > 255:
            return "El titulo no puede exceder 255 caracteres"

        fecha = datos.get("fecha_recordatorio", "").strip() if isinstance(datos.get("fecha_recordatorio"), str) else datos.get("fecha_recordatorio")
        if not fecha:
            return "La fecha del recordatorio es requerida"

        return None

    # ==========================================
    # PROCESAMIENTO DE RECORDATORIOS VENCIDOS
    # ==========================================

    def procesar_recordatorios_vencidos(self, usuario_id, email_usuario, nombre_usuario=""):
        """
        Detecta recordatorios vencidos para el usuario, envia un correo por cada uno
        y los marca como leidos (enviados). Retorna la lista de recordatorios procesados.

        Returns: (procesados: list[Recordatorio], error: str | None)
        """
        try:
            vencidos = self._record_repo.find_due(usuario_id)
        except Exception as e:
            return [], sanitize_error_message(e)

        if not vencidos:
            return [], None

        config = self._config_repo.find_activa()
        enviados = []
        errores = []

        for rec in vencidos:
            if config and config.host:
                ok, err = self._enviar_email_recordatorio(rec, email_usuario, nombre_usuario, config)
                if not ok:
                    errores.append(err)
            # Marcar como leido independientemente del resultado del correo
            try:
                self._record_repo.marcar_leido(rec.recordatorio_id)
                enviados.append(rec)
                logger.info(f"Recordatorio {rec.recordatorio_id} procesado para usuario {usuario_id}")
            except Exception as e:
                logger.error(f"Error al marcar recordatorio {rec.recordatorio_id} como leido: {e}")

        error_msg = "; ".join(errores) if errores else None
        return enviados, error_msg

    def _enviar_email_recordatorio(self, recordatorio, email_destino, nombre_usuario, config):
        """Envía un correo de recordatorio usando la configuracion SMTP activa."""
        try:
            cuerpo_texto = (
                f"Hola {nombre_usuario},\n\n"
                f"Tienes un recordatorio pendiente:\n\n"
                f"Titulo: {recordatorio.titulo}\n"
            )
            if recordatorio.descripcion:
                cuerpo_texto += f"Descripcion: {recordatorio.descripcion}\n"
            cuerpo_texto += f"Fecha: {recordatorio.fecha_recordatorio}\n"
            if recordatorio.nombre_contacto:
                cuerpo_texto += f"Contacto: {recordatorio.nombre_contacto}\n"
            if recordatorio.nombre_empresa:
                cuerpo_texto += f"Empresa: {recordatorio.nombre_empresa}\n"
            if recordatorio.nombre_oportunidad:
                cuerpo_texto += f"Oportunidad: {recordatorio.nombre_oportunidad}\n"
            cuerpo_texto += "\nEste es un mensaje automatico del CRM."

            cuerpo_html = f"""
            <html><body style="font-family: Segoe UI, Arial, sans-serif; color: #333;">
            <div style="max-width:600px;margin:auto;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
              <div style="background:#1a1a2e;padding:20px;">
                <h2 style="color:#fff;margin:0;">Recordatorio CRM</h2>
              </div>
              <div style="padding:24px;">
                <p>Hola <strong>{nombre_usuario}</strong>,</p>
                <p>Tienes el siguiente recordatorio pendiente:</p>
                <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                  <tr><td style="padding:8px;background:#f8f9fa;font-weight:600;width:140px;">Titulo</td>
                      <td style="padding:8px;">{recordatorio.titulo}</td></tr>
                  {"<tr><td style='padding:8px;background:#f8f9fa;font-weight:600;'>Descripcion</td><td style='padding:8px;'>" + recordatorio.descripcion + "</td></tr>" if recordatorio.descripcion else ""}
                  <tr><td style="padding:8px;background:#f8f9fa;font-weight:600;">Fecha</td>
                      <td style="padding:8px;">{recordatorio.fecha_recordatorio}</td></tr>
                  {"<tr><td style='padding:8px;background:#f8f9fa;font-weight:600;'>Contacto</td><td style='padding:8px;'>" + (recordatorio.nombre_contacto or "") + "</td></tr>" if recordatorio.nombre_contacto else ""}
                  {"<tr><td style='padding:8px;background:#f8f9fa;font-weight:600;'>Empresa</td><td style='padding:8px;'>" + (recordatorio.nombre_empresa or "") + "</td></tr>" if recordatorio.nombre_empresa else ""}
                  {"<tr><td style='padding:8px;background:#f8f9fa;font-weight:600;'>Oportunidad</td><td style='padding:8px;'>" + (recordatorio.nombre_oportunidad or "") + "</td></tr>" if recordatorio.nombre_oportunidad else ""}
                </table>
                <p style="color:#7f8c9b;font-size:13px;">Este es un mensaje automatico generado por el CRM.</p>
              </div>
            </div>
            </body></html>
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Recordatorio: {recordatorio.titulo}"
            msg["From"] = f"{config.nombre_remitente or config.email_remitente} <{config.email_remitente}>"
            msg["To"] = email_destino

            msg.attach(MIMEText(cuerpo_texto, "plain", "utf-8"))
            msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

            if config.usar_ssl:
                smtp = smtplib.SMTP_SSL(config.host, config.puerto, timeout=15)
            else:
                smtp = smtplib.SMTP(config.host, config.puerto, timeout=15)
                if config.usar_tls:
                    smtp.starttls()

            if config.usuario and config.contrasena:
                smtp.login(config.usuario, config.contrasena)

            smtp.sendmail(config.email_remitente, [email_destino], msg.as_string())
            smtp.quit()

            logger.info(f"Email de recordatorio enviado a {email_destino} para recordatorio {recordatorio.recordatorio_id}")
            return True, None

        except Exception as e:
            logger.error(f"Error al enviar email de recordatorio: {e}")
            return False, sanitize_error_message(e)

    @property
    def tipos_recurrencia(self):
        return _TIPOS_RECURRENCIA
