# Vista principal del CRM (dashboard) - carga el .ui y muestra datos del usuario

import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5 import uic

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "main_view.ui")
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")


class MainView(QMainWindow):

    def __init__(self, usuario):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self._setup_icons()
        self._set_user_data(usuario)

    def _setup_icons(self):
        logout_icon = QIcon(os.path.join(ASSETS_PATH, "logout.svg"))
        self.btnCerrarSesion.setIcon(logout_icon)
        self.btnCerrarSesion.setIconSize(QSize(20, 20))

    def _set_user_data(self, usuario):
        nombre_completo = f"{usuario.nombre} {usuario.apellido_paterno}"
        self.headerUserName.setText(nombre_completo)
        self.welcomeTitle.setText(f"Bienvenido, {usuario.nombre}")
