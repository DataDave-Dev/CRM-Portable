# Logica de negocio generica para catalogos

from app.repositories.catalogo_repository import CatalogoRepository
from app.utils.catalog_cache import CatalogCache


class CatalogoService:
    def __init__(self, config):
        self._config = config
        self._repo = CatalogoRepository(config)

    def obtener_todos(self, filters=None):
        try:
            items = self._repo.find_all(filters)
            return items, None
        except Exception as e:
            return None, f"Error al obtener datos: {str(e)}"

    def obtener_por_id(self, id_value):
        try:
            item = self._repo.find_by_id(id_value)
            if item is None:
                return None, "Registro no encontrado"
            return item, None
        except Exception as e:
            return None, f"Error al obtener registro: {str(e)}"

    def crear(self, datos):
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
            new_id = self._repo.create(datos)
            # invalidar cache del catalogo modificado
            self._invalidate_cache()
            return new_id, None
        except Exception as e:
            return None, f"Error al crear: {str(e)}"

    def actualizar(self, id_value, datos):
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
            self._repo.update(id_value, datos)
            # invalidar cache del catalogo modificado
            self._invalidate_cache()
            return True, None
        except Exception as e:
            return None, f"Error al actualizar: {str(e)}"

    def eliminar(self, id_value):
        # verificar referencias antes de eliminar
        refs = self._repo.count_references(id_value)
        if refs > 0:
            return None, f"No se puede eliminar. Este registro es utilizado por {refs} registro(s) en el sistema."

        ok, error = self._repo.delete(id_value)
        if not ok:
            return None, error
        # invalidar cache del catalogo modificado
        self._invalidate_cache()
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
