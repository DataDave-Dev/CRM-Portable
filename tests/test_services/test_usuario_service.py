# tests unitarios para servicio de usuarios

import pytest
import bcrypt
from unittest.mock import Mock, patch
from app.services.usuario_service import UsuarioService
from app.models.Usuario import Usuario


class TestUsuarioService:

    @pytest.fixture
    def mock_repo(self):
        with patch('app.services.usuario_service.UsuarioRepository') as mock:
            instance = mock.return_value
            instance.email_exists.return_value = False
            yield instance

    @pytest.fixture
    def service(self, mock_repo):
        return UsuarioService()

    @pytest.fixture
    def datos_validos(self):
        return {
            "nombre": "Juan",
            "apellido_paterno": "Perez",
            "email": "juan@example.com",
            "contrasena": "Password123",
            "rol_id": 1,
        }

    # ==========================================
    # CREAR USUARIO - CAMPOS REQUERIDOS
    # ==========================================

    def test_crear_usuario_exitoso(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 1
        usuario, error = service.crear_usuario(datos_validos)
        assert error is None
        assert usuario is not None
        assert usuario.email == "juan@example.com"
        assert usuario.usuario_id == 1
        # verificar que la contrasena fue hasheada con bcrypt
        assert usuario.contrasena_hash.startswith("$2b$") or usuario.contrasena_hash.startswith("$2a$")

    def test_crear_usuario_sin_nombre(self, service, mock_repo, datos_validos):
        datos_validos["nombre"] = ""
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "nombre" in error.lower()

    def test_crear_usuario_nombre_none(self, service, mock_repo, datos_validos):
        datos_validos["nombre"] = None
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert error is not None

    def test_crear_usuario_sin_apellido(self, service, mock_repo, datos_validos):
        datos_validos["apellido_paterno"] = ""
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "apellido" in error.lower()

    def test_crear_usuario_sin_email(self, service, mock_repo, datos_validos):
        datos_validos["email"] = ""
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert error is not None

    def test_crear_usuario_sin_contrasena(self, service, mock_repo, datos_validos):
        datos_validos["contrasena"] = ""
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert error is not None

    def test_crear_usuario_sin_rol(self, service, mock_repo, datos_validos):
        datos_validos["rol_id"] = None
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "rol" in error.lower()

    # ==========================================
    # VALIDACIONES DE EMAIL
    # ==========================================

    def test_crear_usuario_email_invalido(self, service, mock_repo, datos_validos):
        datos_validos["email"] = "no-es-email"
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "email" in error.lower()

    def test_crear_usuario_email_sin_arroba(self, service, mock_repo, datos_validos):
        datos_validos["email"] = "juanexample.com"
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert error is not None

    def test_crear_usuario_email_duplicado(self, service, mock_repo, datos_validos):
        mock_repo.email_exists.return_value = True
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "ya" in error.lower()

    # ==========================================
    # VALIDACIONES DE CONTRASENA
    # ==========================================

    def test_crear_usuario_contrasena_muy_corta(self, service, mock_repo, datos_validos):
        datos_validos["contrasena"] = "Ab1"
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "8" in error

    def test_crear_usuario_contrasena_exactamente_8(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 2
        datos_validos["contrasena"] = "Abcde123"
        usuario, error = service.crear_usuario(datos_validos)
        assert error is None

    def test_crear_usuario_contrasena_hasheada_verificable(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 3
        password = "MiPassword99"
        datos_validos["contrasena"] = password
        usuario, error = service.crear_usuario(datos_validos)
        assert error is None
        # verificar que el hash es valido y corresponde a la contrasena original
        assert bcrypt.checkpw(password.encode("utf-8"), usuario.contrasena_hash.encode("utf-8"))

    # ==========================================
    # VALIDACIONES DE TELEFONO
    # ==========================================

    def test_crear_usuario_telefono_valido(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 4
        datos_validos["telefono"] = "8112345678"
        usuario, error = service.crear_usuario(datos_validos)
        assert error is None

    def test_crear_usuario_telefono_invalido(self, service, mock_repo, datos_validos):
        datos_validos["telefono"] = "812345"
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None
        assert "10" in error

    def test_crear_usuario_telefono_letras(self, service, mock_repo, datos_validos):
        datos_validos["telefono"] = "811234abcd"
        usuario, error = service.crear_usuario(datos_validos)
        assert usuario is None

    def test_crear_usuario_sin_telefono_es_valido(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 5
        # el telefono es opcional
        datos_validos.pop("telefono", None)
        usuario, error = service.crear_usuario(datos_validos)
        assert error is None

    # ==========================================
    # ACTUALIZAR USUARIO
    # ==========================================

    def test_actualizar_usuario_exitoso(self, service, mock_repo):
        datos = {
            "nombre": "Juan Carlos",
            "apellido_paterno": "Perez",
            "email": "juan@example.com",
            "rol_id": 2,
        }
        usuario, error = service.actualizar_usuario(1, datos)
        assert error is None
        assert usuario.nombre == "Juan Carlos"
        mock_repo.update.assert_called_once()

    def test_actualizar_usuario_sin_nombre(self, service, mock_repo):
        datos = {"nombre": "", "apellido_paterno": "Perez", "email": "juan@example.com", "rol_id": 1}
        usuario, error = service.actualizar_usuario(1, datos)
        assert usuario is None
        assert error is not None

    def test_actualizar_usuario_email_invalido(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "email": "invalido", "rol_id": 1}
        usuario, error = service.actualizar_usuario(1, datos)
        assert usuario is None
        assert "email" in error.lower()

    def test_actualizar_usuario_email_de_otro(self, service, mock_repo):
        mock_repo.email_exists.return_value = True
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "email": "otro@example.com", "rol_id": 1}
        usuario, error = service.actualizar_usuario(1, datos)
        assert usuario is None
        assert "otro" in error.lower()

    def test_actualizar_usuario_contrasena_muy_corta(self, service, mock_repo):
        datos = {
            "nombre": "Juan", "apellido_paterno": "Perez",
            "email": "juan@example.com", "rol_id": 1,
            "contrasena": "Corta1"
        }
        usuario, error = service.actualizar_usuario(1, datos)
        assert usuario is None
        assert "8" in error

    def test_actualizar_usuario_sin_contrasena_no_cambia(self, service, mock_repo):
        # si no se proporciona contrasena, no debe llamar update_password
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "email": "juan@example.com", "rol_id": 1}
        usuario, error = service.actualizar_usuario(1, datos)
        assert error is None
        mock_repo.update_password.assert_not_called()

    def test_actualizar_usuario_con_nueva_contrasena(self, service, mock_repo):
        datos = {
            "nombre": "Juan", "apellido_paterno": "Perez",
            "email": "juan@example.com", "rol_id": 1,
            "contrasena": "NuevaPass99"
        }
        usuario, error = service.actualizar_usuario(1, datos)
        assert error is None
        mock_repo.update_password.assert_called_once()

    def test_actualizar_usuario_error_bd(self, service, mock_repo):
        mock_repo.update.side_effect = Exception("Error de BD")
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "email": "juan@example.com", "rol_id": 1}
        usuario, error = service.actualizar_usuario(1, datos)
        assert usuario is None
        assert error is not None
