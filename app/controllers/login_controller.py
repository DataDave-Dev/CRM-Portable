# Controller del login - conecta la vista con el servicio de autenticacion

from PyQt5.QtCore import QObject, pyqtSignal

from app.views.login_view import LoginView
from app.services.auth_service import AuthService


class LoginController(QObject):

    login_successful = pyqtSignal(object)  # se emite cuando el login es correcto

    def __init__(self):
        super().__init__()
        self._auth_service = AuthService()
        self._view = LoginView()
        self._view.login_requested.connect(self._handle_login)

    def show(self):
        self._view.show()

    def close(self):
        self._view.close()

    def _handle_login(self, email, password):
        if not email or not password:
            self._view.show_error("Por favor completa todos los campos")
            return

        self._view.set_loading(True)

        usuario, error = self._auth_service.login(email, password)

        self._view.set_loading(False)

        if error:
            self._view.show_error(error)
            return

        self._view.clear_error()
        self.login_successful.emit(usuario)
