# tests unitarios para modulo de validaciones

import pytest
from app.utils.validators import Validator


class TestEmailValidation:
    # tests de validacion de email

    def test_email_valido(self):
        # emails validos deben pasar
        assert Validator.validate_email("user@example.com") is None
        assert Validator.validate_email("test.user@domain.co") is None
        assert Validator.validate_email("admin123@company.mx") is None

    def test_email_invalido(self):
        # emails invalidos deben retornar mensaje de error
        assert Validator.validate_email("invalid") is not None
        assert Validator.validate_email("@example.com") is not None
        assert Validator.validate_email("user@") is not None
        assert Validator.validate_email("user@domain") is not None

    def test_email_vacio(self):
        # email vacio debe retornar error
        assert Validator.validate_email("") is not None
        assert Validator.validate_email(None) is not None


class TestPhoneValidation:
    # tests de validacion de telefono

    def test_telefono_valido(self):
        # telefonos de 10 digitos deben pasar
        assert Validator.validate_phone("8112345678") is None
        assert Validator.validate_phone("5512345678") is None

    def test_telefono_invalido(self):
        # telefonos con formato incorrecto deben retornar error
        assert Validator.validate_phone("123") is not None
        assert Validator.validate_phone("12345678901") is not None
        assert Validator.validate_phone("abcdefghij") is not None

    def test_telefono_opcional(self):
        # telefono vacio debe ser valido si no es requerido
        assert Validator.validate_phone("", required=False) is None
        # telefono vacio debe ser invalido si es requerido
        assert Validator.validate_phone("", required=True) is not None


class TestPostalCodeValidation:
    # tests de validacion de codigo postal

    def test_codigo_postal_valido(self):
        # codigos de 5 digitos deben pasar
        assert Validator.validate_postal_code("64000") is None
        assert Validator.validate_postal_code("12345") is None

    def test_codigo_postal_invalido(self):
        # codigos con formato incorrecto deben retornar error
        assert Validator.validate_postal_code("123") is not None
        assert Validator.validate_postal_code("123456") is not None
        assert Validator.validate_postal_code("abcde") is not None

    def test_codigo_postal_opcional(self):
        # codigo vacio debe ser valido si no es requerido
        assert Validator.validate_postal_code("", required=False) is None
        # codigo vacio debe ser invalido si es requerido
        assert Validator.validate_postal_code("", required=True) is not None


class TestRFCValidation:
    # tests de validacion de RFC mexicano

    def test_rfc_valido(self):
        # RFCs validos deben pasar
        assert Validator.validate_rfc("VECJ880326XXX") is None
        assert Validator.validate_rfc("GODE561231GR8") is None
        assert Validator.validate_rfc("ABC123456789") is None

    def test_rfc_invalido(self):
        # RFCs con formato incorrecto deben retornar error
        assert Validator.validate_rfc("ABC") is not None
        assert Validator.validate_rfc("1234567890123") is not None
        assert Validator.validate_rfc("ABC-123-456") is not None

    def test_rfc_opcional(self):
        # RFC vacio debe ser valido si no es requerido
        assert Validator.validate_rfc("", required=False) is None
        # RFC vacio debe ser invalido si es requerido
        assert Validator.validate_rfc("", required=True) is not None


class TestURLValidation:
    # tests de validacion de URL

    def test_url_valida(self):
        # URLs validas deben pasar
        assert Validator.validate_url("http://example.com") is None
        assert Validator.validate_url("https://www.google.com") is None
        assert Validator.validate_url("https://domain.com/path?query=value") is None

    def test_url_invalida(self):
        # URLs invalidas deben retornar error
        assert Validator.validate_url("invalid") is not None
        assert Validator.validate_url("ftp://example.com") is not None
        assert Validator.validate_url("www.example.com") is not None

    def test_url_opcional(self):
        # URL vacia debe ser valida si no es requerida
        assert Validator.validate_url("", required=False) is None
        # URL vacia debe ser invalida si es requerida
        assert Validator.validate_url("", required=True) is not None


class TestLengthValidation:
    # tests de validacion de longitud de texto

    def test_longitud_valida(self):
        # textos dentro del rango deben pasar
        assert Validator.validate_length("test", min_len=2, max_len=10) is None
        assert Validator.validate_length("hello", min_len=5, max_len=5) is None

    def test_longitud_minima_invalida(self):
        # texto muy corto debe retornar error
        assert Validator.validate_length("ab", min_len=3) is not None

    def test_longitud_maxima_invalida(self):
        # texto muy largo debe retornar error
        assert Validator.validate_length("hello world", max_len=5) is not None


class TestNumericRangeValidation:
    # tests de validacion de rango numerico

    def test_rango_valido(self):
        # numeros dentro del rango deben pasar
        assert Validator.validate_numeric_range(5, min_val=1, max_val=10) is None
        assert Validator.validate_numeric_range(100, min_val=100, max_val=100) is None

    def test_rango_minimo_invalido(self):
        # numero menor al minimo debe retornar error
        assert Validator.validate_numeric_range(0, min_val=1) is not None

    def test_rango_maximo_invalido(self):
        # numero mayor al maximo debe retornar error
        assert Validator.validate_numeric_range(11, max_val=10) is not None


class TestPasswordStrengthValidation:
    # tests de validacion de fortaleza de contraseña

    def test_contrasena_fuerte(self):
        # contraseñas fuertes deben pasar
        assert Validator.validate_password_strength("Password123!") is None
        assert Validator.validate_password_strength("Strong1Pass") is None
        assert Validator.validate_password_strength("MyP@ssw0rd") is None

    def test_contrasena_muy_corta(self):
        # contraseña menor a 8 caracteres debe retornar error
        assert Validator.validate_password_strength("Pass1") is not None

    def test_contrasena_sin_mayuscula(self):
        # contraseña sin mayuscula debe retornar error
        assert Validator.validate_password_strength("password123") is not None

    def test_contrasena_sin_minuscula(self):
        # contraseña sin minuscula debe retornar error
        assert Validator.validate_password_strength("PASSWORD123") is not None

    def test_contrasena_sin_numero(self):
        # contraseña sin numero debe retornar error
        assert Validator.validate_password_strength("PasswordABC") is not None

    def test_contrasena_comun(self):
        # contraseñas comunes deben retornar error
        assert Validator.validate_password_strength("password") is not None
        assert Validator.validate_password_strength("admin123") is not None
        assert Validator.validate_password_strength("12345678") is not None
        assert Validator.validate_password_strength("Password123") is not None
