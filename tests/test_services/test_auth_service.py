# tests unitarios para servicio de autenticacion

import pytest
from unittest.mock import Mock, patch
import bcrypt
from app.services.auth_service import AuthService
from app.models.Usuario import Usuario


class TestAuthService:
    # tests del servicio de autenticacion

    @pytest.fixture
    def mock_repo(self):
        # mock del repositorio de usuarios
        with patch('app.services.auth_service.UsuarioRepository') as mock:
            yield mock.return_value

    @pytest.fixture
    def service(self, mock_repo):
        # instancia del servicio con repositorio mockeado
        return AuthService()

    def test_login_exitoso(self, service, mock_repo):
        # test de login con credenciales correctas
        password = "Password123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usuario_mock = Usuario(
            usuario_id=1,
            nombre="Test",
            apellido_paterno="User",
            email="test@example.com",
            contrasena_hash=hashed,
            rol_id=1,
            activo=1
        )

        mock_repo.find_by_email.return_value = usuario_mock

        usuario, error = service.login("test@example.com", password)

        assert error is None
        assert usuario is not None
        assert usuario.email == "test@example.com"
        mock_repo.update_ultimo_acceso.assert_called_once()

    def test_login_email_no_existe(self, service, mock_repo):
        # test de login con email inexistente
        mock_repo.find_by_email.return_value = None

        usuario, error = service.login("noexiste@example.com", "Password123")

        assert usuario is None
        assert error == "Correo electrónico no encontrado"

    def test_login_contrasena_incorrecta(self, service, mock_repo):
        # test de login con contraseña incorrecta
        password_correcta = "Password123"
        hashed = bcrypt.hashpw(password_correcta.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usuario_mock = Usuario(
            usuario_id=1,
            nombre="Test",
            apellido_paterno="User",
            email="test@example.com",
            contrasena_hash=hashed,
            rol_id=1,
            activo=1
        )

        mock_repo.find_by_email.return_value = usuario_mock

        usuario, error = service.login("test@example.com", "PasswordIncorrecta")

        assert usuario is None
        assert error == "Contraseña incorrecta"
