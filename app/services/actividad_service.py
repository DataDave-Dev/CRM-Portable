"""
Servicio de gestion de actividades para el sistema CRM.

Validaciones implementadas:
    - Campos requeridos: tipo_actividad_id, asunto, propietario_id, estado_actividad_id
    - duracion_minutos: entero positivo si se proporciona
    - fecha_inicio, fecha_fin, fecha_vencimiento: formato AAAA-MM-DD si se proporciona
"""

import re
from app.repositories.actividad_repository import ActividadRepository
from app.models.Actividad import Actividad
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class ActividadService:

    def __init__(self):
        self._repo = ActividadRepository()

    def obtener_todas(self, limit=None, offset=0):
        try:
            logger.debug(f"Obteniendo actividades - limit: {limit}, offset: {offset}")
            actividades = self._repo.find_all(limit=limit, offset=offset)
            logger.info(f"Se obtuvieron {len(actividades)} actividades")
            return actividades, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener actividades")
            return None, sanitize_error_message(e)

    def contar_total(self):
        try:
            total = self._repo.count_all()
            logger.debug(f"Total de actividades: {total}")
            return total, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar actividades")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, actividad_id):
        try:
            logger.debug(f"Obteniendo actividad {actividad_id}")
            actividad = self._repo.find_by_id(actividad_id)
            return actividad, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener actividad {actividad_id}")
            return None, sanitize_error_message(e)

    def crear_actividad(self, datos, usuario_actual_id):
        error = self._validar_datos(datos)
        if error:
            return None, error

        nueva = Actividad(
            tipo_actividad_id=datos.get("tipo_actividad_id"),
            asunto=datos.get("asunto", "").strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            contacto_id=datos.get("contacto_id"),
            empresa_id=datos.get("empresa_id"),
            oportunidad_id=datos.get("oportunidad_id"),
            propietario_id=datos.get("propietario_id"),
            prioridad_id=datos.get("prioridad_id"),
            estado_actividad_id=datos.get("estado_actividad_id"),
            fecha_inicio=datos.get("fecha_inicio", "").strip() or None,
            fecha_fin=datos.get("fecha_fin", "").strip() or None,
            fecha_vencimiento=datos.get("fecha_vencimiento", "").strip() or None,
            duracion_minutos=self._parsear_entero(datos.get("duracion_minutos", "")),
            ubicacion=datos.get("ubicacion", "").strip() or None,
            resultado=datos.get("resultado", "").strip() or None,
            creado_por=usuario_actual_id,
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Creando actividad: '{nueva.asunto}' por usuario {usuario_actual_id}")
            actividad_id = self._repo.create(nueva)
            nueva.actividad_id = actividad_id
            logger.info(f"Actividad {actividad_id} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear actividad: {nueva.asunto}")
            return None, sanitize_error_message(e)

    def actualizar_actividad(self, actividad_id, datos, usuario_actual_id):
        error = self._validar_datos(datos)
        if error:
            return None, error

        actividad = Actividad(
            actividad_id=actividad_id,
            tipo_actividad_id=datos.get("tipo_actividad_id"),
            asunto=datos.get("asunto", "").strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            contacto_id=datos.get("contacto_id"),
            empresa_id=datos.get("empresa_id"),
            oportunidad_id=datos.get("oportunidad_id"),
            propietario_id=datos.get("propietario_id"),
            prioridad_id=datos.get("prioridad_id"),
            estado_actividad_id=datos.get("estado_actividad_id"),
            fecha_inicio=datos.get("fecha_inicio", "").strip() or None,
            fecha_fin=datos.get("fecha_fin", "").strip() or None,
            fecha_vencimiento=datos.get("fecha_vencimiento", "").strip() or None,
            duracion_minutos=self._parsear_entero(datos.get("duracion_minutos", "")),
            ubicacion=datos.get("ubicacion", "").strip() or None,
            resultado=datos.get("resultado", "").strip() or None,
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Actualizando actividad {actividad_id}: '{actividad.asunto}' por usuario {usuario_actual_id}")
            self._repo.update(actividad)
            logger.info(f"Actividad {actividad_id} actualizada exitosamente")
            return actividad, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar actividad {actividad_id}")
            return None, sanitize_error_message(e)

    # ==============================
    # HELPERS PRIVADOS
    # ==============================

    def _validar_datos(self, datos):
        # tipo de actividad requerido
        if not datos.get("tipo_actividad_id"):
            return "El tipo de actividad es requerido"

        # asunto requerido
        asunto = datos.get("asunto", "").strip()
        if not asunto:
            return "El asunto es requerido"
        if len(asunto) > 255:
            return "El asunto no puede exceder 255 caracteres"

        # propietario requerido
        if not datos.get("propietario_id"):
            return "El propietario (responsable) es requerido"

        # estado requerido
        if not datos.get("estado_actividad_id"):
            return "El estado de la actividad es requerido"

        # duracion: entero positivo si se proporciona
        dur_str = str(datos.get("duracion_minutos", "") or "").strip()
        if dur_str:
            try:
                dur = int(dur_str)
                if dur < 0:
                    return "La duracion no puede ser negativa"
            except ValueError:
                return "La duracion debe ser un numero entero de minutos"

        # fechas: AAAA-MM-DD si se proporcionan
        for campo, label in [
            ("fecha_inicio", "fecha de inicio"),
            ("fecha_fin", "fecha de fin"),
            ("fecha_vencimiento", "fecha de vencimiento"),
        ]:
            val = str(datos.get(campo, "") or "").strip()
            if val and not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                return f"La {label} debe tener formato AAAA-MM-DD"

        return None

    @staticmethod
    def _parsear_entero(valor):
        if not valor and valor != 0:
            return None
        s = str(valor).strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None
