# tests unitarios para el modulo de sanitizacion

import pytest
from app.utils.sanitizer import Sanitizer


class TestSanitizeHtml:

    def test_escapa_menor_que(self):
        assert Sanitizer.sanitize_html("<b>texto</b>") == "&lt;b&gt;texto&lt;/b&gt;"

    def test_escapa_ampersand(self):
        assert Sanitizer.sanitize_html("Tom & Jerry") == "Tom &amp; Jerry"

    def test_escapa_comillas(self):
        result = Sanitizer.sanitize_html('"hola"')
        assert "&quot;" in result

    def test_escapa_xss(self):
        result = Sanitizer.sanitize_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_texto_sin_html_sin_cambios(self):
        assert Sanitizer.sanitize_html("texto normal") == "texto normal"

    def test_none_retorna_none(self):
        assert Sanitizer.sanitize_html(None) is None

    def test_vacio_retorna_vacio(self):
        assert Sanitizer.sanitize_html("") == ""


class TestSanitizeString:

    def test_quita_espacios_extremos(self):
        result = Sanitizer.sanitize_string("  hola mundo  ")
        assert result == "hola mundo"

    def test_colapsa_espacios_internos(self):
        result = Sanitizer.sanitize_string("hola   mundo   como   estas")
        assert result == "hola mundo como estas"

    def test_escapa_html(self):
        result = Sanitizer.sanitize_string("<b>texto</b>")
        assert "<b>" not in result

    def test_trunca_al_limite(self):
        texto = "A" * 20
        result = Sanitizer.sanitize_string(texto, max_length=10)
        assert len(result) == 10

    def test_no_trunca_si_cabe(self):
        result = Sanitizer.sanitize_string("corto", max_length=100)
        assert result == "corto"

    def test_none_retorna_none(self):
        assert Sanitizer.sanitize_string(None) is None

    def test_vacio_retorna_vacio(self):
        assert Sanitizer.sanitize_string("") == ""


class TestSanitizeEmail:

    def test_email_valido_minusculas(self):
        result = Sanitizer.sanitize_email("Usuario@Empresa.COM")
        assert result == "usuario@empresa.com"

    def test_email_quita_espacios(self):
        result = Sanitizer.sanitize_email("  user@example.com  ")
        assert result == "user@example.com"

    def test_email_invalido_retorna_none(self):
        assert Sanitizer.sanitize_email("no-es-email") is None

    def test_email_sin_arroba_retorna_none(self):
        assert Sanitizer.sanitize_email("user.example.com") is None

    def test_email_none_retorna_none(self):
        assert Sanitizer.sanitize_email(None) is None

    def test_email_vacio_retorna_none(self):
        assert Sanitizer.sanitize_email("") is None

    def test_email_demasiado_largo_retorna_none(self):
        email_largo = "a" * 250 + "@b.com"  # > 254 chars
        assert Sanitizer.sanitize_email(email_largo) is None


class TestSanitizePhone:

    def test_telefono_limpio_sin_cambios(self):
        result = Sanitizer.sanitize_phone("8112345678")
        assert result == "8112345678"

    def test_telefono_con_guiones(self):
        result = Sanitizer.sanitize_phone("811-234-5678")
        assert result is not None
        # los guiones son validos y deben conservarse
        assert "811" in result

    def test_telefono_con_parentesis(self):
        result = Sanitizer.sanitize_phone("(811) 234-5678")
        assert result is not None

    def test_telefono_elimina_letras(self):
        result = Sanitizer.sanitize_phone("81abc12345")
        # las letras deben ser eliminadas
        assert result is not None
        assert "a" not in result
        assert "b" not in result

    def test_telefono_none_retorna_none(self):
        assert Sanitizer.sanitize_phone(None) is None

    def test_telefono_vacio_retorna_none(self):
        assert Sanitizer.sanitize_phone("") is None

    def test_telefono_solo_letras_retorna_none(self):
        result = Sanitizer.sanitize_phone("abcdefghij")
        assert result is None

    def test_telefono_muy_largo_truncado(self):
        telefono_largo = "8" * 30
        result = Sanitizer.sanitize_phone(telefono_largo)
        assert len(result) <= Sanitizer.MAX_TELEFONO_LENGTH


class TestValidateLength:

    def test_texto_dentro_del_rango(self):
        assert Sanitizer.validate_length("hola", min_length=2, max_length=10) is True

    def test_texto_muy_corto(self):
        assert Sanitizer.validate_length("ab", min_length=3) is False

    def test_texto_muy_largo(self):
        assert Sanitizer.validate_length("hola mundo", max_length=5) is False

    def test_texto_exactamente_minimo(self):
        assert Sanitizer.validate_length("abc", min_length=3, max_length=10) is True

    def test_texto_exactamente_maximo(self):
        assert Sanitizer.validate_length("abcde", min_length=1, max_length=5) is True

    def test_vacio_sin_minimo(self):
        assert Sanitizer.validate_length("", min_length=None) is True

    def test_vacio_con_minimo_cero(self):
        assert Sanitizer.validate_length("", min_length=0) is True

    def test_vacio_con_minimo_positivo(self):
        assert Sanitizer.validate_length("", min_length=1) is False

    def test_none_sin_minimo(self):
        assert Sanitizer.validate_length(None, min_length=None) is True


class TestTruncate:

    def test_texto_corto_sin_cambios(self):
        result = Sanitizer.truncate("hola", 20)
        assert result == "hola"

    def test_texto_largo_truncado_con_puntos(self):
        result = Sanitizer.truncate("Esta es una descripcion muy larga", 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_texto_exactamente_al_limite(self):
        result = Sanitizer.truncate("12345", 5)
        assert result == "12345"

    def test_sufijo_personalizado(self):
        result = Sanitizer.truncate("texto muy largo aqui", 10, suffix="…")
        assert result.endswith("…")
        assert len(result) == 10

    def test_none_retorna_none(self):
        assert Sanitizer.truncate(None, 10) is None

    def test_vacio_retorna_vacio(self):
        assert Sanitizer.truncate("", 10) == ""

    def test_sufijo_por_defecto_tres_puntos(self):
        result = Sanitizer.truncate("abcdefghijklmnop", 10)
        assert result[-3:] == "..."
