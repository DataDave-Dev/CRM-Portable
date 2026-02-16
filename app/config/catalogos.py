# Configuración centralizada de todos los catálogos del sistema
# Cada catálogo define su tabla, columnas, validaciones y relaciones

CATALOGO_CONFIGS = {
    # --- Ventas ---
    'etapas_venta': {
        'table': 'EtapasVenta',
        'id_column': 'EtapaID',
        'display_name': 'Etapas de Venta',
        'display_name_singular': 'Etapa de Venta',
        'category': 'Ventas',
        'ui_list': 'catalogos/ventas/etapas_venta_list.ui',
        'ui_form': 'catalogos/ventas/etapas_venta_form.ui',
        'tab_layout': 'tabEtapasVentaLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Orden', 'label': 'Orden', 'required': True, 'type': 'int'},
            {'name': 'Probabilidad', 'label': 'Probabilidad (%)', 'required': False, 'type': 'float'},
            {'name': 'Color', 'label': 'Color', 'required': False, 'type': 'color'},
            {'name': 'Descripcion', 'label': 'Descripción', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Orden',
        'referenced_by': [
            {'table': 'Oportunidades', 'column': 'EtapaID'},
        ],
    },
    'motivos_perdida': {
        'table': 'MotivosPerdida',
        'id_column': 'MotivoID',
        'display_name': 'Motivos de Pérdida',
        'display_name_singular': 'Motivo de Pérdida',
        'category': 'Ventas',
        'ui_list': 'catalogos/ventas/motivos_perdida_list.ui',
        'ui_form': 'catalogos/ventas/motivos_perdida_form.ui',
        'tab_layout': 'tabMotivosPerdidaLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Descripcion', 'label': 'Descripción', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Oportunidades', 'column': 'MotivosPerdidaID'},
        ],
    },

    # --- Actividades ---
    'tipos_actividad': {
        'table': 'TiposActividad',
        'id_column': 'TipoActividadID',
        'display_name': 'Tipos de Actividad',
        'display_name_singular': 'Tipo de Actividad',
        'category': 'Actividades',
        'ui_list': 'catalogos/actividades/tipos_actividad_list.ui',
        'ui_form': 'catalogos/actividades/tipos_actividad_form.ui',
        'tab_layout': 'tabTiposActividadLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Icono', 'label': 'Icono', 'required': False, 'type': 'text'},
            {'name': 'Color', 'label': 'Color', 'required': False, 'type': 'color'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Actividades', 'column': 'TipoActividadID'},
        ],
    },
    'prioridades': {
        'table': 'Prioridades',
        'id_column': 'PrioridadID',
        'display_name': 'Prioridades',
        'display_name_singular': 'Prioridad',
        'category': 'Actividades',
        'ui_list': 'catalogos/actividades/prioridades_list.ui',
        'ui_form': 'catalogos/actividades/prioridades_form.ui',
        'tab_layout': 'tabPrioridadesLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Nivel', 'label': 'Nivel', 'required': True, 'type': 'int'},
            {'name': 'Color', 'label': 'Color', 'required': False, 'type': 'color'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nivel',
        'referenced_by': [
            {'table': 'Actividades', 'column': 'PrioridadID'},
        ],
    },
    'estados_actividad': {
        'table': 'EstadosActividad',
        'id_column': 'EstadoActividadID',
        'display_name': 'Estados de Actividad',
        'display_name_singular': 'Estado de Actividad',
        'category': 'Actividades',
        'ui_list': 'catalogos/actividades/estados_actividad_list.ui',
        'ui_form': 'catalogos/actividades/estados_actividad_form.ui',
        'tab_layout': 'tabEstadosActividadLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Actividades', 'column': 'EstadoActividadID'},
        ],
    },

    # --- Contactos ---
    'industrias': {
        'table': 'Industrias',
        'id_column': 'IndustriaID',
        'display_name': 'Industrias',
        'display_name_singular': 'Industria',
        'category': 'Contactos',
        'ui_list': 'catalogos/empresas/industrias_list.ui',
        'ui_form': 'catalogos/empresas/industrias_form.ui',
        'tab_layout': 'tabIndustriasLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Descripcion', 'label': 'Descripción', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Empresas', 'column': 'IndustriaID'},
        ],
    },
    'tamanos_empresa': {
        'table': 'TamanosEmpresa',
        'id_column': 'TamanoID',
        'display_name': 'Tamaños de Empresa',
        'display_name_singular': 'Tamaño de Empresa',
        'category': 'Contactos',
        'ui_list': 'catalogos/empresas/tamanos_empresa_list.ui',
        'ui_form': 'catalogos/empresas/tamanos_empresa_form.ui',
        'tab_layout': 'tabTamanosEmpresaLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'RangoEmpleados', 'label': 'Rango de Empleados', 'required': False, 'type': 'text'},
            {'name': 'Descripcion', 'label': 'Descripción', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Empresas', 'column': 'TamanoID'},
        ],
    },
    'origenes_contacto': {
        'table': 'OrigenesContacto',
        'id_column': 'OrigenID',
        'display_name': 'Orígenes de Contacto',
        'display_name_singular': 'Origen de Contacto',
        'category': 'Contactos',
        'ui_list': 'catalogos/empresas/origenes_contacto_list.ui',
        'ui_form': 'catalogos/empresas/origenes_contacto_form.ui',
        'tab_layout': 'tabOrigenesContactoLayout',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Descripcion', 'label': 'Descripción', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Contactos', 'column': 'OrigenID'},
            {'table': 'Empresas', 'column': 'OrigenID'},
            {'table': 'Oportunidades', 'column': 'OrigenID'},
        ],
    },

    # --- Finanzas ---
    'monedas': {
        'table': 'Monedas',
        'id_column': 'MonedaID',
        'display_name': 'Monedas',
        'display_name_singular': 'Moneda',
        'category': 'Finanzas',
        'ui_list': 'catalogos/sistema/monedas_list.ui',
        'ui_form': 'catalogos/sistema/monedas_form.ui',
        'tab_layout': 'tabMonedasLayout',
        'columns': [
            {'name': 'Codigo', 'label': 'Código', 'required': True, 'type': 'text'},
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'Simbolo', 'label': 'Símbolo', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Codigo',
        'order_by': 'Codigo',
        'referenced_by': [
            {'table': 'Empresas', 'column': 'MonedaID'},
            {'table': 'Oportunidades', 'column': 'MonedaID'},
            {'table': 'Productos', 'column': 'MonedaID'},
        ],
    },
}

