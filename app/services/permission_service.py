# Servicio de permisos por rol - define qué secciones puede ver cada rol

PERMISOS_POR_ROL = {
    1: {  # Administrador - acceso total
        "dashboard", "clientes", "ventas", "actividades", "segmentacion",
        "comunicacion", "reportes", "notificaciones", "usuarios", "configuracion",
    },
    2: {  # Gerente de Ventas
        "dashboard", "clientes", "ventas", "actividades", "segmentacion",
        "comunicacion", "reportes", "notificaciones",
    },
    3: {  # Vendedor
        "dashboard", "clientes", "ventas", "actividades", "notificaciones",
    },
    4: {  # Marketing
        "dashboard", "clientes", "comunicacion", "segmentacion", "reportes",
        "notificaciones",
    },
}


def tiene_acceso(usuario, seccion: str) -> bool:
    """Retorna True si el usuario tiene permiso para acceder a la sección indicada."""
    permisos = PERMISOS_POR_ROL.get(usuario.rol_id, set())
    return seccion in permisos
