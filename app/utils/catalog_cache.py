# Sistema de cache en memoria para catalogos - mejora rendimiento en carga de formularios

import time
from typing import Dict, List, Tuple, Optional
from app.database.connection import get_connection


class CatalogCache:
    # cache compartido entre todas las instancias
    _cache: Dict[str, List[Tuple]] = {}
    _cache_time: Dict[str, float] = {}
    _ttl_seconds = 300  # 5 minutos de vigencia del cache

    @classmethod
    def get_industrias(cls) -> List[Tuple[int, str]]:
        # obtiene lista de industrias para ComboBox
        return cls._get_catalog('industrias', 'Industrias', 'IndustriaID', 'Nombre')

    @classmethod
    def get_tamanos_empresa(cls) -> List[Tuple[int, str]]:
        # obtiene lista de tamanos de empresa para ComboBox
        return cls._get_catalog('tamanos', 'TamanosEmpresa', 'TamanoID', 'Nombre')

    @classmethod
    def get_origenes_contacto(cls) -> List[Tuple[int, str]]:
        # obtiene lista de origenes de contacto para ComboBox
        return cls._get_catalog('origenes', 'OrigenesContacto', 'OrigenID', 'Nombre')

    @classmethod
    def get_monedas(cls) -> List[Tuple[int, str]]:
        # obtiene lista de monedas para ComboBox
        return cls._get_catalog('monedas', 'Monedas', 'MonedaID', 'Nombre')

    @classmethod
    def get_paises(cls) -> List[Tuple[int, str]]:
        # obtiene lista de paises para ComboBox
        return cls._get_catalog('paises', 'Paises', 'PaisID', 'Nombre')

    @classmethod
    def get_estados(cls, pais_id: Optional[int] = None) -> List[Tuple[int, str]]:
        # obtiene lista de estados para ComboBox, opcionalmente filtrados por pais
        if pais_id:
            cache_key = f'estados_pais_{pais_id}'
            return cls._get_catalog(
                cache_key, 'Estados', 'EstadoID', 'Nombre',
                where_clause=f'PaisID = {pais_id}'
            )
        return cls._get_catalog('estados', 'Estados', 'EstadoID', 'Nombre')

    @classmethod
    def get_ciudades(cls, estado_id: Optional[int] = None) -> List[Tuple[int, str]]:
        # obtiene lista de ciudades para ComboBox, opcionalmente filtradas por estado
        if estado_id:
            cache_key = f'ciudades_estado_{estado_id}'
            return cls._get_catalog(
                cache_key, 'Ciudades', 'CiudadID', 'Nombre',
                where_clause=f'EstadoID = {estado_id}'
            )
        return cls._get_catalog('ciudades', 'Ciudades', 'CiudadID', 'Nombre')

    @classmethod
    def get_usuarios(cls) -> List[Tuple[int, str]]:
        # obtiene lista de usuarios activos para ComboBox
        return cls._get_catalog(
            'usuarios', 'Usuarios', 'UsuarioID',
            'Nombre || " " || ApellidoPaterno',
            where_clause='Activo = 1'
        )

    @classmethod
    def get_etapas_venta(cls) -> List[Tuple[int, str]]:
        # obtiene lista de etapas de venta para ComboBox, ordenadas por Orden
        if cls._is_cache_valid('etapas_venta'):
            return cls._cache['etapas_venta']
        conn = get_connection()
        cursor = conn.execute('SELECT EtapaID, Nombre FROM EtapasVenta ORDER BY Orden, Nombre')
        result = [(row[0], row[1]) for row in cursor.fetchall()]
        cls._cache['etapas_venta'] = result
        cls._cache_time['etapas_venta'] = time.time()
        return result

    @classmethod
    def get_motivos_perdida(cls) -> List[Tuple[int, str]]:
        # obtiene lista de motivos de perdida para ComboBox
        return cls._get_catalog('motivos_perdida', 'MotivosPerdida', 'MotivoID', 'Nombre')

    @classmethod
    def get_tipos_actividad(cls) -> List[Tuple[int, str]]:
        # obtiene lista de tipos de actividad para ComboBox
        return cls._get_catalog('tipos_actividad', 'TiposActividad', 'TipoActividadID', 'Nombre')

    @classmethod
    def get_estados_actividad(cls) -> List[Tuple[int, str]]:
        # obtiene lista de estados de actividad para ComboBox
        return cls._get_catalog('estados_actividad', 'EstadosActividad', 'EstadoActividadID', 'Nombre')

    @classmethod
    def get_prioridades(cls) -> List[Tuple[int, str]]:
        # obtiene lista de prioridades para ComboBox, ordenadas por nivel
        if cls._is_cache_valid('prioridades'):
            return cls._cache['prioridades']
        conn = get_connection()
        cursor = conn.execute('SELECT PrioridadID, Nombre FROM Prioridades ORDER BY Nivel')
        result = [(row[0], row[1]) for row in cursor.fetchall()]
        cls._cache['prioridades'] = result
        cls._cache_time['prioridades'] = time.time()
        return result

    @classmethod
    def _get_catalog(
        cls,
        cache_key: str,
        table: str,
        id_column: str,
        display_column: str,
        where_clause: str = ''
    ) -> List[Tuple[int, str]]:
        # metodo generico para obtener catalogo con cache
        if cls._is_cache_valid(cache_key):
            return cls._cache[cache_key]

        # cache invalido o no existe - consultar base de datos
        conn = get_connection()
        query = f'SELECT {id_column}, {display_column} FROM {table}'
        if where_clause:
            query += f' WHERE {where_clause}'
        query += f' ORDER BY {display_column}'

        cursor = conn.execute(query)
        result = [(row[0], row[1]) for row in cursor.fetchall()]

        # guardar en cache
        cls._cache[cache_key] = result
        cls._cache_time[cache_key] = time.time()

        return result

    @classmethod
    def invalidate(cls, catalog_name: str):
        # invalida cache de un catalogo especifico cuando se modifica
        if catalog_name in cls._cache:
            del cls._cache[catalog_name]
            del cls._cache_time[catalog_name]

    @classmethod
    def invalidate_all(cls):
        # invalida todo el cache
        cls._cache.clear()
        cls._cache_time.clear()

    @classmethod
    def _is_cache_valid(cls, cache_key: str) -> bool:
        # verifica si cache esta vigente
        if cache_key not in cls._cache:
            return False

        age = time.time() - cls._cache_time.get(cache_key, 0)
        return age < cls._ttl_seconds

    @classmethod
    def set_ttl(cls, seconds: int):
        # permite configurar el tiempo de vida del cache
        cls._ttl_seconds = seconds
