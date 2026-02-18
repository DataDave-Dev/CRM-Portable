"""
Servicio de gestion de productos/servicios del catalogo CRM.

Validaciones:
    - nombre: requerido
    - codigo: unico si se proporciona
    - precio_unitario: numero >= 0 si se proporciona
"""

from app.repositories.producto_repository import ProductoRepository
from app.models.Producto import Producto
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class ProductoService:

    def __init__(self):
        self._repo = ProductoRepository()

    def obtener_todos(self, limit=None, offset=0):
        try:
            productos = self._repo.find_all(limit=limit, offset=offset)
            return productos, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener productos")
            return None, sanitize_error_message(e)

    def obtener_activos(self):
        try:
            return self._repo.find_activos(), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener productos activos")
            return None, sanitize_error_message(e)

    def contar_total(self):
        try:
            return self._repo.count_all(), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar productos")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, producto_id):
        try:
            return self._repo.find_by_id(producto_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener producto {producto_id}")
            return None, sanitize_error_message(e)

    def crear_producto(self, datos):
        error = self._validar(datos)
        if error:
            return None, error

        codigo = datos.get("codigo", "").strip() or None
        if codigo and self._repo.codigo_exists(codigo):
            return None, f"Ya existe un producto con el codigo '{codigo}'"

        precio = self._parsear_precio(datos.get("precio_unitario", ""))

        nuevo = Producto(
            codigo=codigo,
            nombre=datos.get("nombre", "").strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
            precio_unitario=precio,
            moneda_id=datos.get("moneda_id"),
            unidad_medida=datos.get("unidad_medida", "").strip() or None,
            activo=datos.get("activo", 1),
        )

        try:
            logger.info(f"Creando producto: '{nuevo.nombre}'")
            pid = self._repo.create(nuevo)
            nuevo.producto_id = pid
            logger.info(f"Producto {pid} creado exitosamente")
            return nuevo, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear producto: {nuevo.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_producto(self, producto_id, datos):
        error = self._validar(datos)
        if error:
            return None, error

        codigo = datos.get("codigo", "").strip() or None
        if codigo and self._repo.codigo_exists(codigo, excluir_id=producto_id):
            return None, f"Ya existe otro producto con el codigo '{codigo}'"

        precio = self._parsear_precio(datos.get("precio_unitario", ""))

        producto = Producto(
            producto_id=producto_id,
            codigo=codigo,
            nombre=datos.get("nombre", "").strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
            precio_unitario=precio,
            moneda_id=datos.get("moneda_id"),
            unidad_medida=datos.get("unidad_medida", "").strip() or None,
            activo=datos.get("activo", 1),
        )

        try:
            logger.info(f"Actualizando producto {producto_id}: '{producto.nombre}'")
            self._repo.update(producto)
            logger.info(f"Producto {producto_id} actualizado exitosamente")
            return producto, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar producto {producto_id}")
            return None, sanitize_error_message(e)

    # ==============================
    # HELPERS PRIVADOS
    # ==============================

    def _validar(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre del producto es requerido"
        precio_str = str(datos.get("precio_unitario", "") or "").strip()
        if precio_str:
            try:
                p = float(precio_str)
                if p < 0:
                    return "El precio unitario no puede ser negativo"
            except ValueError:
                return "El precio unitario debe ser un numero valido"
        return None

    @staticmethod
    def _parsear_precio(valor):
        s = str(valor or "").strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None
