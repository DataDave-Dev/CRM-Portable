"""
Sistema de cache en memoria para catalogos del CRM.

Problema que resuelve:
    Los formularios de la aplicacion (nuevo contacto, nueva empresa, etc.) necesitan
    llenar ComboBoxes con listas de valores: industrias, ciudades, origenes, etapas
    de venta, etc. Sin cache, cada vez que el usuario abre un formulario se hacen
    varias consultas SQL a la BD, lo que puede causar un retardo visible.

    Con CatalogCache, los datos se cargan una vez de la BD y se guardan en memoria.
    Las siguientes aperturas del formulario leen del cache sin tocar la BD, haciendo
    la interfaz mas rapida y fluida.

Patron usado: Cache de clase compartida (Class-level cache)
    Los atributos _cache y _cache_time son de CLASE, no de instancia. Esto significa
    que son compartidos por todos los usos de CatalogCache en toda la aplicacion,
    como si fuera un singleton. No es necesario instanciar la clase; todos los
    metodos son @classmethod.

TTL (Time To Live):
    El cache tiene una vigencia de 5 minutos (300 segundos). Despues de ese tiempo
    se considera expirado y la siguiente consulta volvera a leer de la BD.
    Esto garantiza que si un administrador agrega una nueva industria, los
    formularios la veran en menos de 5 minutos sin necesidad de reiniciar la app.

    Para cambios inmediatos, llamar CatalogCache.invalidate('nombre_catalogo') o
    CatalogCache.invalidate_all() despues de guardar en la BD.

Como usar este modulo en formularios (vistas):
    from app.utils.catalog_cache import CatalogCache

    # Obtener lista de industrias para llenar un ComboBox
    industrias = CatalogCache.get_industrias()
    # industrias es una lista de tuplas: [(1, "Tecnologia"), (2, "Salud"), ...]
    for id_industria, nombre in industrias:
        self.combo_industria.addItem(nombre, id_industria)

    # Cuando el usuario guarda y agrega una nueva industria, invalidar el cache:
    CatalogCache.invalidate('industrias')
"""

import time
from typing import Dict, List, Tuple, Optional
from app.database.connection import get_connection


