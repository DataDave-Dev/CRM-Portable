# tests unitarios para servicio de actividades

import pytest
from unittest.mock import Mock, patch
from app.services.actividad_service import ActividadService
from app.models.Actividad import Actividad


class TestActividadService:

    @pytest.fixture
    def mock_repo(self):
        with patch('app.services.actividad_service.ActividadRepository') as mock:
            yield mock.return_value

    @pytest.fixture
    def service(self, mock_repo):
        return ActividadService()

    @pytest.fixture
    def datos_validos(self):
        return {
            "tipo_actividad_id": 1,
            "asunto": "Llamada de seguimiento",
            "propietario_id": 1,
            "estado_actividad_id": 1,
        }

    # ==========================================
    # CREAR ACTIVIDAD - CAMPOS REQUERIDOS
    # ==========================================

    def test_crear_actividad_exitosa(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 1
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert error is None
        assert actividad is not None
        assert actividad.asunto == "Llamada de seguimiento"
        assert actividad.actividad_id == 1

    def test_crear_actividad_sin_tipo(self, service, mock_repo):
        datos = {"tipo_actividad_id": None, "asunto": "Llamada", "propietario_id": 1, "estado_actividad_id": 1}
        actividad, error = service.crear_actividad(datos, 1)
        assert actividad is None
        assert error == "El tipo de actividad es requerido"

    def test_crear_actividad_sin_asunto(self, service, mock_repo):
        datos = {"tipo_actividad_id": 1, "asunto": "", "propietario_id": 1, "estado_actividad_id": 1}
        actividad, error = service.crear_actividad(datos, 1)
        assert actividad is None
        assert error == "El asunto es requerido"

    def test_crear_actividad_asunto_muy_largo(self, service, mock_repo):
        datos = {
            "tipo_actividad_id": 1,
            "asunto": "A" * 256,
            "propietario_id": 1,
            "estado_actividad_id": 1,
        }
        actividad, error = service.crear_actividad(datos, 1)
        assert actividad is None
        assert "255" in error

    def test_crear_actividad_sin_propietario(self, service, mock_repo):
        datos = {"tipo_actividad_id": 1, "asunto": "Llamada", "propietario_id": None, "estado_actividad_id": 1}
        actividad, error = service.crear_actividad(datos, 1)
        assert actividad is None
        assert "propietario" in error.lower()

    def test_crear_actividad_sin_estado(self, service, mock_repo):
        datos = {"tipo_actividad_id": 1, "asunto": "Llamada", "propietario_id": 1, "estado_actividad_id": None}
        actividad, error = service.crear_actividad(datos, 1)
        assert actividad is None
        assert "estado" in error.lower()

    # ==========================================
    # VALIDACIONES DE DURACION
    # ==========================================

    def test_crear_actividad_duracion_valida(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 2
        datos_validos["duracion_minutos"] = "60"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert error is None
        assert actividad.duracion_minutos == 60

    def test_crear_actividad_duracion_negativa(self, service, mock_repo, datos_validos):
        datos_validos["duracion_minutos"] = "-30"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert actividad is None
        assert "negativa" in error

    def test_crear_actividad_duracion_no_entero(self, service, mock_repo, datos_validos):
        datos_validos["duracion_minutos"] = "media hora"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert actividad is None
        assert "entero" in error

    def test_crear_actividad_duracion_cero(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 3
        datos_validos["duracion_minutos"] = "0"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert error is None

    # ==========================================
    # VALIDACIONES DE FECHAS
    # ==========================================

    def test_crear_actividad_fecha_inicio_valida(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 4
        datos_validos["fecha_inicio"] = "2026-03-15"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert error is None

    def test_crear_actividad_fecha_inicio_invalida(self, service, mock_repo, datos_validos):
        datos_validos["fecha_inicio"] = "15-03-2026"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert actividad is None
        assert "AAAA-MM-DD" in error

    def test_crear_actividad_fecha_fin_invalida(self, service, mock_repo, datos_validos):
        datos_validos["fecha_fin"] = "2026/03/15"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert actividad is None
        assert "AAAA-MM-DD" in error

    def test_crear_actividad_fecha_vencimiento_invalida(self, service, mock_repo, datos_validos):
        datos_validos["fecha_vencimiento"] = "mañana"
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert actividad is None
        assert "AAAA-MM-DD" in error

    def test_crear_actividad_fechas_vacias_permitidas(self, service, mock_repo, datos_validos):
        mock_repo.create.return_value = 5
        datos_validos["fecha_inicio"] = ""
        datos_validos["fecha_fin"] = ""
        datos_validos["fecha_vencimiento"] = ""
        actividad, error = service.crear_actividad(datos_validos, 1)
        assert error is None

    # ==========================================
    # HELPERS PRIVADOS
    # ==========================================

    def test_parsear_entero_none(self, service, mock_repo):
        assert ActividadService._parsear_entero(None) is None

    def test_parsear_entero_vacio(self, service, mock_repo):
        assert ActividadService._parsear_entero("") is None

    def test_parsear_entero_valido(self, service, mock_repo):
        assert ActividadService._parsear_entero("120") == 120

    def test_parsear_entero_invalido(self, service, mock_repo):
        assert ActividadService._parsear_entero("abc") is None

    # ==========================================
    # OBTENER ACTIVIDADES
    # ==========================================

    def test_obtener_todas_exitoso(self, service, mock_repo):
        mock_repo.find_all.return_value = [
            Actividad(asunto="Llamada", tipo_actividad_id=1, propietario_id=1, estado_actividad_id=1)
        ]
        actividades, error = service.obtener_todas()
        assert error is None
        assert len(actividades) == 1

    def test_obtener_todas_error(self, service, mock_repo):
        mock_repo.find_all.side_effect = Exception("Error de BD")
        actividades, error = service.obtener_todas()
        assert actividades is None
        assert error is not None

    def test_contar_total_exitoso(self, service, mock_repo):
        mock_repo.count_all.return_value = 25
        total, error = service.contar_total()
        assert error is None
        assert total == 25

    # ==========================================
    # ACTUALIZAR ACTIVIDAD
    # ==========================================

    def test_actualizar_actividad_exitosa(self, service, mock_repo, datos_validos):
        actividad, error = service.actualizar_actividad(1, datos_validos, 1)
        assert error is None
        assert actividad.asunto == "Llamada de seguimiento"
        mock_repo.update.assert_called_once()

    def test_actualizar_actividad_error_bd(self, service, mock_repo, datos_validos):
        mock_repo.update.side_effect = Exception("Error de BD")
        actividad, error = service.actualizar_actividad(1, datos_validos, 1)
        assert actividad is None
        assert error is not None