# Configuración separada para catálogos geográficos (cascada)
GEOGRAFIA_CONFIGS = {
    'paises': {
        'table': 'Paises',
        'id_column': 'PaisID',
        'display_name': 'Países',
        'display_name_singular': 'País',
        'ui_form': 'geografia/paises_form.ui',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
            {'name': 'CodigoISO', 'label': 'Código ISO', 'required': False, 'type': 'text'},
        ],
        'unique_column': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Estados', 'column': 'PaisID'},
        ],
    },
    'estados': {
        'table': 'Estados',
        'id_column': 'EstadoID',
        'display_name': 'Estados',
        'display_name_singular': 'Estado',
        'ui_form': 'geografia/estados_geo_form.ui',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
        ],
        'fk_column': 'PaisID',
        'fk_parent_table': 'Paises',
        'fk_parent_id': 'PaisID',
        'fk_parent_display': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Ciudades', 'column': 'EstadoID'},
        ],
    },
    'ciudades': {
        'table': 'Ciudades',
        'id_column': 'CiudadID',
        'display_name': 'Ciudades',
        'display_name_singular': 'Ciudad',
        'ui_form': 'geografia/ciudades_form.ui',
        'columns': [
            {'name': 'Nombre', 'label': 'Nombre', 'required': True, 'type': 'text'},
        ],
        'fk_column': 'EstadoID',
        'fk_parent_table': 'Estados',
        'fk_parent_id': 'EstadoID',
        'fk_parent_display': 'Nombre',
        'order_by': 'Nombre',
        'referenced_by': [
            {'table': 'Contactos', 'column': 'CiudadID'},
            {'table': 'Empresas', 'column': 'CiudadID'},
        ],
    },
}

# Orden de categorías para los tabs principales
CATEGORIAS_ORDEN = [
    'Ventas',
    'Actividades',
    'Contactos',
    'Finanzas',
    'Geografía',
]
