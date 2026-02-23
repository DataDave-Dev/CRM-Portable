"""
Controlador principal del menu del CRM.

Este controlador es intencionalmente simple: su unica responsabilidad es
crear la vista principal (MainView) y pasarle el usuario autenticado.

La logica de negocio de cada modulo (contactos, empresas, ventas, etc.) vive
en sus propias vistas y servicios. MainController solo gestiona el ciclo de
vida de la ventana principal: crearla, mostrarla y cerrarla.

Flujo:
    1. main.py recibe el evento login_successful con el objeto Usuario.
    2. main.py crea MainController(usuario).
    3. MainController.__init__ crea MainView(usuario).
    4. main.py llama MainController.show() que llama MainView.showMaximized().
    5. El usuario navega por los modulos dentro de MainView.
    6. Al cerrar la ventana, MainView maneja el evento de cierre.
"""

from app.views.main_view import MainView


class MainController:
    """
    Controlador del menu principal de la aplicacion CRM.

    Gestiona el ciclo de vida de la ventana principal: creacion, visualizacion y cierre.
    Todo el comportamiento de los modulos (contactos, ventas, etc.) esta encapsulado
    dentro de MainView y sus sub-vistas.

    Atributos:
        _view (MainView): La ventana principal de la aplicacion.
    """

    def __init__(self, usuario):
        """
        Inicializa el controlador creando la vista principal.

        Parametros:
            usuario (Usuario): El objeto con los datos del usuario autenticado.
                MainView lo usa para mostrar el nombre del usuario en el encabezado
                y para asignar el ID del usuario como 'propietario' en nuevos registros.
        """
        # Crear la ventana principal con el usuario autenticado.
        # MainView construye todos los tabs y sub-vistas en su __init__.
        self._view = MainView(usuario)

    def show(self):
        """
        Muestra la ventana principal maximizada.

        showMaximized() ocupa toda la pantalla disponible (sin modo pantalla completa),
        ideal para una aplicacion de gestion empresarial donde el usuario necesita
        ver muchos datos al mismo tiempo.
        """
        self._view.showMaximized()

    def close(self):
        """
        Cierra la ventana principal.

        Se puede llamar desde fuera del controlador si se necesita cerrar
        la ventana programaticamente (ej: cierre de sesion).
        """
        self._view.close()
