# Logica de negocio para gestionar usuarios

import bcrypt
import re
from app.repositories.usuario_repository import UsuarioRepository
from app.models.Usuario import Usuario


class UsuarioService:
    def __init__(self):
        self._repo = UsuarioRepository()

    def crear_usuario(self, datos_usuario):
        # validar que los campos requeridos estén presentes
        campos_requeridos = ["nombre", "apellido_paterno", "email", "contrasena", "rol_id"]
        for campo in campos_requeridos:
            valor = datos_usuario.get(campo)
            if valor is None:
                return None, f"El campo {campo.replace('_', ' ')} es requerido"
            if isinstance(valor, str) and valor.strip() == "":
                return None, f"El campo {campo.replace('_', ' ')} es requerido"

        # validar formato de email usando una expresión regular simple
        email = datos_usuario["email"].strip()
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, email):
            return None, "El formato del email no es válido"

        # verificar que el email no esté registrado previamente
        if self._repo.email_exists(email):
            return None, "Este email ya está registrado"

        # validar longitud mínima de contraseña
        contrasena = datos_usuario["contrasena"]
        if len(contrasena) < 8:
            return None, "La contraseña debe tener al menos 8 caracteres"

        # validar formato de teléfono si se proporciona
        telefono = datos_usuario.get("telefono", "").strip()
        if telefono:
            if not telefono.isdigit() or len(telefono) != 10:
                return None, "El teléfono debe contener exactamente 10 dígitos"

        # hashear la contraseña con bcrypt antes de guardarla
        contrasena_hash = bcrypt.hashpw(
            contrasena.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # crear el objeto Usuario con los datos validados
        nuevo_usuario = Usuario(
            nombre=datos_usuario["nombre"].strip(),
            apellido_paterno=datos_usuario["apellido_paterno"].strip(),
            apellido_materno=datos_usuario.get("apellido_materno", "").strip() or None,
            email=email,
            telefono=telefono or None,
            contrasena_hash=contrasena_hash,
            rol_id=datos_usuario["rol_id"],
            activo=datos_usuario.get("activo", 1),
            foto_perfil=datos_usuario.get("foto_perfil"),
        )

        # guardar el usuario en la base de datos
        try:
            usuario_id = self._repo.create(nuevo_usuario)
            nuevo_usuario.usuario_id = usuario_id
            return nuevo_usuario, None
        except Exception as e:
            return None, f"Error al crear usuario: {str(e)}"

    def actualizar_usuario(self, usuario_id, datos_usuario):
        # validar campos requeridos
        campos_requeridos = ["nombre", "apellido_paterno", "email", "rol_id"]
        for campo in campos_requeridos:
            valor = datos_usuario.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                return None, f"El campo {campo.replace('_', ' ')} es requerido"

        # validar formato de email
        email = datos_usuario["email"].strip()
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, email):
            return None, "El formato del email no es válido"

        # verificar que el email no esté en uso por otro usuario
        if self._repo.email_exists(email, excluir_id=usuario_id):
            return None, "Este email ya está registrado por otro usuario"

        # validar teléfono si se proporciona
        telefono = datos_usuario.get("telefono", "").strip()
        if telefono:
            if not telefono.isdigit() or len(telefono) != 10:
                return None, "El teléfono debe contener exactamente 10 dígitos"

        # actualizar contraseña solo si se proporcionó una nueva
        contrasena = datos_usuario.get("contrasena", "")
        if contrasena:
            if len(contrasena) < 8:
                return None, "La contraseña debe tener al menos 8 caracteres"
            contrasena_hash = bcrypt.hashpw(
                contrasena.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            try:
                self._repo.update_password(usuario_id, contrasena_hash)
            except Exception as e:
                return None, f"Error al actualizar contraseña: {str(e)}"

        # construir el objeto usuario para la actualización
        usuario = Usuario(
            usuario_id=usuario_id,
            nombre=datos_usuario["nombre"].strip(),
            apellido_paterno=datos_usuario["apellido_paterno"].strip(),
            apellido_materno=datos_usuario.get("apellido_materno", "").strip() or None,
            email=email,
            telefono=telefono or None,
            rol_id=datos_usuario["rol_id"],
            activo=datos_usuario.get("activo", 1),
        )

        try:
            self._repo.update(usuario)
            return usuario, None
        except Exception as e:
            return None, f"Error al actualizar usuario: {str(e)}"
