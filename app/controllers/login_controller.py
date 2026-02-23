"""
Controlador de la pantalla de login del CRM.

Responsabilidades:
    - Intermediar entre LoginView (la pantalla) y AuthService (la logica de autenticacion).
    - Ejecutar la verificacion de contrasenia en un hilo separado para que la
      interfaz no se congele durante el proceso (bcrypt es lento por diseno).
    - Emitir la senal login_successful con el objeto Usuario cuando el login es exitoso.

Por que se usa un hilo separado para bcrypt:
    bcrypt es un algoritmo de hashing disenado deliberadamente para ser lento
    (tarda ~100-300ms por verificacion). Esta lentitud es una caracteristica de
    seguridad, no un bug: hace que los ataques de fuerza bruta sean impracticos.
    Sin embargo, si se ejecuta en el hilo principal de Qt (el hilo de la UI),
    la interfaz se congela durante esos 100-300ms, lo que se ve como un bug.
    La solucion es mover la operacion a un QThread para que la UI siga respondiendo.

Patron QThread usado:
    1. Se crea un QThread (hilo de trabajo).
    2. Se crea un _AuthWorker (el objeto que hace el trabajo real).
    3. moveToThread() asocia el worker con el hilo (la instancia cambia de "hilo propietario").
    4. Se conectan senales: thread.started -> worker.run, worker.finished -> callback.
    5. thread.start() inicia el hilo, lo que dispara la senal started, lo que llama worker.run().
    6. Cuando worker.run() termina, emite finished(), lo que llama _on_auth_finished()
       en el hilo principal (gracias al sistema de senales de Qt).

Senal publica:
    login_successful (pyqtSignal): Se emite con el objeto Usuario autenticado.
        Se conecta en main.py para abrir el menu principal.
"""

from PyQt5.QtCore import QObject, pyqtSignal, QThread

from app.views.login_view import LoginView
from app.services.auth_service import AuthService


class _AuthWorker(QObject):
    """
    Worker que ejecuta la autenticacion en un hilo secundario.

    Se prefija con _ para indicar que es un detalle de implementacion interno,
    no parte de la API publica del modulo.

    Hereda de QObject para poder usar el sistema de senales de Qt.
    Esto es requerido para que las senales funcionen correctamente cuando
    el objeto esta en un hilo diferente al de la UI.

    Atributos:
        finished (pyqtSignal): Se emite al terminar con dos parametros:
            - Primer parametro (object): El objeto Usuario si el login fue exitoso, None si fallo.
            - Segundo parametro (object): Mensaje de error si fallo, None si fue exitoso.
    """

    # Senal que se emite cuando termina la autenticacion (exitosa o fallida).
    # Usa object para poder emitir cualquier tipo (Usuario o None, str o None).
    finished = pyqtSignal(object, object)  # firma: (usuario_o_none, error_o_none)

    def __init__(self, auth_service, email, password):
        """
        Inicializa el worker con los datos necesarios para autenticar.

        Parametros:
            auth_service: Instancia de AuthService para llamar a login().
            email       : Email del usuario ingresado en el formulario.
            password    : Contrasenia en texto plano ingresada en el formulario.
                          NUNCA se loguea ni se almacena fuera de este objeto temporal.
        """
        super().__init__()
        self._auth_service = auth_service
        self._email = email
        self._password = password

    def run(self):
        """
        Ejecuta la autenticacion y emite el resultado via la senal 'finished'.

        Este metodo corre en el hilo secundario (no en el hilo de la UI).
        Llama a auth_service.login() que internamente verifica la contrasenia con bcrypt.
        Al terminar (exito o error), emite la senal finished para que el resultado
        sea procesado en el hilo principal de la UI.

        El try/except general captura cualquier error inesperado (ej: error de conexion
        a la BD) y lo convierte en un mensaje de error para la interfaz.
        """
        try:
            # Esta llamada puede tardar 100-300ms por el bcrypt; no bloquea la UI
            # porque corre en un hilo separado
            usuario, error = self._auth_service.login(self._email, self._password)
            # Emitir el resultado: (usuario o None, None o mensaje_error)
            self.finished.emit(usuario, error)
        except Exception as e:
            # Error inesperado: emitir None como usuario y el mensaje de excepcion
            self.finished.emit(None, str(e))


