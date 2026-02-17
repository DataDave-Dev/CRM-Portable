# tests unitarios para servicio de notas de contacto

import sys
import os
# agregar directorio raiz al path para imports cuando se ejecuta directamente
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import Mock, patch
from app.services.nota_contacto_service import NotaContactoService
from app.models.NotaContacto import NotaContacto


class TestNotaContactoService:
    # tests del servicio de notas de contacto

    @pytest.fixture
    def mock_repo(self):
        # mock del repositorio de notas de contacto
        with patch('app.services.nota_contacto_service.NotaContactoRepository') as mock:
            yield mock.return_value

    @pytest.fixture
    def service(self, mock_repo):
        # instancia del servicio con repositorio mockeado
        return NotaContactoService()

    def test_obtener_por_contacto_exitoso(self, service, mock_repo):
        # test de obtener notas por contacto
        notas_mock = [
            NotaContacto(
                nota_id=1,
                contacto_id=1,
                titulo="Test Nota",
                contenido="Contenido de prueba",
                es_privada=0,
                creado_por=1
            )
        ]

        mock_repo.find_by_contacto.return_value = notas_mock

        notas, error = service.obtener_por_contacto(1)

        assert error is None
        assert notas is not None
        assert len(notas) == 1
        assert notas[0].titulo == "Test Nota"

    def test_obtener_por_contacto_error(self, service, mock_repo):
        # test de error al obtener notas
        mock_repo.find_by_contacto.side_effect = Exception("Error de conexion")

        notas, error = service.obtener_por_contacto(1)

        assert notas is None
        assert error is not None  # el mensaje es sanitizado

    def test_crear_nota_exitoso(self, service, mock_repo):
        # test de crear nota correctamente
        mock_repo.create.return_value = 1

        datos = {
            "contacto_id": 1,
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
            "contacto_id": 1,
            "titulo": "Nota sin contenido",
            "contenido": "",
            "es_privada": 0
        }

        nota, error = service.crear_nota(datos, 1)

        assert nota is None
        assert error == "El contenido de la nota es requerido"

    def test_crear_nota_sin_contacto_id(self, service, mock_repo):
        # test de crear nota sin contacto_id
        datos = {
            "titulo": "Nota sin contacto",
            "contenido": "Contenido valido",
            "es_privada": 0
        }

        nota, error = service.crear_nota(datos, 1)

        assert nota is None
        assert error == "El ID del contacto es requerido"

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
        assert error is not None  # el mensaje es sanitizado
