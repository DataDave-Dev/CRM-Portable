# tests unitarios para servicio de notas de empresa

import sys
import os
# agregar directorio raiz al path para imports cuando se ejecuta directamente
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import Mock, patch
from app.services.nota_empresa_service import NotaEmpresaService
from app.models.NotaEmpresa import NotaEmpresa


class TestNotaEmpresaService:
    # tests del servicio de notas de empresa

    @pytest.fixture
    def mock_repo(self):
        # mock del repositorio de notas de empresa
        with patch('app.services.nota_empresa_service.NotaEmpresaRepository') as mock:
            yield mock.return_value

    @pytest.fixture
    def service(self, mock_repo):
        # instancia del servicio con repositorio mockeado
        return NotaEmpresaService()

    def test_obtener_por_empresa_exitoso(self, service, mock_repo):
        # test de obtener notas por empresa
        notas_mock = [
            NotaEmpresa(
                nota_id=1,
                empresa_id=1,
                titulo="Test Nota",
                contenido="Contenido de prueba",
                es_privada=0,
                creado_por=1
            )
        ]

        mock_repo.find_by_empresa.return_value = notas_mock

        notas, error = service.obtener_por_empresa(1)

        assert error is None
        assert notas is not None
        assert len(notas) == 1
        assert notas[0].titulo == "Test Nota"

    def test_obtener_por_empresa_error(self, service, mock_repo):
        # test de error al obtener notas
        mock_repo.find_by_empresa.side_effect = Exception("Error de conexion")

        notas, error = service.obtener_por_empresa(1)

        assert notas is None
        assert "Error al obtener notas" in error

    def test_crear_nota_exitoso(self, service, mock_repo):
        # test de crear nota correctamente
        mock_repo.create.return_value = 1

        datos = {
            "empresa_id": 1,
            "titulo": "Nueva Nota",
            "contenido": "Contenido de la nota",
            "es_privada": 0
        }

        nota, error = service.crear_nota(datos, 1)

        assert error is None
        assert nota is not None
        assert nota.nota_id == 1
        assert nota.titulo == "Nueva Nota"
        mock_repo.create.assert_called_once()

    def test_crear_nota_sin_contenido(self, service, mock_repo):
        # test de crear nota sin contenido
        datos = {
            "empresa_id": 1,
            "titulo": "Nota sin contenido",
            "contenido": "",
            "es_privada": 0
        }

        nota, error = service.crear_nota(datos, 1)

        assert nota is None
        assert error == "El contenido de la nota es requerido"

    def test_crear_nota_sin_empresa_id(self, service, mock_repo):
        # test de crear nota sin empresa_id
        datos = {
            "titulo": "Nota sin empresa",
            "contenido": "Contenido valido",
            "es_privada": 0
        }

        nota, error = service.crear_nota(datos, 1)

        assert nota is None
        assert error == "El ID de la empresa es requerido"

    def test_actualizar_nota_exitoso(self, service, mock_repo):
        # test de actualizar nota correctamente
        datos = {
            "titulo": "Nota Actualizada",
            "contenido": "Contenido actualizado",
            "es_privada": 1
        }

        nota, error = service.actualizar_nota(1, datos)

        assert error is None
        assert nota is not None
        assert nota.titulo == "Nota Actualizada"
        assert nota.es_privada == 1
        mock_repo.update.assert_called_once()

    def test_actualizar_nota_sin_contenido(self, service, mock_repo):
        # test de actualizar nota sin contenido
        datos = {
            "titulo": "Titulo",
            "contenido": "   ",
            "es_privada": 0
        }

        nota, error = service.actualizar_nota(1, datos)

        assert nota is None
        assert error == "El contenido de la nota es requerido"

    def test_eliminar_nota_exitoso(self, service, mock_repo):
        # test de eliminar nota correctamente
        resultado, error = service.eliminar_nota(1)

        assert error is None
        assert resultado is True
        mock_repo.delete.assert_called_once_with(1)

    def test_eliminar_nota_error(self, service, mock_repo):
        # test de error al eliminar nota
        mock_repo.delete.side_effect = Exception("Error de base de datos")

        resultado, error = service.eliminar_nota(1)

        assert resultado is False
        assert "Error al eliminar nota" in error