class LoginController(QObject):
    """
    Controlador de la pantalla de login.

    Coordina la vista (LoginView) con el servicio de autenticacion (AuthService).
    Maneja el ciclo completo del login: validacion basica -> hilo de autenticacion
    -> resultado -> emitir senal o mostrar error.

    Hereda de QObject para poder emitir senales (login_successful).

    Atributos publicos:
        login_successful (pyqtSignal): Se emite con el objeto Usuario cuando
            el login es exitoso. main.py se conecta a esta senal para abrir
            el menu principal.

    Atributos privados:
        _auth_service: Instancia del servicio de autenticacion.
        _view        : La ventana de login (LoginView).
        _thread      : QThread que ejecuta la autenticacion en segundo plano.
        _worker      : _AuthWorker que contiene la logica de autenticacion.
    """

    # Senal publica: se emite con el objeto Usuario cuando el login es exitoso.
    # Se conecta en main.py: self._login_controller.login_successful.connect(self._on_login_success)
    login_successful = pyqtSignal(object)

    def __init__(self):
        """
        Inicializa el controlador de login.

        Crea las instancias del servicio y la vista, y conecta la senal
        login_requested de la vista con el metodo _handle_login de este controlador.
        """
        super().__init__()
        self._auth_service = AuthService()  # servicio que verifica credenciales con bcrypt

        # Crear la vista y conectar su senal al handler de este controlador
        self._view = LoginView()
        # La vista emite login_requested(email, password) cuando el usuario hace clic en "Ingresar"
        self._view.login_requested.connect(self._handle_login)

        # Referencias al hilo y worker; se crean al hacer login, no antes
        self._thread = None
        self._worker = None

    def show(self):
        """Muestra la ventana de login al usuario."""
        self._view.show()

    def close(self):
        """Cierra la ventana de login (llamado desde main.py despues del login exitoso)."""
        self._view.close()

    def _handle_login(self, email, password):
        """
        Maneja el intento de login del usuario.

        Primero hace validacion basica (campos no vacios) para respuesta inmediata.
        Si pasa la validacion, lanza el worker en un hilo separado para la
        verificacion de contrasenia con bcrypt (operacion lenta).

        Parametros:
            email   : Email ingresado por el usuario.
            password: Contrasenia ingresada por el usuario.
        """
        # Validacion basica: no enviar a bcrypt si faltan campos
        if not email or not password:
            self._view.show_error("Por favor completa todos los campos")
            return

        # Mostrar spinner/estado de carga en la vista mientras se procesa
        self._view.set_loading(True)

        # bcrypt es lento por diseno (medida de seguridad antifuerza-bruta).
        # Se ejecuta en un hilo aparte para que la UI no se congele.
        self._thread = QThread()
        self._worker = _AuthWorker(self._auth_service, email, password)

        # Mover el worker al nuevo hilo (cambia su "hilo propietario" en Qt)
        # Esto es necesario para que las operaciones del worker no bloqueen la UI
        self._worker.moveToThread(self._thread)

        # Conectar senales para el ciclo de vida del hilo:
        # 1. Cuando el hilo inicie, ejecutar el metodo run() del worker
        self._thread.started.connect(self._worker.run)
        # 2. Cuando el worker termine, procesar el resultado en el hilo principal
        self._worker.finished.connect(self._on_auth_finished)
        # 3. Cuando el worker termine, detener el hilo
        self._worker.finished.connect(self._thread.quit)
        # 4. Cuando el hilo se detenga, eliminar el objeto QThread para liberar memoria
        self._thread.finished.connect(self._thread.deleteLater)

        # Iniciar el hilo (dispara la senal started, que llama worker.run())
        self._thread.start()

    def _on_auth_finished(self, usuario, error):
        """
        Callback ejecutado en el hilo principal cuando la autenticacion termina.

        Este metodo es llamado automaticamente por la senal finished del worker.
        Qt garantiza que los callbacks de senales cross-thread se ejecuten en el
        hilo receptor del objeto conectado (este controlador esta en el hilo principal),
        por lo que es seguro actualizar la UI desde aqui.

        Parametros:
            usuario: Objeto Usuario si el login fue exitoso, None si fallo.
            error  : Mensaje de error si fallo, None si fue exitoso.
        """
        # Quitar el spinner/estado de carga de la vista
        self._view.set_loading(False)

        if error:
            # Login fallido: mostrar el mensaje de error en la vista
            self._view.show_error(error)
            return

        # Login exitoso: limpiar errores previos y emitir la senal con el usuario
        self._view.clear_error()
        # Esta senal lleva el objeto Usuario a main.py para abrir el menu principal
        self.login_successful.emit(usuario)
