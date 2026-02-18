"""
Servicio de gestion de cotizaciones del CRM.

Validaciones:
    - oportunidad_id: requerido
    - numero_cotizacion: unico, auto-generado si no se proporciona
    - fecha_emision: formato AAAA-MM-DD
    - fecha_vigencia: formato AAAA-MM-DD si se proporciona
    - estado: uno de Borrador, Enviada, Aceptada, Rechazada, Vencida

IVA: 16% aplicado sobre subtotal.
"""

import re
import datetime
from app.repositories.cotizacion_repository import CotizacionRepository
from app.repositories.cotizacion_detalle_repository import CotizacionDetalleRepository
from app.models.Cotizacion import Cotizacion
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

ESTADOS_VALIDOS = ("Borrador", "Enviada", "Aceptada", "Rechazada", "Vencida")
IVA_RATE = 0.16


class CotizacionService:

    def __init__(self):
        self._repo = CotizacionRepository()
        self._detalle_repo = CotizacionDetalleRepository()

    def obtener_todas(self, limit=None, offset=0):
        try:
            cots = self._repo.find_all(limit=limit, offset=offset)
            return cots, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener cotizaciones")
            return None, sanitize_error_message(e)

    def contar_total(self):
        try:
            return self._repo.count_all(), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar cotizaciones")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, cotizacion_id):
        try:
            return self._repo.find_by_id(cotizacion_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener cotizacion {cotizacion_id}")
            return None, sanitize_error_message(e)

    def generar_numero(self):
        """Genera el siguiente NumeroCotizacion disponible en formato COT-YYYY-NNNN."""
        year = datetime.datetime.now().year
        ultimo = self._repo.get_ultimo_secuencial(year)
        return f"COT-{year}-{ultimo + 1:04d}"

    def crear_cotizacion(self, datos, items_detalle, usuario_id):
        error = self._validar(datos)
        if error:
            return None, error

        numero = datos.get("numero_cotizacion", "").strip()
        if not numero:
            numero = self.generar_numero()

        if self._repo.numero_exists(numero):
            return None, f"Ya existe una cotizacion con el numero '{numero}'"

        subtotal, iva, total = self._calcular_totales(items_detalle)

        nueva = Cotizacion(
            numero_cotizacion=numero,
            oportunidad_id=datos.get("oportunidad_id"),
            contacto_id=datos.get("contacto_id"),
            fecha_emision=datos.get("fecha_emision", "").strip() or datetime.datetime.now().strftime("%Y-%m-%d"),
            fecha_vigencia=datos.get("fecha_vigencia", "").strip() or None,
            subtotal=subtotal,
            iva=iva,
            total=total,
            moneda_id=datos.get("moneda_id"),
            estado=datos.get("estado", "Borrador"),
            notas=datos.get("notas", "").strip() or None,
            terminos_condiciones=datos.get("terminos_condiciones", "").strip() or None,
            creado_por=usuario_id,
        )

        try:
            logger.info(f"Creando cotizacion '{numero}' por usuario {usuario_id}")
            cid = self._repo.create(nueva)
            nueva.cotizacion_id = cid
            if items_detalle:
                self._detalle_repo.create_many(cid, items_detalle)
            logger.info(f"Cotizacion {cid} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear cotizacion: {numero}")
            return None, sanitize_error_message(e)

    def actualizar_cotizacion(self, cotizacion_id, datos, items_detalle):
        error = self._validar(datos)
        if error:
            return None, error

        numero = datos.get("numero_cotizacion", "").strip()
        if self._repo.numero_exists(numero, excluir_id=cotizacion_id):
            return None, f"Ya existe otra cotizacion con el numero '{numero}'"

        subtotal, iva, total = self._calcular_totales(items_detalle)

        cotizacion = Cotizacion(
            cotizacion_id=cotizacion_id,
            numero_cotizacion=numero,
            oportunidad_id=datos.get("oportunidad_id"),
            contacto_id=datos.get("contacto_id"),
            fecha_emision=datos.get("fecha_emision", "").strip() or datetime.datetime.now().strftime("%Y-%m-%d"),
            fecha_vigencia=datos.get("fecha_vigencia", "").strip() or None,
            subtotal=subtotal,
            iva=iva,
            total=total,
            moneda_id=datos.get("moneda_id"),
            estado=datos.get("estado", "Borrador"),
            notas=datos.get("notas", "").strip() or None,
            terminos_condiciones=datos.get("terminos_condiciones", "").strip() or None,
        )

        try:
            logger.info(f"Actualizando cotizacion {cotizacion_id}: '{numero}'")
            self._repo.update(cotizacion)
            self._detalle_repo.delete_by_cotizacion(cotizacion_id)
            if items_detalle:
                self._detalle_repo.create_many(cotizacion_id, items_detalle)
            logger.info(f"Cotizacion {cotizacion_id} actualizada exitosamente")
            return cotizacion, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar cotizacion {cotizacion_id}")
            return None, sanitize_error_message(e)

    def obtener_detalle(self, cotizacion_id):
        try:
            return self._detalle_repo.find_by_cotizacion(cotizacion_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener detalle de cotizacion {cotizacion_id}")
            return None, sanitize_error_message(e)

    # ==============================
    # HELPERS PRIVADOS
    # ==============================

    def _validar(self, datos):
        if not datos.get("oportunidad_id"):
            return "La oportunidad es requerida"
        fecha_emision = datos.get("fecha_emision", "").strip()
        if fecha_emision and not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_emision):
            return "La fecha de emision debe tener formato AAAA-MM-DD"
        fecha_vigencia = datos.get("fecha_vigencia", "").strip()
        if fecha_vigencia and not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_vigencia):
            return "La fecha de vigencia debe tener formato AAAA-MM-DD"
        estado = datos.get("estado", "Borrador")
        if estado not in ESTADOS_VALIDOS:
            return f"Estado invalido. Debe ser uno de: {', '.join(ESTADOS_VALIDOS)}"
        return None

    @staticmethod
    def _calcular_totales(items):
        subtotal = sum(
            item["cantidad"] * item["precio_unitario"] * (1 - item.get("descuento", 0) / 100.0)
            for item in items
        ) if items else 0.0
        subtotal = round(subtotal, 2)
        iva = round(subtotal * IVA_RATE, 2)
        total = round(subtotal + iva, 2)
        return subtotal, iva, total
