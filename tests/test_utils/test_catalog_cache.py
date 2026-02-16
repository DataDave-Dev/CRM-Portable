# tests unitarios para sistema de cache de catalogos

import pytest
from unittest.mock import Mock, patch
from app.utils.catalog_cache import CatalogCache


class TestCatalogCache:
    # tests del sistema de cache

    @pytest.fixture(autouse=True)
    def reset_cache(self):
        # limpiar cache antes de cada test
        CatalogCache.invalidate_all()
        yield
        # limpiar cache despues de cada test
        CatalogCache.invalidate_all()

    @patch('app.utils.catalog_cache.get_connection')
    def test_cache_industrias(self, mock_conn):
        # test de cache de industrias
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, 'Tecnologia'),
            (2, 'Manufactura'),
        ]
        mock_conn.return_value.execute.return_value = mock_cursor

        # primera llamada debe consultar BD
        result1 = CatalogCache.get_industrias()
        assert len(result1) == 2
        assert result1[0] == (1, 'Tecnologia')
        assert mock_conn.return_value.execute.call_count == 1

        # segunda llamada debe usar cache (no consultar BD nuevamente)
        result2 = CatalogCache.get_industrias()
        assert len(result2) == 2
        assert result2 == result1
        assert mock_conn.return_value.execute.call_count == 1  # no incrementa

    @patch('app.utils.catalog_cache.get_connection')
    def test_invalidate_cache(self, mock_conn):
        # test de invalidacion de cache
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, 'Test')]
        mock_conn.return_value.execute.return_value = mock_cursor

        # obtener datos (consulta BD)
        CatalogCache.get_industrias()
        assert mock_conn.return_value.execute.call_count == 1

        # invalidar cache
        CatalogCache.invalidate('industrias')

        # siguiente llamada debe consultar BD nuevamente
        CatalogCache.get_industrias()
        assert mock_conn.return_value.execute.call_count == 2

    @patch('app.utils.catalog_cache.get_connection')
    def test_cache_con_filtro(self, mock_conn):
        # test de cache con filtros (estados por pais)
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, 'Nuevo Leon')]
        mock_conn.return_value.execute.return_value = mock_cursor

        # obtener estados de un pais
        result = CatalogCache.get_estados(pais_id=1)
        assert len(result) == 1
        assert result[0] == (1, 'Nuevo Leon')

    @patch('app.utils.catalog_cache.get_connection')
    def test_invalidate_all(self, mock_conn):
        # test de invalidacion total del cache
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, 'Test')]
        mock_conn.return_value.execute.return_value = mock_cursor

        # cargar varios catalogos
        CatalogCache.get_industrias()
        CatalogCache.get_monedas()
        initial_calls = mock_conn.return_value.execute.call_count

        # invalidar todo
        CatalogCache.invalidate_all()

        # siguiente llamada debe consultar BD nuevamente
        CatalogCache.get_industrias()
        CatalogCache.get_monedas()

        # debe haber mas llamadas (cache invalidado)
        assert mock_conn.return_value.execute.call_count > initial_calls

    def test_set_ttl(self):
        # test de configuracion de TTL
        CatalogCache.set_ttl(600)
        assert CatalogCache._ttl_seconds == 600

        CatalogCache.set_ttl(300)  # restaurar valor por defecto
