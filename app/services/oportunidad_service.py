"""
Servicio de gestion de oportunidades de venta para el sistema CRM.

Validaciones implementadas:
    - Campos requeridos: nombre, etapa_id, propietario_id
    - monto_estimado: numero positivo si se proporciona
    - probabilidad_cierre: entero 0-100 si se proporciona
    - fecha_cierre_estimada y fecha_cierre_real: formato AAAA-MM-DD
    - EsGanada: None (abierta), 1 (ganada), 0 (perdida)
"""

import re
from app.repositories.oportunidad_repository import OportunidadRepository
from app.repositories.oportunidad_producto_repository import OportunidadProductoRepository
from app.models.Oportunidad import Oportunidad
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class OportunidadService:

    def __init__(self):
        self._repo = OportunidadRepository()
        self._producto_repo = OportunidadProductoRepository()

    def obtener_todas(self, limit=None, offset=0):
        try:
            logger.debug(f"Obteniendo oportunidades - limit: {limit}, offset: {offset}")
            oportunidades = self._repo.find_all(limit=limit, offset=offset)
            logger.info(f"Se obtuvieron {len(oportunidades)} oportunidades")
            return oportunidades, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener oportunidades")
            return None, sanitize_error_message(e)

    def contar_total(self):
        try:
            total = self._repo.count_all()
            logger.debug(f"Total de oportunidades: {total}")
            return total, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar oportunidades")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, oportunidad_id):
        try:
            logger.debug(f"Obteniendo oportunidad {oportunidad_id}")
            oportunidad = self._repo.find_by_id(oportunidad_id)
            return oportunidad, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener oportunidad {oportunidad_id}")
            return None, sanitize_error_message(e)

    def crear_oportunidad(self, datos, usuario_actual_id):
        error = self._validar_datos(datos)
        if error:
            return None, error

        monto = self._parsear_monto(datos.get("monto_estimado", ""))
        probabilidad = self._parsear_probabilidad(datos.get("probabilidad_cierre", ""))
        es_ganada = datos.get("es_ganada")  # None, 0 o 1

        nueva = Oportunidad(
            nombre=datos.get("nombre", "").strip(),
            empresa_id=datos.get("empresa_id"),
            contacto_id=datos.get("contacto_id"),
            etapa_id=datos.get("etapa_id"),
            monto_estimado=monto,
            moneda_id=datos.get("moneda_id"),
            probabilidad_cierre=probabilidad,
            fecha_cierre_estimada=datos.get("fecha_cierre_estimada", "").strip() or None,
            fecha_cierre_real=datos.get("fecha_cierre_real", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            motivos_perdida_id=datos.get("motivos_perdida_id"),
            notas_perdida=datos.get("notas_perdida", "").strip() or None,
            descripcion=datos.get("descripcion", "").strip() or None,
            es_ganada=es_ganada,
            creado_por=usuario_actual_id,
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Creando oportunidad: '{nueva.nombre}' por usuario {usuario_actual_id}")
            oportunidad_id = self._repo.create(nueva)
            nueva.oportunidad_id = oportunidad_id
            logger.info(f"Oportunidad {oportunidad_id} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear oportunidad: {nueva.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_oportunidad(self, oportunidad_id, datos, usuario_actual_id):
        error = self._validar_datos(datos)
        if error:
            return None, error

        monto = self._parsear_monto(datos.get("monto_estimado", ""))
        probabilidad = self._parsear_probabilidad(datos.get("probabilidad_cierre", ""))
        es_ganada = datos.get("es_ganada")

        oportunidad = Oportunidad(
            oportunidad_id=oportunidad_id,
            nombre=datos.get("nombre", "").strip(),
            empresa_id=datos.get("empresa_id"),
            contacto_id=datos.get("contacto_id"),
            etapa_id=datos.get("etapa_id"),
            monto_estimado=monto,
            moneda_id=datos.get("moneda_id"),
            probabilidad_cierre=probabilidad,
            fecha_cierre_estimada=datos.get("fecha_cierre_estimada", "").strip() or None,
            fecha_cierre_real=datos.get("fecha_cierre_real", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            motivos_perdida_id=datos.get("motivos_perdida_id"),
            notas_perdida=datos.get("notas_perdida", "").strip() or None,
            descripcion=datos.get("descripcion", "").strip() or None,
            es_ganada=es_ganada,
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Actualizando oportunidad {oportunidad_id}: '{oportunidad.nombre}' por usuario {usuario_actual_id}")
            self._repo.update(oportunidad)
            logger.info(f"Oportunidad {oportunidad_id} actualizada exitosamente")
            return oportunidad, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar oportunidad {oportunidad_id}")
            return None, sanitize_error_message(e)

    # ==============================
    # HELPERS PRIVADOS
    # ==============================

    def _validar_datos(self, datos):
        # nombre requerido
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre de la oportunidad es requerido"

        # etapa requerida
        if not datos.get("etapa_id"):
            return "La etapa de venta es requerida"

        # propietario requerido
        if not datos.get("propietario_id"):
            return "El propietario (vendedor) es requerido"

        # monto estimado: debe ser numero >= 0 si se proporciona
        monto_str = datos.get("monto_estimado", "").strip() if isinstance(datos.get("monto_estimado"), str) else str(datos.get("monto_estimado", "") or "")
        if monto_str:
            try:
                monto = float(monto_str)
                if monto < 0:
                    return "El monto estimado no puede ser negativo"
            except ValueError:
                return "El monto estimado debe ser un numero valido"

        # probabilidad: entero 0-100 si se proporciona
        prob_str = datos.get("probabilidad_cierre", "").strip() if isinstance(datos.get("probabilidad_cierre"), str) else str(datos.get("probabilidad_cierre", "") or "")
        if prob_str:
            try:
                prob = int(prob_str)
                if prob < 0 or prob > 100:
                    return "La probabilidad de cierre debe estar entre 0 y 100"
            except ValueError:
                return "La probabilidad de cierre debe ser un numero entero"

        # fecha cierre estimada: AAAA-MM-DD si se proporciona
        fecha_est = datos.get("fecha_cierre_estimada", "").strip() if isinstance(datos.get("fecha_cierre_estimada"), str) else ""
        if fecha_est:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_est):
                return "La fecha de cierre estimada debe tener formato AAAA-MM-DD"

        # fecha cierre real: AAAA-MM-DD si se proporciona
        fecha_real = datos.get("fecha_cierre_real", "").strip() if isinstance(datos.get("fecha_cierre_real"), str) else ""
        if fecha_real:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_real):
                return "La fecha de cierre real debe tener formato AAAA-MM-DD"

        return None

    @staticmethod
    def _parsear_monto(valor):
        if not valor and valor != 0:
            return None
        s = str(valor).strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def _parsear_probabilidad(valor):
        if not valor and valor != 0:
            return None
        s = str(valor).strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None

    def guardar_productos(self, oportunidad_id, items):
        """Reemplaza todos los productos de la oportunidad con la lista recibida."""
        try:
            self._producto_repo.delete_by_oportunidad(oportunidad_id)
            if items:
                self._producto_repo.create_many(oportunidad_id, items)
            logger.info(f"Productos de oportunidad {oportunidad_id} actualizados: {len(items)} items")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al guardar productos de oportunidad {oportunidad_id}")
            return False, sanitize_error_message(e)

    def obtener_productos(self, oportunidad_id):
        """Obtiene todos los productos vinculados a una oportunidad."""
        try:
            return self._producto_repo.find_by_oportunidad(oportunidad_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener productos de oportunidad {oportunidad_id}")
            return None, sanitize_error_message(e)
