"""
Servicio de autenticacion para el sistema CRM.

Este modulo proporciona la logica de negocio para la autenticacion de usuarios,
incluyendo validacion de credenciales, verificacion de contraseñas con bcrypt,
y actualizacion de fecha de ultimo acceso.

IMPORTANTE: Este servicio maneja datos sensibles (contraseñas). NUNCA loguear
contraseñas en texto plano. Todas las operaciones de logging deben usar el
sistema centralizado de AppLogger que filtra automaticamente datos sensibles.

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

import bcrypt
from datetime import datetime
from app.repositories.usuario_repository import UsuarioRepository
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class AuthService:
    """
    Servicio de autenticacion de usuarios.

    Maneja el proceso de login validando credenciales contra la base de datos,
    verificando contraseñas hasheadas con bcrypt, y actualizando el ultimo acceso.
    """
    def __init__(self):
        """
        Inicializa el servicio de autenticacion.

        Crea una instancia del repositorio de usuarios para acceso a datos.
        """
        self._repo = UsuarioRepository()

    def login(self, email, password):
        """
        Autentica un usuario con email y contraseña.

        Valida las credenciales del usuario, verifica la contraseña hasheada
        con bcrypt, y actualiza la fecha de ultimo acceso si la autenticacion
        es exitosa.

        Args:
            email (str): Correo electronico del usuario.
            password (str): Contraseña en texto plano.

        Returns:
            tuple: (Usuario|None, str|None)
                - Si es exitoso: (objeto Usuario, None)
                - Si falla: (None, mensaje de error)

        Examples:
            >>> service = AuthService()
            >>> usuario, error = service.login("admin@example.com", "password123")
            >>> if error is None:
            >>>     print(f"Bienvenido {usuario.nombre}")
            >>> else:
            >>>     print(f"Error: {error}")

        Note:
            - Las contraseñas NUNCA se loguean en texto plano
            - Los intentos fallidos se registran en el log con nivel WARNING
            - Los intentos exitosos se registran con nivel INFO
        """
        # IMPORTANTE: NUNCA loguear la contrasena en texto plano
        logger.info(f"Intento de login para email: {email}")

        try:
            usuario = self._repo.find_by_email(email)
            if usuario is None:
                AppLogger.log_auth_attempt(logger, email, False, "Email no encontrado")
                return None, "Correo electrónico no encontrado"

            # verificar contraseña con bcrypt
            if not bcrypt.checkpw(password.encode("utf-8"), usuario.contrasena_hash.encode("utf-8")):
                AppLogger.log_auth_attempt(logger, email, False, "Contraseña incorrecta")
                return None, "Contraseña incorrecta"

            # actualizar la fecha de ultimo acceso
            self._repo.update_ultimo_acceso(
                usuario.usuario_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            AppLogger.log_auth_attempt(logger, email, True)
            logger.info(f"Usuario {usuario.usuario_id} ({email}) inicio sesion exitosamente")
            return usuario, None

        except Exception as e:
            AppLogger.log_exception(logger, f"Error en login para {email}")
            return None, sanitize_error_message(e)
