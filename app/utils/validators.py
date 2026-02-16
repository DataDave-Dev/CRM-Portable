# funciones de validacion reutilizables para toda la aplicacion

import re
from typing import Optional


class ValidationError(Exception):
    # excepcion personalizada para errores de validacion
    pass


class Validator:
    # patrones regex para validaciones
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE_PATTERN = r"^\d{10}$"
    POSTAL_CODE_PATTERN = r"^\d{5}$"
    RFC_PATTERN = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"
    URL_PATTERN = r"^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$"

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        # valida formato de email, retorna None si valido o mensaje de error
        if not email:
            return "El email es requerido"
        if not re.match(Validator.EMAIL_PATTERN, email):
            return "El formato del email no es válido"
        return None

    @staticmethod
    def validate_phone(phone: str, required: bool = False) -> Optional[str]:
        # valida telefono (10 digitos)
        if not phone:
            return "El teléfono es requerido" if required else None
        if not re.match(Validator.PHONE_PATTERN, phone):
            return "El teléfono debe contener exactamente 10 dígitos"
        return None

    @staticmethod
    def validate_postal_code(code: str, required: bool = False) -> Optional[str]:
        # valida codigo postal (5 digitos)
        if not code:
            return "El código postal es requerido" if required else None
        if not re.match(Validator.POSTAL_CODE_PATTERN, code):
            return "El código postal debe contener 5 dígitos"
        return None

    @staticmethod
    def validate_rfc(rfc: str, required: bool = False) -> Optional[str]:
        # valida formato de RFC mexicano
        if not rfc:
            return "El RFC es requerido" if required else None
        if not re.match(Validator.RFC_PATTERN, rfc.upper()):
            return "El RFC debe tener entre 12 y 13 caracteres alfanuméricos"
        return None

    @staticmethod
    def validate_url(url: str, required: bool = False) -> Optional[str]:
        # valida formato de URL
        if not url:
            return "La URL es requerida" if required else None
        if not re.match(Validator.URL_PATTERN, url):
            return "El formato de la URL no es válido"
        return None

    @staticmethod
    def validate_length(value: str, min_len: int = None, max_len: int = None,
                       field_name: str = "Campo") -> Optional[str]:
        # valida longitud de texto
        if min_len and len(value) < min_len:
            return f"{field_name} debe tener al menos {min_len} caracteres"
        if max_len and len(value) > max_len:
            return f"{field_name} no puede exceder {max_len} caracteres"
        return None

    @staticmethod
    def validate_numeric_range(value: int, min_val: int = None, max_val: int = None,
                              field_name: str = "Valor") -> Optional[str]:
        # valida rango numerico
        if min_val is not None and value < min_val:
            return f"{field_name} debe ser al menos {min_val}"
        if max_val is not None and value > max_val:
            return f"{field_name} no puede exceder {max_val}"
        return None

    @staticmethod
    def validate_password_strength(password: str) -> Optional[str]:
        # valida fortaleza de contraseña (minimo 8 caracteres, mayusculas, minusculas, numeros)
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres"

        if not re.search(r'[A-Z]', password):
            return "La contraseña debe contener al menos una mayúscula"

        if not re.search(r'[a-z]', password):
            return "La contraseña debe contener al menos una minúscula"

        if not re.search(r'[0-9]', password):
            return "La contraseña debe contener al menos un número"

        # verificar contraseñas comunes
        common_passwords = {'password', 'admin123', '12345678', 'qwerty123', 'password123'}
        if password.lower() in common_passwords:
            return "Contraseña demasiado común, elige una más segura"

        return None
