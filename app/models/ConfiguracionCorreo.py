# Modelo de ConfiguracionCorreo - representa un registro de la tabla ConfiguracionCorreo

from datetime import datetime


class ConfiguracionCorreo:
    def __init__(
        self,
        config_id=None,
        nombre="",
        proveedor="SMTP",
        host=None,
        puerto=587,
        usar_tls=1,
        usar_ssl=0,
        email_remitente="",
        nombre_remitente=None,
        usuario=None,
        contrasena=None,
        api_key=None,
        activa=0,
        notas=None,
        fecha_creacion=None,
        fecha_modificacion=None,
    ):
        self.config_id = config_id
        self.nombre = nombre
        self.proveedor = proveedor
        self.host = host
        self.puerto = puerto
        self.usar_tls = usar_tls
        self.usar_ssl = usar_ssl
        self.email_remitente = email_remitente
        self.nombre_remitente = nombre_remitente
        self.usuario = usuario
        self.contrasena = contrasena
        self.api_key = api_key
        self.activa = activa
        self.notas = notas
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion

    def __repr__(self):
        return f"<ConfiguracionCorreo(id={self.config_id}, nombre='{self.nombre}', proveedor='{self.proveedor}')>"
