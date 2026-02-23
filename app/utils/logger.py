"""
Modulo de logging centralizado para la aplicacion CRM.

Este modulo provee un sistema unificado de registro de eventos (logs) para toda
la aplicacion. En lugar de que cada modulo configure su propio sistema de logs,
todos usan AppLogger como punto central. Esto garantiza:

  - Formato consistente en todos los registros (fecha, nombre del modulo, nivel, mensaje).
  - Almacenamiento en archivos rotativos para no ocupar disco indefinidamente.
  - Separacion automatica de errores criticos en su propio archivo.
  - Filtrado de datos sensibles para no exponer contrasenas o tokens en los logs.

Como usar este modulo en otros archivos del proyecto:

    from app.utils.logger import AppLogger

    # Crear un logger con el nombre del modulo actual (__name__ = e.g. 'app.services.contactos')
    logger = AppLogger.get_logger(__name__)

    # Luego usar el logger normalmente:
    logger.info("Contacto creado exitosamente")
    logger.warning("Intento de acceso sin permisos")
    logger.error("No se pudo conectar a la base de datos")
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    """
    Clase estatica que actua como fabrica y gestor centralizado de loggers.

    Usa el patron Singleton por modulo: cada nombre de logger se crea una sola
    vez y se reutiliza en llamadas posteriores. Esto evita duplicar handlers
    (y por tanto, duplicar lineas en los archivos de log).

    Atributos de clase:
        _loggers     : Diccionario que guarda los loggers ya creados, indexados
                       por nombre. Funciona como cache para no recrearlos.
        _log_dir     : Carpeta donde se almacenan los archivos de log.
        _max_bytes   : Tamano maximo de cada archivo de log antes de rotarlo (10 MB).
        _backup_count: Cantidad de archivos de respaldo que se conservan tras la rotacion.
    """

    # Diccionario cache: { 'nombre_modulo': logger_instance }
    # Se consulta antes de crear un nuevo logger para evitar duplicados.
    _loggers = {}

    # Directorio donde se guardan los archivos .log (relativo al directorio de ejecucion)
    _log_dir = "logs"

    # Limite de tamano por archivo de log: 10 MB (10 * 1024 * 1024 bytes)
    # Cuando el archivo supera este tamano, el RotatingFileHandler lo rota automaticamente.
    _max_bytes = 10 * 1024 * 1024  # 10 MB

    # Cuantos archivos de respaldo se mantienen despues de rotar.
    # Con 5 backups y 10 MB cada uno, el historico maximo es de ~55 MB por tipo de log.
    _backup_count = 5

    @staticmethod
    def _ensure_log_dir():
        """
        Crea el directorio de logs si todavia no existe.

        Se llama antes de crear cualquier handler de archivo para evitar el error
        FileNotFoundError que ocurrira si se intenta escribir en una carpeta
        que no existe.
        """
        if not os.path.exists(AppLogger._log_dir):
            os.makedirs(AppLogger._log_dir)

    @staticmethod
    def get_logger(name, level=logging.INFO):
        """
        Obtiene un logger configurado con los tres handlers estandar.

        Si el logger con ese nombre ya fue creado anteriormente, lo devuelve
        desde el cache (_loggers) sin reconfigurarlo. Esto es importante porque
        Python's logging module tambien guarda loggers globalmente; si se
        agregaran handlers dos veces, cada mensaje apareceria duplicado en los logs.

        Parametros:
            name  : Nombre del logger, tipicamente __name__ del modulo que lo pide.
                    Ejemplo: 'app.controllers.contactos_controller'
            level : Nivel minimo de mensajes que el logger procesara.
                    Por defecto logging.INFO (DEBUG quedara fuera a menos que
                    se pida explicitamente).

        Retorna:
            logging.Logger: Instancia de logger lista para usar.

        Handlers configurados:
            1. RotatingFileHandler -> logs/app.log    (nivel DEBUG y superior)
            2. RotatingFileHandler -> logs/errors.log (nivel ERROR y superior)
            3. StreamHandler       -> consola          (nivel WARNING y superior)
        """
        # Si ya existe en el cache local, devolverlo directamente
        if name in AppLogger._loggers:
            return AppLogger._loggers[name]

        # Garantizar que el directorio de logs existe antes de crear archivos
        AppLogger._ensure_log_dir()

        # Crear (o recuperar) el logger de Python con el nombre dado
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Proteccion contra doble configuracion: si el logger ya tiene handlers
        # (por ejemplo porque otro codigo ya lo configuro), no agregar mas.
        if logger.handlers:
            return logger

        # --- Formato comun para todos los handlers ---
        # Ejemplo de linea resultante:
        #   2026-02-21 14:35:02 - app.services.ventas - INFO - Venta registrada [ID: 42]
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # --- Handler 1: Archivo general (app.log) ---
        # Recibe TODOS los niveles desde DEBUG en adelante.
        # Es el registro completo de la actividad de la aplicacion.
        # RotatingFileHandler rota el archivo cuando alcanza _max_bytes,
        # renombrando el actual a app.log.1, app.log.2, etc., y creando
        # uno nuevo vacio. Al llegar a _backup_count archivos de respaldo,
        # elimina el mas antiguo automaticamente.
        general_file = os.path.join(AppLogger._log_dir, 'app.log')
        file_handler = RotatingFileHandler(
            general_file,
            maxBytes=AppLogger._max_bytes,
            backupCount=AppLogger._backup_count,
            encoding='utf-8'  # importante para nombres con acentos u otros caracteres UTF-8
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # --- Handler 2: Archivo de errores (errors.log) ---
        # Solo recibe mensajes de nivel ERROR y CRITICAL.
        # Tener un archivo separado facilita el monitoreo de problemas graves
        # sin tener que revisar todo el log general.
        # Tambien usa rotacion para no crecer indefinidamente.
        error_file = os.path.join(AppLogger._log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=AppLogger._max_bytes,
            backupCount=AppLogger._backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # --- Handler 3: Consola (salida estandar) ---
        # Solo muestra WARNING y superiores para no saturar la terminal durante el desarrollo.
        # Los mensajes INFO y DEBUG siguen yendo al archivo, pero no aparecen en pantalla.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)

        # Registrar los tres handlers en el logger
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        # Guardar en cache para reutilizar en llamadas futuras
        AppLogger._loggers[name] = logger

        return logger

    @staticmethod
    def log_exception(logger, message, exc_info=True):
        """
        Registra una excepcion incluyendo su stack trace completo.

        Usar este metodo en lugar de logger.error() cuando se captura una
        excepcion con except, porque exc_info=True hace que Python adjunte
        automaticamente la traza de error (traceback) al mensaje de log.
        Esto es indispensable para depurar errores en produccion.

        Parametros:
            logger  : Instancia de logger obtenida con get_logger().
            message : Descripcion legible del error (contexto de lo que ocurria).
            exc_info: Si True (valor por defecto), adjunta el traceback actual.

        Ejemplo de uso:
            try:
                conn = get_connection()
            except Exception as e:
                AppLogger.log_exception(logger, "Fallo la conexion a la BD")
        """
        logger.error(message, exc_info=exc_info)

    @staticmethod
    def log_db_operation(logger, operation, table, record_id=None, details=None):
        """
        Registra operaciones de base de datos con formato estandarizado.

        Centraliza el formato de los logs de BD para que sean consistentes
        en toda la aplicacion y facilmente filtrables (todos empiezan con 'DB').

        Parametros:
            logger    : Instancia de logger del modulo que realiza la operacion.
            operation : Tipo de operacion: 'INSERT', 'UPDATE', 'DELETE', 'SELECT'.
            table     : Nombre de la tabla afectada, e.g. 'Contactos'.
            record_id : ID del registro afectado (opcional, ayuda a rastrear cambios).
            details   : Informacion adicional como campos modificados (opcional).

        Ejemplo de mensaje generado:
            "DB INSERT: Contactos [ID: 15] - nombre=Juan Lopez"
        """
        msg = f"DB {operation}: {table}"
        if record_id:
            msg += f" [ID: {record_id}]"
        if details:
            msg += f" - {details}"
        logger.info(msg)

    @staticmethod
    def _filter_sensitive_data(data):
        """
        Elimina o enmascara datos sensibles antes de escribirlos en los logs.

        Esta funcion es crucial para seguridad: nunca deben aparecer contrasenas,
        tokens, numeros de tarjeta u otra informacion confidencial en los archivos
        de log, ya que estos archivos pueden ser revisados por personal de soporte
        o quedarse almacenados en backups.

        La funcion trabaja de forma recursiva: si encuentra un diccionario dentro
        de otro diccionario o una lista, los procesa tambien.

        Parametros:
            data: Puede ser un dict, una lista, o cualquier valor primitivo.
                  - dict: Se revisa cada clave; si la clave contiene alguna palabra
                          sensible, el valor se reemplaza por '***HIDDEN***'.
                  - list: Se procesa cada elemento de la lista recursivamente.
                  - otro: Se devuelve sin cambios.

        Campos considerados sensibles (se compara en minusculas):
            - password, contrasena, contrasena_hash: contrasenas de usuarios
            - token, api_key, secret:                credenciales de acceso a APIs
            - auth, authorization, session, cookie:  datos de sesion y autenticacion
            - csrf:                                  token anti-falsificacion
            - pin, ssn:                              numeros de identificacion personal
            - tarjeta, cvv, cuenta_bancaria:         datos financieros
            - rfc:                                   identificacion fiscal mexicana

        Retorna:
            Una copia del dato con los campos sensibles reemplazados, o el dato
            original si no es un dict ni una lista.
        """
        if data is None:
            return None

        # Lista de palabras clave que identifican campos sensibles.
        # La comparacion se hace en minusculas para atrapar variantes como
        # 'Password', 'PASSWORD', 'password', etc.
        sensitive_fields = [
            'password', 'contrasena', 'contrasena_hash', 'contrasenah ash',
            'token', 'api_key', 'secret', 'auth', 'authorization',
            'session', 'cookie', 'csrf', 'pin', 'ssn', 'tarjeta',
            'cvv', 'cuenta_bancaria', 'rfc'
        ]

        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                key_lower = str(key).lower()
                # Verificar si alguna palabra sensible aparece como subcadena de la clave.
                # Por ejemplo, 'contrasena_nueva' contiene 'contrasena', entonces se oculta.
                if any(sensitive in key_lower for sensitive in sensitive_fields):
                    filtered[key] = '***HIDDEN***'
                elif isinstance(value, (dict, list)):
                    # Procesar recursivamente estructuras anidadas
                    filtered[key] = AppLogger._filter_sensitive_data(value)
                else:
                    filtered[key] = value
            return filtered
        elif isinstance(data, list):
            # Procesar cada elemento de la lista de forma recursiva
            return [AppLogger._filter_sensitive_data(item) for item in data]
        else:
            # Valor primitivo (str, int, float, bool): devolver sin modificar
            return data

    @staticmethod
    def log_service_call(logger, service, method, params=None):
        """
        Registra llamadas a la capa de servicios sin exponer parametros sensibles.

        Util para trazar el flujo de ejecucion (debugging) a nivel DEBUG.
        Antes de escribir los parametros en el log, los filtra con
        _filter_sensitive_data para garantizar que no se registren contrasenas
        ni tokens aunque el llamador los incluya accidentalmente en params.

        Parametros:
            logger  : Instancia de logger del modulo que realiza la llamada.
            service : Nombre de la clase o modulo de servicio, e.g. 'ContactosService'.
            method  : Nombre del metodo invocado, e.g. 'crear_contacto'.
            params  : Diccionario con los parametros enviados al metodo (opcional).
                      Puede contener cualquier dato; los sensibles se enmascaran.

        Ejemplo de mensaje generado:
            "Service call: ContactosService.crear_contacto - params: {'nombre': 'Juan', 'password': '***HIDDEN***'}"
        """
        msg = f"Service call: {service}.{method}"
        if params:
            # Filtrar datos sensibles antes de incluirlos en el log
            safe_params = AppLogger._filter_sensitive_data(params)
            msg += f" - params: {safe_params}"
        logger.debug(msg)

    @staticmethod
    def log_auth_attempt(logger, email, success, reason=None):
        """
        Registra intentos de autenticacion (login) con nivel apropiado segun resultado.

        Los intentos exitosos se registran como INFO porque son eventos normales.
        Los intentos fallidos se registran como WARNING porque pueden indicar:
          - Un usuario que olvido su contrasena (benigno).
          - Un ataque de fuerza bruta o de diccionario (malicioso).
        Usar WARNING en fallos permite configurar alertas o filtrar facilmente
        todos los intentos de acceso no autorizados revisando solo ese nivel.

        Por seguridad, el email se registra (para auditar quien intento acceder),
        pero la contrasena NUNCA aparece en el log bajo ninguna circunstancia.

        Parametros:
            logger  : Instancia de logger, tipicamente el del modulo de autenticacion.
            email   : Direccion de correo con la que se intento iniciar sesion.
            success : True si el login fue exitoso, False si fallo.
            reason  : Razon del fallo (solo se incluye cuando success=False).
                      Ejemplos: 'Contrasena incorrecta', 'Usuario no encontrado',
                      'Cuenta desactivada'.

        Ejemplos de mensajes generados:
            INFO:    "Intento de login exitoso para: juan@empresa.com"
            WARNING: "Intento de login fallido para: juan@empresa.com - Razon: Contrasena incorrecta"
        """
        status = "exitoso" if success else "fallido"
        msg = f"Intento de login {status} para: {email}"

        # Solo agregar la razon cuando el intento fallo para dar contexto al WARNING
        if reason and not success:
            msg += f" - Razon: {reason}"

        if success:
            logger.info(msg)
        else:
            # WARNING para que aparezca en consola y sea facilmente filtrable en los logs
            logger.warning(msg)
