"""
Servicio de gestion de segmentos para el sistema CRM.

Validaciones:
    - nombre: requerido, max 255 caracteres
    - tipo_entidad: 'Contactos' o 'Empresas'
    - criterios_json: JSON valido si se proporciona
"""

import json
from app.repositories.segmento_repository import SegmentoRepository
from app.models.Segmento import Segmento
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

_TIPOS_ENTIDAD = ("Contactos", "Empresas")


class SegmentoService:

    def __init__(self):
        self._repo = SegmentoRepository()

    def obtener_todos(self):
        try:
            segmentos = self._repo.find_all()
            logger.debug(f"Se obtuvieron {len(segmentos)} segmentos")
            return segmentos, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener segmentos")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, segmento_id):
        try:
            segmento = self._repo.find_by_id(segmento_id)
            return segmento, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener segmento {segmento_id}")
            return None, sanitize_error_message(e)

    def crear_segmento(self, datos, usuario_id):
        error = self._validar_datos(datos)
        if error:
            return None, error

        nuevo = Segmento(
            nombre=datos["nombre"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            tipo_entidad=datos.get("tipo_entidad", "Contactos"),
            criterios_json=datos.get("criterios_json", "").strip() or None,
            es_dinamico=1 if datos.get("es_dinamico") else 0,
            creado_por=usuario_id,
        )
        try:
            logger.info(f"Creando segmento: '{nuevo.nombre}' por usuario {usuario_id}")
            nuevo.segmento_id = self._repo.create(nuevo)
            logger.info(f"Segmento {nuevo.segmento_id} creado exitosamente")
            return nuevo, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear segmento: {nuevo.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_segmento(self, segmento_id, datos):
        error = self._validar_datos(datos)
        if error:
            return None, error

        segmento = Segmento(
            segmento_id=segmento_id,
            nombre=datos["nombre"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            tipo_entidad=datos.get("tipo_entidad", "Contactos"),
            criterios_json=datos.get("criterios_json", "").strip() or None,
            es_dinamico=1 if datos.get("es_dinamico") else 0,
        )
        try:
            logger.info(f"Actualizando segmento {segmento_id}: '{segmento.nombre}'")
            self._repo.update(segmento)
            logger.info(f"Segmento {segmento_id} actualizado exitosamente")
            return segmento, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar segmento {segmento_id}")
            return None, sanitize_error_message(e)

    def obtener_miembros(self, segmento):
        try:
            miembros = self._repo.get_miembros(segmento)
            self._repo.update_cantidad_registros(segmento.segmento_id, len(miembros))
            logger.debug(f"Segmento {segmento.segmento_id}: {len(miembros)} miembros encontrados")
            return miembros, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener miembros del segmento {segmento.segmento_id}")
            return None, sanitize_error_message(e)

    def eliminar_segmento(self, segmento_id):
        try:
            logger.info(f"Eliminando segmento {segmento_id}")
            self._repo.delete(segmento_id)
            logger.info(f"Segmento {segmento_id} eliminado exitosamente")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar segmento {segmento_id}")
            return False, sanitize_error_message(e)

    def _validar_datos(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre del segmento es requerido"
        if len(nombre) > 255:
            return "El nombre no puede exceder 255 caracteres"

        tipo = datos.get("tipo_entidad", "")
        if tipo not in _TIPOS_ENTIDAD:
            return f"El tipo de entidad debe ser uno de: {', '.join(_TIPOS_ENTIDAD)}"

        criterios = datos.get("criterios_json", "").strip()
        if criterios:
            try:
                json.loads(criterios)
            except json.JSONDecodeError:
                return "Los criterios deben ser JSON valido"

        return None
