"""
Validadores reutilizables para toda la aplicacion CRM.

Este modulo provee funciones de validacion que se pueden usar en cualquier
capa de la aplicacion (servicios, vistas, etc.) para verificar el formato
de datos antes de guardarlos en la base de datos.

Convencion de retorno:
    Todos los metodos de Validator retornan:
    - None: si el valor es valido (sin error)
    - str:  mensaje de error en espanol si el valor es invalido

Ejemplo de uso en un servicio:
    from app.utils.validators import Validator

    error = Validator.validate_email(datos.get("email"))
    if error:
        return None, error  # retornar el mensaje de error al llamador

Nota sobre ValidationError:
    La clase ValidationError existe para uso con la sintaxis de excepciones
    cuando se prefiere raise en lugar del patron de retorno (None, error).
    En los servicios del proyecto se usa el patron de retorno de tupla.
"""

import re
from typing import Optional


class ValidationError(Exception):
    """
    Excepcion personalizada para errores de validacion.

    Se puede usar cuando se prefiere el patron de excepciones:
        raise ValidationError("El email no es valido")
    En lugar del patron de tupla:
        return None, "El email no es valido"

    En el codigo actual del proyecto se usa principalmente el patron de tupla,
    pero esta clase esta disponible para uso futuro o en contextos donde
    las excepciones sean mas convenientes.
    """
    pass


