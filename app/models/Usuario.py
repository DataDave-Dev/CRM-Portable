# Modelo de Usuario - representa un registro de la tabla Usuarios

from datetime import datetime


class Usuario:
    def __init__(
        self,
        usuario_id=None,
        nombre="",
        apellido_paterno="",
        apellido_materno=None,
        email="",
        telefono=None,
        contrasena_hash="",
        rol_id=1,
        activo=1,
        foto_perfil=None,
        fecha_creacion=None,
        ultimo_acceso=None
    ):
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.telefono = telefono
        self.contrasena_hash = contrasena_hash
        self.rol_id = rol_id
        self.activo = activo
        self.foto_perfil = foto_perfil
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ultimo_acceso = ultimo_acceso

    def __repr__(self):
        return f"<Usuario(id={self.usuario_id}, email='{self.email}')>"