# Vista del login - carga el .ui de Qt Designer y maneja la interaccion

import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5 import uic

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "auth", "login_view.ui")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.svg")
ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.svg")


def _svg_to_pixmap(svg_path, width, height):
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


class LoginView(QWidget):

    login_requested = pyqtSignal(str, str)  # email, password

    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self._load_logo()
        self._set_window_icon()
        self._connect_signals()
        self._center_on_screen()

    def _load_logo(self):
        pixmap = _svg_to_pixmap(LOGO_PATH, 380, 100)
        self.logoLabel.setPixmap(pixmap)

    def _set_window_icon(self):
        pixmap = _svg_to_pixmap(ICON_PATH, 64, 64)
        self.setWindowIcon(QIcon(pixmap))

    def _connect_signals(self):
        self.loginBtn.clicked.connect(self._emit_login)
        self.passwordInput.returnPressed.connect(self._emit_login)  # enter tambien hace login

    def _emit_login(self):
        self.login_requested.emit(
            self.emailInput.text().strip(),
            self.passwordInput.text(),
        )

    def show_error(self, message):
        self.errorLabel.setText(message)
        self.errorLabel.setVisible(True)

    def clear_error(self):
        self.errorLabel.setVisible(False)

    def set_loading(self, loading):
        self.loginBtn.setEnabled(not loading)
        self.loginBtn.setText("Verificando..." if loading else "Iniciar Sesión")

    def _center_on_screen(self):
        # centrar la ventana en la pantalla y ajustar tamaño
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()

        # ajustar tamaño de la ventana para ocupar mejor el espacio
        window_width = min(1100, int(screen.width() * 0.8))
        window_height = min(700, int(screen.height() * 0.85))
        self.resize(window_width, window_height)

        # centrar en la pantalla
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)