class Validator:
    """
    Coleccion de metodos estaticos de validacion para campos comunes del CRM.

    Todos los metodos son estaticos (@staticmethod), por lo que se llaman
    directamente sobre la clase sin instanciarla:
        error = Validator.validate_email("usuario@ejemplo.com")

    Patrones de expresion regular (regex):
        Los patrones se definen como constantes de clase para evitar compilarlos
        en cada llamada. Python cachea las expresiones regulares, pero tenerlos
        como constantes mejora la legibilidad.
    """

    # Patron de email: usuario@dominio.extension
    # - ^[a-zA-Z0-9._%+-]+   : parte local (antes del @): letras, numeros, punto, guion, etc.
    # - @                     : arroba (literal)
    # - [a-zA-Z0-9.-]+        : dominio: letras, numeros, punto, guion
    # - \.                    : punto literal (escapado porque . en regex significa "cualquier caracter")
    # - [a-zA-Z]{2,}$         : extension: al menos 2 letras (.com, .mx, .org, .info, etc.)
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Patron de telefono: exactamente 10 digitos numericos (formato mexicano)
    # No permite espacios, guiones ni parentesis; solo digitos puros.
    # Ej. valido: "8112345678", invalido: "811-234-5678"
    PHONE_PATTERN = r"^\d{10}$"

    # Patron de codigo postal: exactamente 5 digitos (codigo postal mexicano)
    POSTAL_CODE_PATTERN = r"^\d{5}$"

    # Patron de RFC mexicano:
    # - [A-ZÑ&]{3,4}  : 3 o 4 letras iniciales (incluye Ñ y &)
    # - \d{6}         : 6 digitos de la fecha de nacimiento/constitucion (AAMMDD)
    # - [A-Z0-9]{3}   : 3 caracteres homoclave
    RFC_PATTERN = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"

    # Patron de URL: debe empezar con http:// o https://
    # Acepta subdominios, rutas, parametros de query y fragmentos.
    URL_PATTERN = r"^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$"

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """
        Valida el formato de una direccion de correo electronico.

        Parametros:
            email: Cadena a validar. Si esta vacia o es None, se considera error.

        Returns:
            None si el email es valido, o un str con el mensaje de error.
        """
        if not email:
            return "El email es requerido"
        if not re.match(Validator.EMAIL_PATTERN, email):
            return "El formato del email no es válido"
        return None

    @staticmethod
    def validate_phone(phone: str, required: bool = False) -> Optional[str]:
        """
        Valida un numero de telefono de 10 digitos.

        Parametros:
            phone   : Numero de telefono a validar. Se espera solo digitos, sin espacios.
            required: Si True, un telefono vacio se considera error.
                      Si False (default), un telefono vacio se acepta (campo opcional).

        Returns:
            None si es valido, o un str con el mensaje de error.
        """
        if not phone:
            # Si el campo esta vacio, verificar si era requerido
            return "El teléfono es requerido" if required else None
        if not re.match(Validator.PHONE_PATTERN, phone):
            return "El teléfono debe contener exactamente 10 dígitos"
        return None

    @staticmethod
    def validate_postal_code(code: str, required: bool = False) -> Optional[str]:
        """
        Valida un codigo postal de 5 digitos (formato mexicano).

        Parametros:
            code    : Codigo postal a validar.
            required: Si True, un codigo vacio es error. Si False, es opcional.

        Returns:
            None si es valido, o un str con el mensaje de error.
        """
        if not code:
            return "El código postal es requerido" if required else None
        if not re.match(Validator.POSTAL_CODE_PATTERN, code):
            return "El código postal debe contener 5 dígitos"
        return None

    @staticmethod
    def validate_rfc(rfc: str, required: bool = False) -> Optional[str]:
        """
        Valida el formato del RFC mexicano (Registro Federal de Contribuyentes).

        El RFC tiene formato diferente para personas fisicas (13 caracteres)
        y morales/empresas (12 caracteres). El patron acepta ambos.
        La validacion se hace en mayusculas (.upper()) para ser case-insensitive.

        Parametros:
            rfc     : RFC a validar.
            required: Si True, un RFC vacio es error. Si False, es opcional.

        Returns:
            None si es valido, o un str con el mensaje de error.
        """
        if not rfc:
            return "El RFC es requerido" if required else None
        if not re.match(Validator.RFC_PATTERN, rfc.upper()):
            return "El RFC debe tener entre 12 y 13 caracteres alfanuméricos"
        return None

    @staticmethod
    def validate_url(url: str, required: bool = False) -> Optional[str]:
        """
        Valida el formato de una URL (debe iniciar con http:// o https://).

        Parametros:
            url     : URL a validar.
            required: Si True, una URL vacia es error. Si False, es opcional.

        Returns:
            None si es valida, o un str con el mensaje de error.
        """
        if not url:
            return "La URL es requerida" if required else None
        if not re.match(Validator.URL_PATTERN, url):
            return "El formato de la URL no es válido"
        return None

    @staticmethod
    def validate_length(value: str, min_len: int = None, max_len: int = None,
                        field_name: str = "Campo") -> Optional[str]:
        """
        Valida la longitud de un texto.

        Parametros:
            value     : Texto a validar.
            min_len   : Longitud minima aceptada (inclusive). None = sin minimo.
            max_len   : Longitud maxima aceptada (inclusive). None = sin maximo.
            field_name: Nombre del campo para incluirlo en el mensaje de error.

        Returns:
            None si la longitud es valida, o un str con el mensaje de error.
        """
        if min_len and len(value) < min_len:
            return f"{field_name} debe tener al menos {min_len} caracteres"
        if max_len and len(value) > max_len:
            return f"{field_name} no puede exceder {max_len} caracteres"
        return None

    @staticmethod
    def validate_numeric_range(value: int, min_val: int = None, max_val: int = None,
                               field_name: str = "Valor") -> Optional[str]:
        """
        Valida que un valor numerico este dentro de un rango dado.

        Parametros:
            value     : Numero a validar.
            min_val   : Valor minimo aceptado (inclusive). None = sin minimo.
            max_val   : Valor maximo aceptado (inclusive). None = sin maximo.
            field_name: Nombre del campo para el mensaje de error.

        Returns:
            None si el valor esta en rango, o un str con el mensaje de error.
        """
        if min_val is not None and value < min_val:
            return f"{field_name} debe ser al menos {min_val}"
        if max_val is not None and value > max_val:
            return f"{field_name} no puede exceder {max_val}"
        return None

    @staticmethod
    def validate_password_strength(password: str) -> Optional[str]:
        """
        Valida la fortaleza de una contrasenia.

        Reglas de seguridad aplicadas:
        1. Minimo 8 caracteres.
        2. Al menos una letra mayuscula (A-Z).
        3. Al menos una letra minuscula (a-z).
        4. Al menos un digito numerico (0-9).
        5. No puede ser una contrasenia demasiado comun (lista negra).

        Estas reglas son un estandar minimo de seguridad. Contrasenias mas
        largas o con caracteres especiales son mas seguras, pero no se fuerzan
        para no frustrar al usuario con requisitos excesivos.

        Parametros:
            password: Contrasenia en texto plano a validar.
                      NUNCA guardar la contrasenia en texto plano; solo validarla
                      aqui antes de hashearla con bcrypt.

        Returns:
            None si la contrasenia cumple todos los requisitos, o un str con
            el primer requisito que no cumple.
        """
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres"

        # re.search busca el patron en cualquier parte de la cadena (no solo al inicio)
        if not re.search(r'[A-Z]', password):
            return "La contraseña debe contener al menos una mayúscula"

        if not re.search(r'[a-z]', password):
            return "La contraseña debe contener al menos una minúscula"

        if not re.search(r'[0-9]', password):
            return "La contraseña debe contener al menos un número"

        # Lista negra de contrasenias comunes que deben rechazarse aunque cumplan los demas requisitos
        # Estas son las contrasenias mas usadas en brechas de seguridad conocidas
        common_passwords = {'password', 'admin123', '12345678', 'qwerty123', 'password123'}
        if password.lower() in common_passwords:
            return "Contraseña demasiado común, elige una más segura"

        return None  # todos los requisitos cumplidos
