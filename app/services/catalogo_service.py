"""
Servicio generico de gestion de catalogos para el sistema CRM.

Este modulo proporciona una interfaz unificada para gestionar cualquier tipo de catalogo
(Industrias, Monedas, Paises, etc.) usando configuracion dinamica. Incluye validaciones
genericas, invalidacion de cache, y validacion de referencias antes de eliminar.

Caracteristicas:
    - Configuracion dinamica basada en app.config.catalogos
    - Validacion de campos requeridos segun configuracion
    - Validacion de unicidad en columna especificada
    - Invalidacion automatica de cache al modificar datos
    - Proteccion contra eliminacion de registros referenciados
    - Logging completo de operaciones

Catalogos soportados:
    - Industrias, TamanosEmpresa, OrigenesContacto, Monedas
    - Paises, Estados, Ciudades (jerarquia geografica)
    - Usuarios (catalogo especial para dropdowns)
    - Cualquier tabla configurada en catalogos.py

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

from app.repositories.catalogo_repository import CatalogoRepository
from app.utils.catalog_cache import CatalogCache
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class CatalogoService:
    """
    Servicio generico para operaciones CRUD en catalogos.

    Maneja cualquier tabla de catalogo basandose en configuracion dinamica,
    con validaciones, cache, y proteccion de integridad referencial.
    """
    def __init__(self, config):
        """
        Inicializa el servicio de catalogo con configuracion especifica.

        Args:
            config (dict): Configuracion del catalogo desde catalogos.py:
                - table (str): Nombre de la tabla
                - id_column (str): Nombre de la columna ID
                - display_column (str): Columna a mostrar
                - columns (list): Lista de columnas con tipo, label, required
                - unique_column (str, opcional): Columna que debe ser unica
        """
        self._config = config
        self._repo = CatalogoRepository(config)

    def obtener_todos(self, filters=None):
        """
        Obtiene todos los registros del catalogo con filtros opcionales.

        Args:
            filters (dict, opcional): Filtros a aplicar (ej: {"activo": 1})

        Returns:
            tuple: (list[dict]|None, str|None)
        """
        try:
            tabla = self._config.get('table', 'catalogo')
            logger.debug(f"Obteniendo registros de {tabla}")
            items = self._repo.find_all(filters)
            logger.info(f"Se obtuvieron {len(items)} registros de {tabla}")
            return items, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener datos de {self._config.get('table', 'catalogo')}")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, id_value):
        """Obtiene un registro especifico por su ID."""
        try:
            tabla = self._config.get('table', 'catalogo')
            logger.debug(f"Obteniendo registro {id_value} de {tabla}")
            item = self._repo.find_by_id(id_value)
            if item is None:
                return None, "Registro no encontrado"
            return item, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener registro {id_value}")
            return None, sanitize_error_message(e)

    def crear(self, datos):
        """
        Crea un nuevo registro en el catalogo.

        Args:
            datos (dict): Datos del registro segun configuracion de columnas

        Returns:
            tuple: (int|None, str|None) - ID del registro creado o error

        Note:
            - Valida campos requeridos segun configuracion
            - Valida unicidad si unique_column esta configurado
            - Invalida cache automaticamente
        """
        # validar campos requeridos
        for col_config in self._config['columns']:
            if col_config.get('required'):
                value = datos.get(col_config['name'], '')
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    return None, f"El campo {col_config['label']} es requerido"

        # validar unicidad
        unique_col = self._config.get('unique_column')
        if unique_col and unique_col in datos:
            if self._repo.name_exists(unique_col, datos[unique_col]):
                return None, f"Ya existe un registro con ese {unique_col}"

        try:
            tabla = self._config.get('table', 'catalogo')
            logger.info(f"Creando registro en {tabla}")
            new_id = self._repo.create(datos)
            # invalidar cache del catalogo modificado
            self._invalidate_cache()
            logger.info(f"Registro {new_id} creado en {tabla}")
            return new_id, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear en {self._config.get('table', 'catalogo')}")
            return None, sanitize_error_message(e)

    def actualizar(self, id_value, datos):
        """
        Actualiza un registro existente en el catalogo.

        Args:
            id_value (int): ID del registro a actualizar
            datos (dict): Datos a actualizar

        Returns:
            tuple: (bool|None, str|None)

        Note:
            - Valida unicidad excluyendo el registro actual
            - Invalida cache automaticamente
        """
        # validar campos requeridos
        for col_config in self._config['columns']:
            if col_config.get('required'):
                value = datos.get(col_config['name'], '')
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    return None, f"El campo {col_config['label']} es requerido"

        # validar unicidad excluyendo el registro actual
        unique_col = self._config.get('unique_column')
        if unique_col and unique_col in datos:
            if self._repo.name_exists(unique_col, datos[unique_col], exclude_id=id_value):
                return None, f"Ya existe otro registro con ese {unique_col}"

        try:
            tabla = self._config.get('table', 'catalogo')
            logger.info(f"Actualizando registro {id_value} en {tabla}")
            self._repo.update(id_value, datos)
            # invalidar cache del catalogo modificado
            self._invalidate_cache()
            logger.info(f"Registro {id_value} actualizado en {tabla}")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar {id_value} en {self._config.get('table', 'catalogo')}")
            return None, sanitize_error_message(e)

    def eliminar(self, id_value):
        """
        Elimina un registro del catalogo.

        Args:
            id_value (int): ID del registro a eliminar

        Returns:
            tuple: (bool|None, str|None)

        Note:
            - IMPORTANTE: Verifica referencias antes de eliminar
            - Impide eliminacion si existen registros que referencian este ID
            - Invalida cache automaticamente si la eliminacion es exitosa
        """
        tabla = self._config.get('table', 'catalogo')
        # verificar referencias antes de eliminar
        refs = self._repo.count_references(id_value)
        if refs > 0:
            logger.warning(f"Intento de eliminar registro {id_value} de {tabla} con {refs} referencias")
            return None, f"No se puede eliminar. Este registro es utilizado por {refs} registro(s) en el sistema."

        ok, error = self._repo.delete(id_value)
        if not ok:
            AppLogger.log_exception(logger, f"Error al eliminar {id_value} de {tabla}: {error}")
            return None, error
        # invalidar cache del catalogo modificado
        self._invalidate_cache()
        logger.info(f"Registro {id_value} eliminado de {tabla}")
        return True, None

    def _invalidate_cache(self):
        # invalida cache segun la tabla del catalogo
        table = self._config.get('table', '')
        cache_map = {
            'Industrias': 'industrias',
            'TamanosEmpresa': 'tamanos',
            'OrigenesContacto': 'origenes',
            'Monedas': 'monedas',
            'Paises': 'paises',
            'Estados': 'estados',
            'Ciudades': 'ciudades',
            'Usuarios': 'usuarios'
        }
        cache_key = cache_map.get(table)
        if cache_key:
            CatalogCache.invalidate(cache_key)
