# Controller del login - conecta la vista con el servicio de autenticacion

from PyQt5.QtCore import QObject, pyqtSignal, QThread

from app.views.login_view import LoginView
from app.services.auth_service import AuthService


class _AuthWorker(QObject):
    
    finished = pyqtSignal(object, object)  # (usuario, error)

    def __init__(self, auth_service, email, password):
        super().__init__()
        self._auth_service = auth_service
        self._email = email
        self._password = password

    def run(self):
        try:
            usuario, error = self._auth_service.login(self._email, self._password)
            self.finished.emit(usuario, error)
        except Exception as e:
            self.finished.emit(None, str(e))


class LoginController(QObject):

    login_successful = pyqtSignal(object)  # se emite cuando el login es correcto

    def __init__(self):
        super().__init__()
        self._auth_service = AuthService()
        self._view = LoginView()
        self._view.login_requested.connect(self._handle_login)
        self._thread = None
        self._worker = None

    def show(self):
        self._view.show()

    def close(self):
        self._view.close()

    def _handle_login(self, email, password):
        if not email or not password:
            self._view.show_error("Por favor completa todos los campos")
            return

        self._view.set_loading(True)

        # bcrypt es CPU-intensivo: correrlo en un hilo aparte evita bloquear
        # el event loop de Qt y previene KeyboardInterrupt en el hilo principal
        self._thread = QThread()
        self._worker = _AuthWorker(self._auth_service, email, password)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_auth_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_auth_finished(self, usuario, error):
        self._view.set_loading(False)

        if error:
            self._view.show_error(error)
            return

        self._view.clear_error()
        self.login_successful.emit(usuario)
