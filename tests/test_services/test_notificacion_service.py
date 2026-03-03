# tests unitarios para servicio de notificaciones y recordatorios

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.notificacion_service import NotificacionService
from app.models.Notificacion import Notificacion
from app.models.Recordatorio import Recordatorio


class TestNotificacionService:

    @pytest.fixture
    def mock_repos(self):
        with patch('app.services.notificacion_service.NotificacionRepository') as mock_notif, \
             patch('app.services.notificacion_service.RecordatorioRepository') as mock_record, \
             patch('app.services.notificacion_service.ConfigCorreoRepository') as mock_config:
            yield mock_notif.return_value, mock_record.return_value, mock_config.return_value

    @pytest.fixture
    def service(self, mock_repos):
        return NotificacionService()

    # ==========================================
    # NOTIFICACIONES
    # ==========================================

    def test_obtener_notificaciones_exitoso(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.find_by_usuario.return_value = [
            Notificacion(notificacion_id=1, usuario_id=1, mensaje="Prueba", es_leida=0)
        ]
        notificaciones, error = service.obtener_notificaciones(1)
        assert error is None
        assert len(notificaciones) == 1

    def test_obtener_notificaciones_error(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.find_by_usuario.side_effect = Exception("Error de BD")
        notificaciones, error = service.obtener_notificaciones(1)
        assert notificaciones == []
        assert error is not None

    def test_obtener_no_leidas_exitoso(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.find_unread_by_usuario.return_value = [
            Notificacion(notificacion_id=2, usuario_id=1, mensaje="Nueva", es_leida=0)
        ]
        no_leidas, error = service.obtener_no_leidas(1)
        assert error is None
        assert len(no_leidas) == 1

    def test_count_no_leidas_exitoso(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.count_unread.return_value = 3
        count = service.count_no_leidas(1)
        assert count == 3

    def test_count_no_leidas_error_retorna_cero(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.count_unread.side_effect = Exception("Error")
        count = service.count_no_leidas(1)
        assert count == 0

    def test_marcar_como_leida_exitoso(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        resultado, error = service.marcar_como_leida(1)
        assert resultado is True
        assert error is None
        notif_repo.mark_as_read.assert_called_once_with(1)

    def test_marcar_como_leida_error(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        notif_repo.mark_as_read.side_effect = Exception("Error de BD")
        resultado, error = service.marcar_como_leida(1)
        assert resultado is False
        assert error is not None

    def test_marcar_todas_como_leidas_exitoso(self, service, mock_repos):
        notif_repo, _, _ = mock_repos
        resultado, error = service.marcar_todas_como_leidas(1)
        assert resultado is True
        assert error is None
        notif_repo.mark_all_read.assert_called_once_with(1)

    # ==========================================
    # RECORDATORIOS - VALIDACION
    # ==========================================

    def test_crear_recordatorio_exitoso(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.create.return_value = 1
        datos = {"titulo": "Llamar cliente", "fecha_recordatorio": "2026-03-15"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert error is None
        assert recordatorio is not None
        assert recordatorio.titulo == "Llamar cliente"
        assert recordatorio.recordatorio_id == 1

    def test_crear_recordatorio_sin_titulo(self, service, mock_repos):
        datos = {"titulo": "", "fecha_recordatorio": "2026-03-15"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert error == "El titulo del recordatorio es requerido"

    def test_crear_recordatorio_titulo_solo_espacios(self, service, mock_repos):
        datos = {"titulo": "   ", "fecha_recordatorio": "2026-03-15"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert error == "El titulo del recordatorio es requerido"

    def test_crear_recordatorio_titulo_muy_largo(self, service, mock_repos):
        datos = {"titulo": "T" * 256, "fecha_recordatorio": "2026-03-15"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert "255" in error

    def test_crear_recordatorio_sin_fecha(self, service, mock_repos):
        datos = {"titulo": "Llamar cliente", "fecha_recordatorio": ""}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert "fecha" in error.lower()

    def test_crear_recordatorio_sin_fecha_none(self, service, mock_repos):
        datos = {"titulo": "Llamar cliente"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert "fecha" in error.lower()

    def test_crear_recordatorio_error_bd(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.create.side_effect = Exception("Error de BD")
        datos = {"titulo": "Recordatorio", "fecha_recordatorio": "2026-03-15"}
        recordatorio, error = service.crear_recordatorio(datos, 1)
        assert recordatorio is None
        assert error is not None

    # ==========================================
    # RECORDATORIOS - ACTUALIZAR
    # ==========================================

    def test_actualizar_recordatorio_exitoso(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        datos = {"titulo": "Recordatorio actualizado", "fecha_recordatorio": "2026-04-01"}
        recordatorio, error = service.actualizar_recordatorio(1, datos)
        assert error is None
        assert recordatorio.titulo == "Recordatorio actualizado"
        record_repo.update.assert_called_once()

    def test_actualizar_recordatorio_sin_titulo(self, service, mock_repos):
        datos = {"titulo": "", "fecha_recordatorio": "2026-04-01"}
        recordatorio, error = service.actualizar_recordatorio(1, datos)
        assert recordatorio is None
        assert error is not None

    def test_actualizar_recordatorio_error_bd(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.update.side_effect = Exception("Error de BD")
        datos = {"titulo": "Recordatorio", "fecha_recordatorio": "2026-04-01"}
        recordatorio, error = service.actualizar_recordatorio(1, datos)
        assert recordatorio is None
        assert error is not None

    # ==========================================
    # RECORDATORIOS - CRUD BASICO
    # ==========================================

    def test_eliminar_recordatorio_exitoso(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        resultado, error = service.eliminar_recordatorio(1)
        assert resultado is True
        assert error is None
        record_repo.delete.assert_called_once_with(1)

    def test_eliminar_recordatorio_error(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.delete.side_effect = Exception("Error de BD")
        resultado, error = service.eliminar_recordatorio(1)
        assert resultado is False
        assert error is not None

    def test_completar_recordatorio_exitoso(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        resultado, error = service.completar_recordatorio(1)
        assert resultado is True
        assert error is None
        record_repo.marcar_completado.assert_called_once_with(1)

    def test_completar_recordatorio_error(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.marcar_completado.side_effect = Exception("Error de BD")
        resultado, error = service.completar_recordatorio(1)
        assert resultado is False
        assert error is not None

    def test_obtener_recordatorios_exitoso(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.find_by_usuario.return_value = [
            Recordatorio(titulo="Recordatorio 1", fecha_recordatorio="2026-03-15")
        ]
        recordatorios, error = service.obtener_recordatorios(1)
        assert error is None
        assert len(recordatorios) == 1

    # ==========================================
    # TIPOS DE RECURRENCIA
    # ==========================================

    def test_tipos_recurrencia(self, service, mock_repos):
        tipos = service.tipos_recurrencia
        assert "Sin recurrencia" in tipos
        assert "Diaria" in tipos
        assert "Semanal" in tipos
        assert "Mensual" in tipos
        assert len(tipos) == 4

    # ==========================================
    # PROCESAR RECORDATORIOS VENCIDOS
    # ==========================================

    def test_procesar_recordatorios_vencidos_sin_vencidos(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.find_due.return_value = []
        procesados, error = service.procesar_recordatorios_vencidos(1, "user@test.com")
        assert procesados == []
        assert error is None

    def test_procesar_recordatorios_vencidos_sin_config(self, service, mock_repos):
        _, record_repo, config_repo = mock_repos
        rec = Recordatorio(recordatorio_id=1, titulo="Vencido", fecha_recordatorio="2026-01-01")
        record_repo.find_due.return_value = [rec]
        config_repo.find_activa.return_value = None  # sin config SMTP
        procesados, error = service.procesar_recordatorios_vencidos(1, "user@test.com")
        # sin config, debe marcar como leido de todas formas
        assert len(procesados) == 1
        record_repo.marcar_leido.assert_called_once_with(1)

    def test_procesar_recordatorios_vencidos_error_bd(self, service, mock_repos):
        _, record_repo, _ = mock_repos
        record_repo.find_due.side_effect = Exception("Error de BD")
        procesados, error = service.procesar_recordatorios_vencidos(1, "user@test.com")
        assert procesados == []
        assert error is not None
