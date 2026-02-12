# Controller principal - maneja la vista del menú despues del login

from app.views.main_view import MainView


class MainController:
    def __init__(self, usuario):
        self._view = MainView(usuario)

    def show(self):
        self._view.showMaximized()

    def close(self):
        self._view.close()
