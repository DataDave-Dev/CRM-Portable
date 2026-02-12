# Logica de autenticacion (login)

import bcrypt
from datetime import datetime
from app.repositories.usuario_repository import UsuarioRepository


class AuthService:
    def __init__(self):
        self._repo = UsuarioRepository()

    def login(self, email, password):
        usuario = self._repo.find_by_email(email)
        if usuario is None:
            return None, "Correo electrónico no encontrado"

        # verificar contraseña con bcrypt
        if not bcrypt.checkpw(password.encode("utf-8"), usuario.contrasena_hash.encode("utf-8")):
            return None, "Contraseña incorrecta"

        # actualizar la fecha de ultimo acceso
        self._repo.update_ultimo_acceso(
            usuario.usuario_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return usuario, None
