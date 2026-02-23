import sys
import signal
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMessageBox

from app.database.initializer import initialize_database, has_users
from app.views.setup_view import SetupView
from app.controllers.login_controller import LoginController
from app.controllers.main_controller import MainController


class CRMApp:
    """
    Clase principal que gestiona el ciclo de vida de la aplicacion CRM.

    Responsabilidades:
    - Crear la instancia de QApplication (obligatoria para PyQt5)
    - Inicializar la base de datos en el primer uso
    - Determinar si mostrar configuracion inicial o login
    - Orquestar la transicion entre pantallas: setup -> login -> menu principal
    - Mantener referencias a los controladores activos para evitar que el
      garbage collector de Python los elimine mientras estan en uso

    Atributos privados:
        _app: Instancia de QApplication (singleton de PyQt5)
        _setup_view: Vista de configuracion inicial (solo en primer uso)
        _login_controller: Controlador de la pantalla de login
        _main_controller: Controlador del menu principal (tras login exitoso)
    """

    def __init__(self):
        """
        Inicializa la aplicacion PyQt5 y configura seniales del sistema.

        Notas importantes:
        - setQuitOnLastWindowClosed(False): Evita que la app se cierre al cerrar
          la ventana de login, ya que luego se abre el menu principal.
        - signal.SIG_IGN: Ignora Ctrl+C desde consola para prevenir cierre abrupto.
          El usuario debe cerrar la app desde la ventana principal.
        """
        self._app = QApplication(sys.argv)
        # no cerrar la app cuando se cierra el login (aun falta abrir el menu)
        self._app.setQuitOnLastWindowClosed(False)
        # ignorar Ctrl+C en consola para evitar cierre sin limpiar recursos
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        # referencias a las ventanas activas (None hasta que se necesiten)
        self._setup_view: Optional[SetupView] = None
        self._login_controller: Optional[LoginController] = None
        self._main_controller: Optional[MainController] = None

    def run(self):
        """
        Ejecuta el ciclo principal de la aplicacion.

        Pasos:
        1. Inicializa la BD (ejecuta database_query.sql si crm.db no existe)
        2. Verifica si hay usuarios registrados
        3. Muestra la pantalla apropiada (setup o login)
        4. Bloquea en app.exec_() hasta que el usuario cierra la aplicacion
        """
        # crear tablas del schema SQL si la base de datos no existe aun
        initialize_database()

        # decidir que pantalla mostrar segun si ya hay usuarios en el sistema
        if not has_users():
            # primer uso del sistema: crear administrador inicial
            self._show_setup()
        else:
            # uso normal: mostrar pantalla de autenticacion
            self._show_login()

        # exec_() inicia el event loop de Qt; sys.exit recibe el codigo de salida
        sys.exit(self._app.exec_())

    def _show_setup(self):
        """
        Muestra la pantalla de configuracion inicial (solo en el primer uso).

        SetupView pide nombre, email y contrasenia para crear el primer usuario
        administrador. Al cerrar esta ventana (senal 'destroyed'), se llama
        automaticamente a _show_login para continuar el flujo normal.
        """
        self._setup_view = SetupView()
        self._setup_view.show()
        # al terminar el setup y cerrarse la ventana, avanzar al login
        self._setup_view.destroyed.connect(self._show_login)

    def _show_login(self):
        """
        Muestra la pantalla de login.

        LoginController maneja la autenticacion en un hilo secundario (QThread)
        para que la interfaz no se congele mientras bcrypt verifica la contrasenia
        (bcrypt es intencionalmente lento como medida de seguridad).
        La senal 'login_successful' se emite con el objeto Usuario cuando el login es exitoso.
        """
        self._login_controller = LoginController()
        # conectar la senal de login exitoso a nuestra funcion de transicion
        self._login_controller.login_successful.connect(self._on_login_success)
        self._login_controller.show()

    def _on_login_success(self, usuario):
        """
        Callback ejecutado cuando el login es exitoso.

        Cierra la ventana de login y abre el menu principal maximizado.
        El objeto 'usuario' se pasa al MainController para personalizar
        la interfaz (nombre en encabezado, permisos segun rol, etc.).

        Si ocurre un error al abrir el menu (situacion rara), muestra un
        dialogo de error y regresa a la pantalla de login.

        Args:
            usuario (Usuario): Objeto con los datos del usuario autenticado.
                Viene del AuthService tras validar email y contrasenia.
        """
        # cerrar la ventana de login antes de abrir el menu
        if self._login_controller:
            self._login_controller.close()
        try:
            # crear y mostrar el menu principal con el usuario autenticado
            self._main_controller = MainController(usuario)
            self._main_controller.show()  # showMaximized() se llama internamente
        except Exception as e:
            # si falla al abrir el menu, avisar y volver al login
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
        # el usuario presiono Ctrl+C desde la consola: salir limpiamente
        sys.exit(0)
