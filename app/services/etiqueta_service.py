"""
Servicio de gestion de etiquetas para el sistema CRM.

Validaciones:
    - nombre: requerido, max 100 caracteres, unico
    - color: formato hex opcional (#RRGGBB)
    - categoria: opcional, max 100 caracteres
"""

import re
from app.repositories.etiqueta_repository import EtiquetaRepository
from app.models.Etiqueta import Etiqueta
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

_RE_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class EtiquetaService:

    def __init__(self):
        self._repo = EtiquetaRepository()

    def obtener_todas(self):
        try:
            etiquetas = self._repo.find_all()
            logger.debug(f"Se obtuvieron {len(etiquetas)} etiquetas")
            return etiquetas, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener etiquetas")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, etiqueta_id):
        try:
            etiqueta = self._repo.find_by_id(etiqueta_id)
            return etiqueta, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener etiqueta {etiqueta_id}")
            return None, sanitize_error_message(e)

    def crear_etiqueta(self, datos):
        error = self._validar_datos(datos)
        if error:
            return None, error

        nueva = Etiqueta(
            nombre=datos["nombre"].strip(),
            color=datos.get("color", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
        )
        try:
            logger.info(f"Creando etiqueta: '{nueva.nombre}'")
            nueva.etiqueta_id = self._repo.create(nueva)
            logger.info(f"Etiqueta {nueva.etiqueta_id} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear etiqueta: {nueva.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_etiqueta(self, etiqueta_id, datos):
        error = self._validar_datos(datos)
        if error:
            return None, error

        etiqueta = Etiqueta(
            etiqueta_id=etiqueta_id,
            nombre=datos["nombre"].strip(),
            color=datos.get("color", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
        )
        try:
            logger.info(f"Actualizando etiqueta {etiqueta_id}: '{etiqueta.nombre}'")
            self._repo.update(etiqueta)
            logger.info(f"Etiqueta {etiqueta_id} actualizada exitosamente")
            return etiqueta, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar etiqueta {etiqueta_id}")
            return None, sanitize_error_message(e)

    def eliminar_etiqueta(self, etiqueta_id):
        try:
            logger.info(f"Eliminando etiqueta {etiqueta_id}")
            self._repo.delete(etiqueta_id)
            logger.info(f"Etiqueta {etiqueta_id} eliminada exitosamente")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar etiqueta {etiqueta_id}")
            return False, sanitize_error_message(e)

    # ---- Asignaciones ----

    def get_contactos_asignados(self, etiqueta_id):
        try:
            return self._repo.get_contactos_asignados(etiqueta_id), None
        except Exception as e:
            return None, sanitize_error_message(e)

    def asignar_contacto(self, etiqueta_id, contacto_id, usuario_id=None):
        try:
            self._repo.asignar_contacto(etiqueta_id, contacto_id, usuario_id)
            return True, None
        except Exception as e:
            return False, sanitize_error_message(e)

    def quitar_contacto(self, etiqueta_id, contacto_id):
        try:
            self._repo.quitar_contacto(etiqueta_id, contacto_id)
            return True, None
        except Exception as e:
            return False, sanitize_error_message(e)

    def get_empresas_asignadas(self, etiqueta_id):
        try:
            return self._repo.get_empresas_asignadas(etiqueta_id), None
        except Exception as e:
            return None, sanitize_error_message(e)

    def asignar_empresa(self, etiqueta_id, empresa_id, usuario_id=None):
        try:
            self._repo.asignar_empresa(etiqueta_id, empresa_id, usuario_id)
            return True, None
        except Exception as e:
            return False, sanitize_error_message(e)

    def quitar_empresa(self, etiqueta_id, empresa_id):
        try:
            self._repo.quitar_empresa(etiqueta_id, empresa_id)
            return True, None
        except Exception as e:
            return False, sanitize_error_message(e)

    def get_etiquetas_de_contacto(self, contacto_id):
        try:
            return self._repo.get_etiquetas_de_contacto(contacto_id), None
        except Exception as e:
            return None, sanitize_error_message(e)

    def get_etiquetas_de_empresa(self, empresa_id):
        try:
            return self._repo.get_etiquetas_de_empresa(empresa_id), None
        except Exception as e:
            return None, sanitize_error_message(e)

    # ---- Validaciones ----

    def _validar_datos(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre de la etiqueta es requerido"
        if len(nombre) > 100:
            return "El nombre no puede exceder 100 caracteres"

        color = datos.get("color", "").strip()
        if color and not _RE_COLOR.match(color):
            return "El color debe tener formato hexadecimal (ej: #4a90d9)"

        categoria = datos.get("categoria", "").strip()
        if categoria and len(categoria) > 100:
            return "La categoria no puede exceder 100 caracteres"

        return None
