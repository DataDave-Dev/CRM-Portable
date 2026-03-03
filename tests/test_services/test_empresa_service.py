# tests unitarios para servicio de empresas

import pytest
from unittest.mock import Mock, patch
from app.services.empresa_service import EmpresaService
from app.models.Empresa import Empresa


class TestEmpresaService:

    @pytest.fixture
    def mock_repo(self):
        with patch('app.services.empresa_service.EmpresaRepository') as mock:
            instance = mock.return_value
            instance.rfc_exists.return_value = False
            yield instance

    @pytest.fixture
    def service(self, mock_repo):
        return EmpresaService()

    # ==========================================
    # CREAR EMPRESA - CAMPOS REQUERIDOS
    # ==========================================

    def test_crear_empresa_exitoso(self, service, mock_repo):
        mock_repo.create.return_value = 1
        datos = {"razon_social": "Acme Corp S.A."}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None
        assert empresa is not None
        assert empresa.razon_social == "Acme Corp S.A."
        assert empresa.empresa_id == 1

    def test_crear_empresa_sin_razon_social(self, service, mock_repo):
        datos = {"razon_social": ""}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert error == "La razon social es requerida"

    def test_crear_empresa_razon_social_espacios(self, service, mock_repo):
        datos = {"razon_social": "   "}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert error == "La razon social es requerida"

    # ==========================================
    # CREAR EMPRESA - VALIDACIONES RFC
    # ==========================================

    def test_crear_empresa_rfc_valido_12(self, service, mock_repo):
        mock_repo.create.return_value = 2
        datos = {"razon_social": "Empresa SA", "rfc": "ACM010101ABC"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_rfc_valido_13(self, service, mock_repo):
        mock_repo.create.return_value = 3
        datos = {"razon_social": "Empresa SA", "rfc": "GODE561231GR8"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_rfc_invalido_corto(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "rfc": "ABC123"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "12 o 13 caracteres" in error

    def test_crear_empresa_rfc_con_guiones(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "rfc": "ACM-010101-ABC"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert error is not None

    def test_crear_empresa_rfc_duplicado(self, service, mock_repo):
        mock_repo.rfc_exists.return_value = True
        datos = {"razon_social": "Empresa SA", "rfc": "ACM010101ABC"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "ya esta registrado" in error

    def test_crear_empresa_rfc_se_guarda_mayusculas(self, service, mock_repo):
        mock_repo.create.return_value = 4
        datos = {"razon_social": "Empresa SA", "rfc": "acm010101abc"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None
        assert empresa.rfc == "ACM010101ABC"

    # ==========================================
    # CREAR EMPRESA - EMAIL
    # ==========================================

    def test_crear_empresa_email_valido(self, service, mock_repo):
        mock_repo.create.return_value = 5
        datos = {"razon_social": "Empresa SA", "email": "contacto@empresa.com"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_email_invalido(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "email": "no-es-email"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "email" in error.lower()

    # ==========================================
    # CREAR EMPRESA - TELEFONO
    # ==========================================

    def test_crear_empresa_telefono_valido(self, service, mock_repo):
        mock_repo.create.return_value = 6
        datos = {"razon_social": "Empresa SA", "telefono": "8112345678"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_telefono_invalido(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "telefono": "8112345"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "10 digitos" in error

    def test_crear_empresa_telefono_letras(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "telefono": "811234abcd"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None

    # ==========================================
    # CREAR EMPRESA - CODIGO POSTAL
    # ==========================================

    def test_crear_empresa_cp_valido(self, service, mock_repo):
        mock_repo.create.return_value = 7
        datos = {"razon_social": "Empresa SA", "codigo_postal": "64000"}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_cp_invalido(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "codigo_postal": "640"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "5 digitos" in error

    # ==========================================
    # CREAR EMPRESA - INGRESO ANUAL
    # ==========================================

    def test_crear_empresa_ingreso_valido(self, service, mock_repo):
        mock_repo.create.return_value = 8
        datos = {"razon_social": "Empresa SA", "ingreso_anual_estimado": 1000000.0}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_ingreso_negativo(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "ingreso_anual_estimado": -5000}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "negativo" in error

    def test_crear_empresa_ingreso_no_numerico(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "ingreso_anual_estimado": "mucho"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "numero" in error

    # ==========================================
    # CREAR EMPRESA - NUMERO EMPLEADOS
    # ==========================================

    def test_crear_empresa_empleados_valido(self, service, mock_repo):
        mock_repo.create.return_value = 9
        datos = {"razon_social": "Empresa SA", "num_empleados": 50}
        empresa, error = service.crear_empresa(datos, 1)
        assert error is None

    def test_crear_empresa_empleados_negativos(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "num_empleados": -10}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "negativo" in error

    def test_crear_empresa_empleados_no_entero(self, service, mock_repo):
        datos = {"razon_social": "Empresa SA", "num_empleados": "muchos"}
        empresa, error = service.crear_empresa(datos, 1)
        assert empresa is None
        assert "entero" in error

    # ==========================================
    # ACTUALIZAR EMPRESA
    # ==========================================

    def test_actualizar_empresa_exitoso(self, service, mock_repo):
        datos = {"razon_social": "Acme Corp Actualizada"}
        empresa, error = service.actualizar_empresa(1, datos, 1)
        assert error is None
        assert empresa.razon_social == "Acme Corp Actualizada"
        mock_repo.update.assert_called_once()

    def test_actualizar_empresa_sin_razon_social(self, service, mock_repo):
        datos = {"razon_social": ""}
        empresa, error = service.actualizar_empresa(1, datos, 1)
        assert empresa is None
        assert error == "La razon social es requerida"

    def test_actualizar_empresa_rfc_duplicado_otra(self, service, mock_repo):
        mock_repo.rfc_exists.return_value = True
        datos = {"razon_social": "Empresa SA", "rfc": "ACM010101ABC"}
        empresa, error = service.actualizar_empresa(1, datos, 1)
        assert empresa is None
        assert "otra empresa" in error

    def test_actualizar_empresa_error_bd(self, service, mock_repo):
        mock_repo.update.side_effect = Exception("Error de BD")
        datos = {"razon_social": "Empresa SA"}
        empresa, error = service.actualizar_empresa(1, datos, 1)
        assert empresa is None
        assert error is not None

    # ==========================================
    # OBTENER EMPRESAS
    # ==========================================

    def test_obtener_todas_exitoso(self, service, mock_repo):
        mock_repo.find_all.return_value = [Empresa(razon_social="Empresa A")]
        empresas, error = service.obtener_todas()
        assert error is None
        assert len(empresas) == 1

    def test_obtener_todas_error(self, service, mock_repo):
        mock_repo.find_all.side_effect = Exception("Error de BD")
        empresas, error = service.obtener_todas()
        assert empresas is None
        assert error is not None

    def test_contar_total_exitoso(self, service, mock_repo):
        mock_repo.count_all.return_value = 10
        total, error = service.contar_total()
        assert error is None
        assert total == 10
