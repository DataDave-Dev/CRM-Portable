# sistema de logging centralizado

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    # clase para gestionar el logging de la aplicacion

    _loggers = {}
    _log_dir = "logs"
    _max_bytes = 10 * 1024 * 1024  # 10 MB
    _backup_count = 5

    @staticmethod
    def _ensure_log_dir():
        # crear directorio de logs si no existe
        if not os.path.exists(AppLogger._log_dir):
            os.makedirs(AppLogger._log_dir)

    @staticmethod
    def get_logger(name, level=logging.INFO):
        # obtiene o crea un logger con el nombre especificado
        if name in AppLogger._loggers:
            return AppLogger._loggers[name]

        AppLogger._ensure_log_dir()

        # crear logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # evitar duplicar handlers si el logger ya existe
        if logger.handlers:
            return logger

        # formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # handler para archivo general
        general_file = os.path.join(AppLogger._log_dir, 'app.log')
        file_handler = RotatingFileHandler(
            general_file,
            maxBytes=AppLogger._max_bytes,
            backupCount=AppLogger._backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # handler para errores
        error_file = os.path.join(AppLogger._log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=AppLogger._max_bytes,
            backupCount=AppLogger._backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # handler para consola (solo WARNING y superiores)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)

        # agregar handlers al logger
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        # guardar en cache
        AppLogger._loggers[name] = logger

        return logger

    @staticmethod
    def log_exception(logger, message, exc_info=True):
        # registra una excepcion con su stack trace
        logger.error(message, exc_info=exc_info)

    @staticmethod
    def log_db_operation(logger, operation, table, record_id=None, details=None):
        # registra operaciones de base de datos
        msg = f"DB {operation}: {table}"
        if record_id:
            msg += f" [ID: {record_id}]"
        if details:
            msg += f" - {details}"
        logger.info(msg)

    @staticmethod
    def _filter_sensitive_data(data):
        # filtra datos sensibles de diccionarios y objetos
        if data is None:
            return None

        # lista de campos sensibles
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
                # si la clave contiene palabra sensible, ocultar valor
                if any(sensitive in key_lower for sensitive in sensitive_fields):
                    filtered[key] = '***HIDDEN***'
                elif isinstance(value, (dict, list)):
                    filtered[key] = AppLogger._filter_sensitive_data(value)
                else:
                    filtered[key] = value
            return filtered
        elif isinstance(data, list):
            return [AppLogger._filter_sensitive_data(item) for item in data]
        else:
            return data

    @staticmethod
    def log_service_call(logger, service, method, params=None):
        # registra llamadas a servicios sin exponer datos sensibles
        msg = f"Service call: {service}.{method}"
        if params:
            safe_params = AppLogger._filter_sensitive_data(params)
            msg += f" - params: {safe_params}"
        logger.debug(msg)

    @staticmethod
    def log_auth_attempt(logger, email, success, reason=None):
        # registra intentos de autenticacion
        status = "exitoso" if success else "fallido"
        msg = f"Intento de login {status} para: {email}"
        if reason and not success:
            msg += f" - Razon: {reason}"
        if success:
            logger.info(msg)
        else:
            logger.warning(msg)
