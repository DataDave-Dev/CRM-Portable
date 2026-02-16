# Modelo de Contacto - representa un registro de la tabla Contactos

from datetime import datetime


class Contacto:
    def __init__(
        self,
        contacto_id=None,
        nombre="",
        apellido_paterno="",
        apellido_materno=None,
        email=None,
        email_secundario=None,
        telefono_oficina=None,
        telefono_celular=None,
        puesto=None,
        departamento=None,
        empresa_id=None,
        direccion=None,
        ciudad_id=None,
        codigo_postal=None,
        fecha_nacimiento=None,
        linkedin_url=None,
        origen_id=None,
        propietario_id=None,
        es_contacto_principal=0,
        no_contactar=0,
        activo=1,
        foto_url=None,
        fecha_creacion=None,
        fecha_modificacion=None,
        creado_por=None,
        modificado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_empresa=None,
        nombre_ciudad=None,
        nombre_origen=None,
        nombre_propietario=None,
    ):
        self.contacto_id = contacto_id
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.email_secundario = email_secundario
        self.telefono_oficina = telefono_oficina
        self.telefono_celular = telefono_celular
        self.puesto = puesto
        self.departamento = departamento
        self.empresa_id = empresa_id
        self.direccion = direccion
        self.ciudad_id = ciudad_id
        self.codigo_postal = codigo_postal
        self.fecha_nacimiento = fecha_nacimiento
        self.linkedin_url = linkedin_url
        self.origen_id = origen_id
        self.propietario_id = propietario_id
        self.es_contacto_principal = es_contacto_principal
        self.no_contactar = no_contactar
        self.activo = activo
        self.foto_url = foto_url
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.creado_por = creado_por
        self.modificado_por = modificado_por
        self.nombre_empresa = nombre_empresa
        self.nombre_ciudad = nombre_ciudad
        self.nombre_origen = nombre_origen
        self.nombre_propietario = nombre_propietario

    def __repr__(self):
        return f"<Contacto(id={self.contacto_id}, nombre='{self.nombre} {self.apellido_paterno}')>"
