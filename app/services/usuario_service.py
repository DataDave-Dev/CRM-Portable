"""
Servicio de gestion de usuarios para el sistema CRM.

Este modulo proporciona la logica de negocio para crear y actualizar usuarios,
incluyendo validaciones robustas de datos, hashing seguro de contraseñas con bcrypt,
y manejo de errores con mensajes sanitizados.

IMPORTANTE: Este servicio maneja datos sensibles (contraseñas). NUNCA loguear
contraseñas en texto plano. El sistema de logging automaticamente filtra campos
sensibles como 'contrasena', 'contrasena_hash', 'password', etc.

Validaciones implementadas:
    - Campos requeridos: nombre, apellido_paterno, email, contraseña, rol_id
    - Formato de email valido (RFC 5322)
    - Unicidad de email en la base de datos
    - Longitud minima de contraseña (8 caracteres)
    - Formato de telefono (10 digitos numericos)
    - Validacion de rol_id existente (foreign key)

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

import bcrypt
import re
from app.repositories.usuario_repository import UsuarioRepository
from app.models.Usuario import Usuario
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class UsuarioService:
    """
    Servicio de gestion de usuarios del sistema.

    Proporciona metodos para crear y actualizar usuarios con validaciones completas,
    hashing de contraseñas con bcrypt, y logging seguro de operaciones.
    """

    def __init__(self):
        """
        Inicializa el servicio de usuarios.

        Crea una instancia del repositorio de usuarios para acceso a datos.
        """
        self._repo = UsuarioRepository()

    def crear_usuario(self, datos_usuario):
        """
        Crea un nuevo usuario en el sistema.

        Valida todos los campos requeridos y formatos, hashea la contraseña con bcrypt,
        y crea el registro en la base de datos. La contraseña NUNCA se loguea.

        Args:
            datos_usuario (dict): Diccionario con los datos del usuario:
                - nombre (str, requerido): Nombre del usuario
                - apellido_paterno (str, requerido): Apellido paterno
                - apellido_materno (str, opcional): Apellido materno
                - email (str, requerido): Correo electronico unico
                - telefono (str, opcional): Telefono de 10 digitos
                - contrasena (str, requerido): Contraseña minimo 8 caracteres
                - rol_id (int, requerido): ID del rol asignado
                - activo (int, opcional): 1=activo, 0=inactivo (default 1)
                - foto_perfil (str, opcional): Ruta a imagen de perfil

        Returns:
            tuple: (Usuario|None, str|None)
                - Si es exitoso: (objeto Usuario con usuario_id asignado, None)
                - Si falla: (None, mensaje de error descriptivo)

        Examples:
            >>> service = UsuarioService()
            >>> datos = {
            ...     "nombre": "Juan",
            ...     "apellido_paterno": "Perez",
            ...     "email": "juan@example.com",
            ...     "contrasena": "MiPassword123",
            ...     "rol_id": 1
            ... }
            >>> usuario, error = service.crear_usuario(datos)
            >>> if error is None:
            ...     print(f"Usuario creado con ID: {usuario.usuario_id}")

        Note:
            - La contraseña se hashea con bcrypt antes de guardar
            - El email se valida con expresion regular
            - El telefono debe ser exactamente 10 digitos
            - El email debe ser unico en el sistema
        """
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
            # IMPORTANTE: NUNCA loguear la contrasena
            logger.info(f"Creando usuario: {email}")
            usuario_id = self._repo.create(nuevo_usuario)
            nuevo_usuario.usuario_id = usuario_id
            logger.info(f"Usuario {usuario_id} ({email}) creado exitosamente")
            return nuevo_usuario, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear usuario: {email}")
            return None, sanitize_error_message(e)

    def actualizar_usuario(self, usuario_id, datos_usuario):
        """
        Actualiza un usuario existente en el sistema.

        Valida campos requeridos y formatos, actualiza la contraseña solo si se
        proporciona una nueva, y actualiza el registro en la base de datos.

        Args:
            usuario_id (int): ID del usuario a actualizar
            datos_usuario (dict): Diccionario con los datos a actualizar:
                - nombre (str, requerido): Nombre del usuario
                - apellido_paterno (str, requerido): Apellido paterno
                - apellido_materno (str, opcional): Apellido materno
                - email (str, requerido): Correo electronico unico
                - telefono (str, opcional): Telefono de 10 digitos
                - contrasena (str, opcional): Nueva contraseña minimo 8 caracteres
                - rol_id (int, requerido): ID del rol asignado
                - activo (int, opcional): 1=activo, 0=inactivo

        Returns:
            tuple: (Usuario|None, str|None)
                - Si es exitoso: (objeto Usuario actualizado, None)
                - Si falla: (None, mensaje de error descriptivo)

        Examples:
            >>> service = UsuarioService()
            >>> datos = {
            ...     "nombre": "Juan Carlos",
            ...     "apellido_paterno": "Perez",
            ...     "email": "juan@example.com",
            ...     "rol_id": 2
            ... }
            >>> usuario, error = service.actualizar_usuario(5, datos)
            >>> if error is None:
            ...     print(f"Usuario {usuario.usuario_id} actualizado")

        Note:
            - Si se proporciona 'contrasena', se hashea antes de actualizar
            - El email debe ser unico excluyendo el usuario actual
            - Si no se proporciona contraseña, la anterior se mantiene
            - La contraseña NUNCA se loguea en texto plano
        """
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
            # IMPORTANTE: NUNCA loguear la contrasena en texto plano
            logger.info(f"Actualizando contrasena para usuario {usuario_id}")
            contrasena_hash = bcrypt.hashpw(
                contrasena.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            try:
                self._repo.update_password(usuario_id, contrasena_hash)
                logger.info(f"Contrasena actualizada exitosamente para usuario {usuario_id}")
            except Exception as e:
                AppLogger.log_exception(logger, f"Error al actualizar contrasena usuario {usuario_id}")
                return None, sanitize_error_message(e)

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
            logger.info(f"Actualizando usuario {usuario_id}: {email}")
            self._repo.update(usuario)
            logger.info(f"Usuario {usuario_id} actualizado exitosamente")
            return usuario, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar usuario {usuario_id}")
            return None, sanitize_error_message(e)
