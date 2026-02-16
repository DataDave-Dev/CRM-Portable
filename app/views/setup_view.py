# Vista para configuracion inicial del sistema - creacion del primer usuario administrador

import os
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from app.services.usuario_service import UsuarioService
from app.utils.validators import Validator

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "auth", "setup_view.ui")


class SetupView(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self._usuario_service = UsuarioService()
        self._setup_connections()

    def _setup_connections(self):
        # conectar eventos
        self.btnCrear.clicked.connect(self._on_crear_usuario)
        self.inputPassword.textChanged.connect(self._on_password_changed)
        self.inputEmail.returnPressed.connect(self._on_crear_usuario)
        self.inputPassword.returnPressed.connect(self._on_crear_usuario)
        self.inputConfirm.returnPressed.connect(self._on_crear_usuario)

    def _on_password_changed(self, password):
        # mostrar indicador de fortaleza de contraseña en tiempo real
        if not password:
            self.lblStrength.setText("")
            self.lblStrength.setStyleSheet("")
            return

        error = Validator.validate_password_strength(password)
        if error is None:
            self.lblStrength.setText("Contraseña segura")
            self.lblStrength.setStyleSheet("color: #48bb78;")
        else:
            self.lblStrength.setText(error)
            self.lblStrength.setStyleSheet("color: #f6ad55;")

    def _on_crear_usuario(self):
        # limpiar mensaje de error previo
        self.lblError.setText("")

        # obtener datos del formulario
        nombre = self.inputNombre.text().strip()
        apellido = self.inputApellido.text().strip()
        email = self.inputEmail.text().strip()
        password = self.inputPassword.text()
        confirm = self.inputConfirm.text()

        # validar campos requeridos
        if not nombre:
            self.lblError.setText("El nombre es requerido")
            self.inputNombre.setFocus()
            return

        if not apellido:
            self.lblError.setText("El apellido es requerido")
            self.inputApellido.setFocus()
            return

        if not email:
            self.lblError.setText("El correo electrónico es requerido")
            self.inputEmail.setFocus()
            return

        # validar formato de email
        error_email = Validator.validate_email(email)
        if error_email:
            self.lblError.setText(error_email)
            self.inputEmail.setFocus()
            return

        if not password:
            self.lblError.setText("La contraseña es requerida")
            self.inputPassword.setFocus()
            return

        # validar fortaleza de contraseña
        error_password = Validator.validate_password_strength(password)
        if error_password:
            self.lblError.setText(error_password)
            self.inputPassword.setFocus()
            return

        # validar que las contraseñas coincidan
        if password != confirm:
            self.lblError.setText("Las contraseñas no coinciden")
            self.inputConfirm.setFocus()
            return

        # crear usuario administrador (rol_id = 1)
        datos_usuario = {
            "nombre": nombre,
            "apellido_paterno": apellido,
            "email": email,
            "contrasena": password,
            "rol_id": 1
        }

        usuario, error = self._usuario_service.crear_usuario(datos_usuario)

        if error:
            self.lblError.setText(error)
            return

        # usuario creado exitosamente - cerrar ventana de setup
        self.close()

    def show_error(self, mensaje):
        # metodo publico para mostrar errores desde el controlador
        self.lblError.setText(mensaje)