class CatalogCache:
    """
    Cache en memoria para listas de valores usados en ComboBoxes de la interfaz.

    Todos los metodos son de clase (@classmethod), por lo que se llaman directamente
    sobre la clase sin necesitar crear una instancia:
        datos = CatalogCache.get_industrias()  # correcto
        cache = CatalogCache()
        datos = cache.get_industrias()          # tambien funciona, pero innecesario

    Atributos de clase:
        _cache      : Diccionario {clave: lista_de_tuplas}. Almacena los datos en memoria.
        _cache_time : Diccionario {clave: timestamp}. Guarda cuando se cargo cada catalogo.
        _ttl_seconds: Segundos de vigencia del cache. Por defecto 300 (5 minutos).
    """

    # Diccionario principal del cache. Clave: nombre del catalogo. Valor: lista de tuplas (id, nombre).
    _cache: Dict[str, List[Tuple]] = {}

    # Timestamps de cuando se cargo cada catalogo. Usado para calcular si el cache expiro.
    _cache_time: Dict[str, float] = {}

    # Tiempo de vida del cache en segundos. Despues de este tiempo, la BD se vuelve a consultar.
    _ttl_seconds = 300  # 5 minutos

    # -------------------------------------------------------------------------
    # Metodos publicos para obtener cada catalogo
    # -------------------------------------------------------------------------
    # Todos retornan List[Tuple[int, str]] = lista de (ID, Nombre)
    # El primer elemento es el ID numerico de la BD (para FK).
    # El segundo elemento es el nombre para mostrar en la interfaz.

    @classmethod
    def get_industrias(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de industrias [(id, nombre), ...] para ComboBox."""
        return cls._get_catalog('industrias', 'Industrias', 'IndustriaID', 'Nombre')

    @classmethod
    def get_tamanos_empresa(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de tamanos de empresa [(id, nombre), ...] para ComboBox."""
        return cls._get_catalog('tamanos', 'TamanosEmpresa', 'TamanoID', 'Nombre')

    @classmethod
    def get_origenes_contacto(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de origenes de contacto/empresa [(id, nombre), ...] para ComboBox."""
        return cls._get_catalog('origenes', 'OrigenesContacto', 'OrigenID', 'Nombre')

    @classmethod
    def get_monedas(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de monedas [(id, nombre), ...] para ComboBox."""
        return cls._get_catalog('monedas', 'Monedas', 'MonedaID', 'Nombre')

    @classmethod
    def get_paises(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de paises [(id, nombre), ...] para ComboBox."""
        return cls._get_catalog('paises', 'Paises', 'PaisID', 'Nombre')

    @classmethod
    def get_estados(cls, pais_id: Optional[int] = None) -> List[Tuple[int, str]]:
        """
        Retorna la lista de estados/provincias para ComboBox.

        Soporte de cascada: si se proporciona pais_id, retorna solo los estados
        de ese pais. Esto se usa para el selector geografico en cadena:
        seleccionar pais -> filtrar estados -> filtrar ciudades.

        Parametros:
            pais_id: ID del pais para filtrar. Si es None, retorna todos los estados.
        """
        if pais_id:
            # Cache separado por pais para no mezclar resultados
            cache_key = f'estados_pais_{pais_id}'
            return cls._get_catalog(
                cache_key, 'Estados', 'EstadoID', 'Nombre',
                where_clause=f'PaisID = {pais_id}'
            )
        # Sin filtro: retornar todos los estados (todos los paises)
        return cls._get_catalog('estados', 'Estados', 'EstadoID', 'Nombre')

    @classmethod
    def get_ciudades(cls, estado_id: Optional[int] = None) -> List[Tuple[int, str]]:
        """
        Retorna la lista de ciudades para ComboBox.

        Soporte de cascada: si se proporciona estado_id, retorna solo las ciudades
        de ese estado. Parte del selector geografico en cadena (pais > estado > ciudad).

        Parametros:
            estado_id: ID del estado para filtrar. Si es None, retorna todas las ciudades.
        """
        if estado_id:
            # Cache separado por estado para no mezclar ciudades de diferentes estados
            cache_key = f'ciudades_estado_{estado_id}'
            return cls._get_catalog(
                cache_key, 'Ciudades', 'CiudadID', 'Nombre',
                where_clause=f'EstadoID = {estado_id}'
            )
        # Sin filtro: retornar todas las ciudades (todos los estados/paises)
        return cls._get_catalog('ciudades', 'Ciudades', 'CiudadID', 'Nombre')

    @classmethod
    def get_usuarios(cls) -> List[Tuple[int, str]]:
        """
        Retorna la lista de usuarios ACTIVOS para ComboBox (campo Propietario).

        Solo incluye usuarios con Activo = 1 para no mostrar cuentas desactivadas
        en los campos de asignacion de oportunidades, actividades, etc.
        El nombre mostrado es 'Nombre Apellido' (concatenacion SQL).
        """
        return cls._get_catalog(
            'usuarios', 'Usuarios', 'UsuarioID',
            'Nombre || " " || ApellidoPaterno',  # concatenar nombre y apellido en SQL
            where_clause='Activo = 1'            # solo usuarios activos en el sistema
        )

    @classmethod
    def get_etapas_venta(cls) -> List[Tuple[int, str]]:
        """
        Retorna la lista de etapas de venta ordenadas por su campo Orden.

        Las etapas de venta tienen un orden especifico (ej: Prospecto=1, Demo=2,
        Propuesta=3, Negociacion=4, Cerrada=5). Se usa ORDER BY Orden para que
        el ComboBox las muestre en el orden del pipeline de ventas.

        Nota: Este metodo no usa _get_catalog() porque necesita un ORDER BY especial
        (por Orden, no por Nombre como hace el metodo generico).
        """
        # Verificar si el cache es valido antes de consultar la BD
        if cls._is_cache_valid('etapas_venta'):
            return cls._cache['etapas_venta']
        conn = get_connection()
        # ORDER BY Orden, Nombre: primero por orden numerico, luego alfabetico como tiebreaker
        cursor = conn.execute('SELECT EtapaID, Nombre FROM EtapasVenta ORDER BY Orden, Nombre')
        result = [(row[0], row[1]) for row in cursor.fetchall()]
        # Guardar en cache para reutilizar
        cls._cache['etapas_venta'] = result
        cls._cache_time['etapas_venta'] = time.time()
        return result

    @classmethod
    def get_motivos_perdida(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de motivos de perdida de oportunidades para ComboBox."""
        return cls._get_catalog('motivos_perdida', 'MotivosPerdida', 'MotivoID', 'Nombre')

    @classmethod
    def get_tipos_actividad(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de tipos de actividad (Llamada, Reunion, Tarea...) para ComboBox."""
        return cls._get_catalog('tipos_actividad', 'TiposActividad', 'TipoActividadID', 'Nombre')

    @classmethod
    def get_estados_actividad(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de estados de actividad (Pendiente, En progreso, Completada...) para ComboBox."""
        return cls._get_catalog('estados_actividad', 'EstadosActividad', 'EstadoActividadID', 'Nombre')

    @classmethod
    def get_etiquetas(cls) -> List[Tuple[int, str]]:
        """Retorna la lista de etiquetas/tags disponibles para asignar a contactos y empresas."""
        return cls._get_catalog('etiquetas', 'Etiquetas', 'EtiquetaID', 'Nombre')

    @classmethod
    def get_prioridades(cls) -> List[Tuple[int, str]]:
        """
        Retorna la lista de prioridades ordenadas por nivel numerico.

        Las prioridades tienen un nivel numerico (ej: Alta=1, Media=2, Baja=3).
        Se ordena por Nivel para que el ComboBox las muestre de mayor a menor prioridad.

        Nota: No usa _get_catalog() porque necesita ORDER BY Nivel, no por Nombre.
        """
        if cls._is_cache_valid('prioridades'):
            return cls._cache['prioridades']
        conn = get_connection()
        cursor = conn.execute('SELECT PrioridadID, Nombre FROM Prioridades ORDER BY Nivel')
        result = [(row[0], row[1]) for row in cursor.fetchall()]
        cls._cache['prioridades'] = result
        cls._cache_time['prioridades'] = time.time()
        return result

    # -------------------------------------------------------------------------
    # Metodo generico privado
    # -------------------------------------------------------------------------

    @classmethod
    def _get_catalog(
        cls,
        cache_key: str,
        table: str,
        id_column: str,
        display_column: str,
        where_clause: str = ''
    ) -> List[Tuple[int, str]]:
        """
        Metodo generico para obtener cualquier catalogo con soporte de cache.

        Construye y ejecuta una consulta SELECT dinamica con los parametros dados.
        Si el cache es valido, lo retorna sin tocar la BD.
        Si el cache expirou o no existe, consulta la BD y guarda el resultado.

        Parametros:
            cache_key      : Clave unica para identificar este catalogo en el cache.
                             Debe ser unica por catalogo/filtro para evitar colisiones.
            table          : Nombre de la tabla en SQLite (ej. 'Industrias').
            id_column      : Columna que contiene el ID numerico (ej. 'IndustriaID').
            display_column : Columna a mostrar en la UI (ej. 'Nombre'), o expresion SQL.
            where_clause   : Condicion WHERE opcional (sin el WHERE). Ej: 'Activo = 1'.

        Returns:
            List[Tuple[int, str]]: Lista de (id, nombre) lista para llenar un ComboBox.
        """
        # Si el cache es valido (existe y no ha expirado), retornarlo directamente
        if cls._is_cache_valid(cache_key):
            return cls._cache[cache_key]

        # Cache invalido o no existe: consultar la base de datos
        conn = get_connection()

        # Construir la query dinamicamente con los parametros
        query = f'SELECT {id_column}, {display_column} FROM {table}'
        if where_clause:
            query += f' WHERE {where_clause}'
        query += f' ORDER BY {display_column}'  # siempre ordenar por nombre para consistencia

        cursor = conn.execute(query)
        # Convertir cada Row de SQLite a una tupla (id, nombre) simple
        result = [(row[0], row[1]) for row in cursor.fetchall()]

        # Guardar en cache con timestamp actual
        cls._cache[cache_key] = result
        cls._cache_time[cache_key] = time.time()

        return result

    # -------------------------------------------------------------------------
    # Metodos de gestion del cache
    # -------------------------------------------------------------------------

    @classmethod
    def invalidate(cls, catalog_name: str):
        """
        Invalida el cache de un catalogo especifico.

        Llamar este metodo despues de crear, editar o eliminar un registro
        de un catalogo para que la proxima consulta obtenga datos actualizados de la BD.

        Parametros:
            catalog_name: La misma clave que se usa internamente (ej: 'industrias',
                          'origenes', 'etapas_venta', 'ciudades_estado_5').
        """
        if catalog_name in cls._cache:
            del cls._cache[catalog_name]
            del cls._cache_time[catalog_name]

    @classmethod
    def invalidate_all(cls):
        """
        Invalida TODO el cache de todos los catalogos.

        Util despues de importar datos masivos o cuando se hacen cambios
        en multiples catalogos al mismo tiempo.
        """
        cls._cache.clear()
        cls._cache_time.clear()

    @classmethod
    def _is_cache_valid(cls, cache_key: str) -> bool:
        """
        Verifica si el cache de un catalogo especifico esta vigente.

        El cache es valido si:
        1. Existe una entrada para esa clave en _cache.
        2. La edad del cache (tiempo actual - timestamp de carga) es menor que _ttl_seconds.

        Parametros:
            cache_key: Clave del catalogo a verificar.

        Returns:
            bool: True si el cache existe y no ha expirado. False en caso contrario.
        """
        # Si la clave no existe en el cache, definitivamente no es valido
        if cache_key not in cls._cache:
            return False

        # Calcular cuantos segundos han pasado desde que se cargo el cache
        age = time.time() - cls._cache_time.get(cache_key, 0)
        # El cache es valido solo si su edad es menor que el TTL configurado
        return age < cls._ttl_seconds

    @classmethod
    def set_ttl(cls, seconds: int):
        """
        Configura el tiempo de vida (TTL) del cache en segundos.

        Util para pruebas (set_ttl(0) para forzar siempre consultar la BD)
        o para entornos donde los datos cambian con frecuencia.

        Parametros:
            seconds: Nuevos segundos de vigencia. 0 = sin cache (siempre va a BD).
        """
        cls._ttl_seconds = seconds
