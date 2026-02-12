# Punto de entrada del CRM - aqui arranca todo

import sys
from typing import Optional
from PyQt5.QtWidgets import QApplication

from app.database.initializer import initialize_database
from app.controllers.login_controller import LoginController
from app.controllers.main_controller import MainController


# Clase principal, controla el ciclo de vida de la app (login a menú)
class CRMApp:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._login_controller: Optional[LoginController] = None
        self._main_controller: Optional[MainController] = None

    def run(self):
        initialize_database()  # crear tablas si no existen
        self._show_login()
        sys.exit(self._app.exec_())

    def _show_login(self):
        self._login_controller = LoginController()
        self._login_controller.login_successful.connect(self._on_login_success)
        self._login_controller.show()

    def _on_login_success(self, usuario):
        # cerrar login y abrir menú
        if self._login_controller:
            self._login_controller.close()
        self._main_controller = MainController(usuario)
        self._main_controller.show()

if __name__ == "__main__":
    app = CRMApp()
    app.run()
