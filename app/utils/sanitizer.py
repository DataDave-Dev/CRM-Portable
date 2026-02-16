# utilidades para sanitizacion y validacion de datos

import re
import html


class Sanitizer:
    # limites de longitud para campos
    MAX_TITULO_LENGTH = 200
    MAX_CONTENIDO_LENGTH = 5000
    MAX_NOMBRE_LENGTH = 100
    MAX_EMAIL_LENGTH = 254
    MAX_TELEFONO_LENGTH = 20

    @staticmethod
    def sanitize_html(text):
        # escapa caracteres HTML para prevenir XSS
        if not text:
            return text
        return html.escape(str(text))

    @staticmethod
    def sanitize_string(text, max_length=None):
        # limpia y valida una cadena de texto
        if not text:
            return text

        # remover espacios extra
        cleaned = " ".join(str(text).split())

        # escapar HTML
        cleaned = html.escape(cleaned)

        # truncar si excede longitud maxima
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned

    @staticmethod
    def sanitize_email(email):
        # valida y limpia un email
        if not email:
            return None

        email = email.strip().lower()

        # patron basico de validacion de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return None

        if len(email) > Sanitizer.MAX_EMAIL_LENGTH:
            return None

        return email

    @staticmethod
    def sanitize_phone(phone):
        # limpia un numero de telefono
        if not phone:
            return None

        # remover caracteres no numericos excepto +, -, (, ), espacios
        cleaned = re.sub(r'[^0-9+\-() ]', '', str(phone))
        cleaned = " ".join(cleaned.split())

        if len(cleaned) > Sanitizer.MAX_TELEFONO_LENGTH:
            cleaned = cleaned[:Sanitizer.MAX_TELEFONO_LENGTH]

        return cleaned if cleaned else None

    @staticmethod
    def validate_length(text, min_length=None, max_length=None):
        # valida la longitud de un texto
        if not text:
            return min_length is None or min_length == 0

        text_length = len(str(text))

        if min_length is not None and text_length < min_length:
            return False

        if max_length is not None and text_length > max_length:
            return False

        return True

    @staticmethod
    def truncate(text, max_length, suffix="..."):
        # trunca un texto a una longitud maxima
        if not text or len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix
