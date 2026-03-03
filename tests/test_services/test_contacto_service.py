# tests unitarios para servicio de contactos

import pytest
from unittest.mock import Mock, patch
from app.services.contacto_service import ContactoService
from app.models.Contacto import Contacto


class TestContactoService:

    @pytest.fixture
    def mock_repo(self):
        with patch('app.services.contacto_service.ContactoRepository') as mock:
            yield mock.return_value

    @pytest.fixture
    def service(self, mock_repo):
        return ContactoService()

    # ==========================================
    # CREAR CONTACTO - CAMPOS REQUERIDOS
    # ==========================================

    def test_crear_contacto_exitoso(self, service, mock_repo):
        mock_repo.create.return_value = 1
        datos = {"nombre": "Juan", "apellido_paterno": "Perez"}
        contacto, error = service.crear_contacto(datos, 1)
        assert error is None
        assert contacto is not None
        assert contacto.nombre == "Juan"
        assert contacto.contacto_id == 1
        mock_repo.create.assert_called_once()

    def test_crear_contacto_sin_nombre(self, service, mock_repo):
        datos = {"nombre": "", "apellido_paterno": "Perez"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error == "El nombre es requerido"

    def test_crear_contacto_sin_apellido(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": ""}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error == "El apellido paterno es requerido"

    # ==========================================
    # CREAR CONTACTO - VALIDACIONES DE EMAIL
    # ==========================================

    def test_crear_contacto_email_valido(self, service, mock_repo):
        mock_repo.create.return_value = 2
        datos = {"nombre": "Ana", "apellido_paterno": "Lopez", "email": "ana@empresa.com"}
        contacto, error = service.crear_contacto(datos, 1)
        assert error is None
        assert contacto.email == "ana@empresa.com"

    def test_crear_contacto_email_invalido(self, service, mock_repo):
        datos = {"nombre": "Ana", "apellido_paterno": "Lopez", "email": "no-es-email"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error == "El formato del email no es valido"

    def test_crear_contacto_email_sin_dominio(self, service, mock_repo):
        datos = {"nombre": "Ana", "apellido_paterno": "Lopez", "email": "ana@"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error is not None

    def test_crear_contacto_email_secundario_invalido(self, service, mock_repo):
        datos = {
            "nombre": "Ana", "apellido_paterno": "Lopez",
            "email": "ana@empresa.com", "email_secundario": "invalido"
        }
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error == "El formato del email secundario no es valido"

    # ==========================================
    # CREAR CONTACTO - VALIDACIONES DE TELEFONO
    # ==========================================

    def test_crear_contacto_telefono_valido(self, service, mock_repo):
        mock_repo.create.return_value = 3
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "telefono_celular": "8112345678"}
        contacto, error = service.crear_contacto(datos, 1)
        assert error is None

    def test_crear_contacto_telefono_muy_corto(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "telefono_celular": "12345"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert "10 digitos" in error

    def test_crear_contacto_telefono_con_letras(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "telefono_oficina": "81abcd1234"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert error is not None

    def test_crear_contacto_telefono_muy_largo(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "telefono_oficina": "81234567890"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None

    # ==========================================
    # CREAR CONTACTO - CODIGO POSTAL
    # ==========================================

    def test_crear_contacto_cp_valido(self, service, mock_repo):
        mock_repo.create.return_value = 4
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "codigo_postal": "64000"}
        contacto, error = service.crear_contacto(datos, 1)
        assert error is None

    def test_crear_contacto_cp_invalido(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "codigo_postal": "123"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert "5 digitos" in error

    def test_crear_contacto_cp_letras(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "codigo_postal": "ABCDE"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None

    # ==========================================
    # CREAR CONTACTO - FECHA NACIMIENTO
    # ==========================================

    def test_crear_contacto_fecha_valida(self, service, mock_repo):
        mock_repo.create.return_value = 5
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "fecha_nacimiento": "1990-05-15"}
        contacto, error = service.crear_contacto(datos, 1)
        assert error is None

    def test_crear_contacto_fecha_invalida(self, service, mock_repo):
        datos = {"nombre": "Juan", "apellido_paterno": "Perez", "fecha_nacimiento": "15/05/1990"}
        contacto, error = service.crear_contacto(datos, 1)
        assert contacto is None
        assert "AAAA-MM-DD" in error

    # ==========================================
    # OBTENER CONTACTOS
    # ==========================================

    def test_obtener_todos_exitoso(self, service, mock_repo):
        mock_repo.find_all.return_value = [
            Contacto(nombre="Juan", apellido_paterno="Perez")
        ]
        contactos, error = service.obtener_todos()
        assert error is None
        assert len(contactos) == 1

    def test_obtener_todos_error(self, service, mock_repo):
        mock_repo.find_all.side_effect = Exception("Error de BD")
        contactos, error = service.obtener_todos()
        assert contactos is None
        assert error is not None

    def test_obtener_por_id_exitoso(self, service, mock_repo):
        mock_repo.find_by_id.return_value = Contacto(contacto_id=1, nombre="Juan", apellido_paterno="Perez")
        contacto, error = service.obtener_por_id(1)
        assert error is None
        assert contacto is not None

    def test_obtener_por_id_error(self, service, mock_repo):
        mock_repo.find_by_id.side_effect = Exception("Error de BD")
        contacto, error = service.obtener_por_id(1)
        assert contacto is None
        assert error is not None

    # ==========================================
    # ACTUALIZAR CONTACTO
    # ==========================================

    def test_actualizar_contacto_exitoso(self, service, mock_repo):
        datos = {"nombre": "Juan Carlos", "apellido_paterno": "Perez"}
        contacto, error = service.actualizar_contacto(1, datos, 1)
        assert error is None
        assert contacto.nombre == "Juan Carlos"
        mock_repo.update.assert_called_once()

    def test_actualizar_contacto_sin_nombre(self, service, mock_repo):
        datos = {"nombre": "", "apellido_paterno": "Perez"}
        contacto, error = service.actualizar_contacto(1, datos, 1)
        assert contacto is None
        assert error == "El nombre es requerido"

    def test_actualizar_contacto_error_bd(self, service, mock_repo):
        mock_repo.update.side_effect = Exception("Error de BD")
        datos = {"nombre": "Juan", "apellido_paterno": "Perez"}
        contacto, error = service.actualizar_contacto(1, datos, 1)
        assert contacto is None
        assert error is not None

    # ==========================================
    # CONTAR TOTAL
    # ==========================================

    def test_contar_total_exitoso(self, service, mock_repo):
        mock_repo.count_all.return_value = 42
        total, error = service.contar_total()
        assert error is None
        assert total == 42

    def test_contar_total_error(self, service, mock_repo):
        mock_repo.count_all.side_effect = Exception("Error de BD")
        total, error = service.contar_total()
        assert total is None
        assert error is not None
