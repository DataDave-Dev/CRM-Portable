# Punto de entrada del CRM

import sys
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMessageBox

from app.database.initializer import initialize_database, has_users
from app.views.setup_view import SetupView
from app.controllers.login_controller import LoginController
from app.controllers.main_controller import MainController


# Clase principal, controla el ciclo de vida de la app (setup inicial o login a menú)
class CRMApp:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)
        self._setup_view: Optional[SetupView] = None
        self._login_controller: Optional[LoginController] = None
        self._main_controller: Optional[MainController] = None

    def run(self):
        initialize_database()  # crear tablas si no existen

        # verificar si hay usuarios en la base de datos
        if not has_users():
            # primera vez - mostrar configuracion inicial
            self._show_setup()
        else:
            # ya hay usuarios - mostrar login normal
            self._show_login()

        sys.exit(self._app.exec_())

    def _show_setup(self):
        # mostrar vista de configuracion inicial para crear primer usuario admin
        self._setup_view = SetupView()
        self._setup_view.show()
        # cuando se cierre setup (usuario creado), mostrar login
        self._setup_view.destroyed.connect(self._show_login)

    def _show_login(self):
        # mostrar ventana de login
        self._login_controller = LoginController()
        self._login_controller.login_successful.connect(self._on_login_success)
        self._login_controller.show()

    def _on_login_success(self, usuario):
        # cerrar login y abrir menu principal
        if self._login_controller:
            self._login_controller.close()
        try:
            self._main_controller = MainController(usuario)
            self._main_controller.show()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error al iniciar",
                f"No se pudo abrir la ventana principal:\n{str(e)}"
            )
            self._show_login()

if __name__ == "__main__":
    try:
        app = CRMApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
