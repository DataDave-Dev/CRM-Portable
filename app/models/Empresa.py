# Modelo de Empresa - representa un registro de la tabla Empresas

from datetime import datetime


class Empresa:
    def __init__(
        self,
        empresa_id=None,
        razon_social="",
        nombre_comercial=None,
        rfc=None,
        industria_id=None,
        tamano_id=None,
        sitio_web=None,
        telefono=None,
        email=None,
        direccion=None,
        ciudad_id=None,
        codigo_postal=None,
        ingreso_anual_estimado=None,
        moneda_id=None,
        num_empleados=None,
        descripcion=None,
        logo_url=None,
        origen_id=None,
        propietario_id=None,
        activo=1,
        fecha_creacion=None,
        fecha_modificacion=None,
        creado_por=None,
        modificado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_industria=None,
        nombre_tamano=None,
        nombre_ciudad=None,
        nombre_moneda=None,
        nombre_origen=None,
        nombre_propietario=None,
    ):
        self.empresa_id = empresa_id
        self.razon_social = razon_social
        self.nombre_comercial = nombre_comercial
        self.rfc = rfc
        self.industria_id = industria_id
        self.tamano_id = tamano_id
        self.sitio_web = sitio_web
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.ciudad_id = ciudad_id
        self.codigo_postal = codigo_postal
        self.ingreso_anual_estimado = ingreso_anual_estimado
        self.moneda_id = moneda_id
        self.num_empleados = num_empleados
        self.descripcion = descripcion
        self.logo_url = logo_url
        self.origen_id = origen_id
        self.propietario_id = propietario_id
        self.activo = activo
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.creado_por = creado_por
        self.modificado_por = modificado_por
        self.nombre_industria = nombre_industria
        self.nombre_tamano = nombre_tamano
        self.nombre_ciudad = nombre_ciudad
        self.nombre_moneda = nombre_moneda
        self.nombre_origen = nombre_origen
        self.nombre_propietario = nombre_propietario

    def __repr__(self):
        return f"<Empresa(id={self.empresa_id}, razon_social='{self.razon_social}')>"
