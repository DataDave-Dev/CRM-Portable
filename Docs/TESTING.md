# Guía de Testing - CRM Sistema

Esta guía proporciona información completa sobre cómo escribir, ejecutar y mantener tests en el proyecto CRM.

## Tabla de Contenidos

1. [Visión general](#visión-general)
2. [Estructura de tests](#estructura-de-tests)
3. [Ejecutar tests](#ejecutar-tests)
4. [Escribir tests](#escribir-tests)
5. [Mocking](#mocking)
6. [Cobertura de tests](#cobertura-de-tests)
7. [Mejores prácticas](#mejores-prácticas)

---

## Visión general

El proyecto utiliza **pytest** como framework de testing principal, con **pytest-mock** para mocking y **pytest-cov** para medición de cobertura.

### Estadísticas actuales

- **Total de tests**: 53
- **Status**: 100% passing ✅
- **Categorías**:
  - Validadores: 15 tests
  - Autenticación: 9 tests
  - Caché: 4 tests
  - Sanitización: 16 tests
  - Notas de contacto: 9 tests
  - Notas de empresa: 9 tests

---

## Estructura de tests

```
tests/
├── __init__.py
├── test_utils/
│   ├── __init__.py
│   ├── test_validators.py        # Tests de validaciones (15 tests)
│   ├── test_catalog_cache.py     # Tests de caché (4 tests)
│   └── test_sanitizer.py         # Tests de sanitización (16 tests)
└── test_services/
    ├── __init__.py
    ├── test_auth_service.py      # Tests de autenticación (9 tests)
    ├── test_nota_contacto_service.py  # Tests de notas de contacto (9 tests)
    └── test_nota_empresa_service.py   # Tests de notas de empresa (9 tests)
```

### Convención de nombres

- **Archivos**: `test_<module>.py`
- **Clases**: `Test<ClassName>` (opcional, útil para agrupar)
- **Funciones**: `test_<scenario>_<expected_result>`

**Ejemplos**:
```python
# ✅ BIEN
def test_crear_usuario_exitoso()
def test_crear_usuario_sin_email()
def test_crear_usuario_email_duplicado()

# ❌ MAL
def test_usuario()  # No describe escenario
def crear_usuario()  # Falta prefijo test_
```

---

## Ejecutar tests

### Comandos básicos

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con verbose (muestra cada test)
pytest -v

# Ejecutar con output completo (print statements)
pytest -s

# Ejecutar tests de un archivo específico
pytest tests/test_utils/test_validators.py

# Ejecutar un test específico
pytest tests/test_services/test_auth_service.py::test_login_exitoso

# Ejecutar tests que coincidan con patrón
pytest -k "email"  # Ejecuta todos los tests con "email" en el nombre
```

### Opciones útiles

```bash
# Mostrar tests más lentos
pytest --durations=10

# Detener al primer fallo
pytest -x

# Ejecutar tests que fallaron la última vez
pytest --lf

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n 4
```

### Cobertura

```bash
# Ejecutar con cobertura
pytest --cov=app

# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte en navegador
# Windows:
start htmlcov/index.html
# Mac/Linux:
open htmlcov/index.html

# Mostrar líneas sin cubrir
pytest --cov=app --cov-report=term-missing
```

---

## Escribir tests

### Estructura básica de un test

```python
import pytest
from unittest.mock import Mock, patch

# Importar el módulo a testear
from app.services.usuario_service import UsuarioService


# Fixtures para setup/teardown
@pytest.fixture
def service():
    """Crea una instancia del servicio con repository mockeado."""
    with patch('app.services.usuario_service.UsuarioRepository'):
        return UsuarioService()


@pytest.fixture
def mock_repo(service):
    """Retorna el repository mockeado del servicio."""
    return service._repo


# Test de caso exitoso
def test_crear_usuario_exitoso(service, mock_repo):
    # Arrange (preparar datos y mocks)
    mock_repo.create.return_value = 1
    mock_repo.email_exists.return_value = False
    datos = {
        "nombre": "Juan",
        "apellido_paterno": "Perez",
        "email": "juan@example.com",
        "contrasena": "Password123",
        "rol_id": 1
    }

    # Act (ejecutar la función)
    usuario, error = service.crear_usuario(datos)

    # Assert (verificar resultados)
    assert error is None
    assert usuario is not None
    assert usuario.usuario_id == 1
    assert usuario.nombre == "Juan"
    mock_repo.create.assert_called_once()


# Test de caso de error
def test_crear_usuario_sin_email(service):
    # Arrange
    datos = {
        "nombre": "Juan",
        "apellido_paterno": "Perez",
        "email": "",
        "contrasena": "Password123",
        "rol_id": 1
    }

    # Act
    usuario, error = service.crear_usuario(datos)

    # Assert
    assert usuario is None
    assert error == "El campo email es requerido"
```

### Patrón AAA (Arrange-Act-Assert)

Todos los tests deben seguir este patrón:

```python
def test_ejemplo():
    # Arrange - preparar datos y configurar mocks
    mock_obj = Mock()
    mock_obj.metodo.return_value = "resultado"
    datos = {"campo": "valor"}

    # Act - ejecutar la función bajo test
    resultado, error = funcion_a_testear(datos)

    # Assert - verificar resultados
    assert resultado is not None
    assert error is None
    mock_obj.metodo.assert_called_once()
```

---

## Mocking

### ¿Cuándo usar mocks?

- ✅ Para **aislar** la unidad bajo test
- ✅ Para **evitar** llamadas reales a BD
- ✅ Para **simular** errores difíciles de reproducir
- ✅ Para **acelerar** tests (sin I/O real)

### Técnicas de mocking

#### 1. Mock de repository completo

```python
@pytest.fixture
def service():
    # Patchear el import del repository
    with patch('app.services.usuario_service.UsuarioRepository'):
        return UsuarioService()

@pytest.fixture
def mock_repo(service):
    # Retornar el repository mockeado
    return service._repo

def test_crear(service, mock_repo):
    # Configurar comportamiento del mock
    mock_repo.create.return_value = 5
    mock_repo.email_exists.return_value = False

    # Ejecutar
    resultado, error = service.crear_usuario({...})

    # Verificar llamadas
    mock_repo.create.assert_called_once()
    assert mock_repo.email_exists.call_count == 1
```

#### 2. Mock de métodos específicos

```python
def test_ejemplo(service, mock_repo):
    # Configurar valores de retorno
    mock_repo.find_by_id.return_value = Usuario(usuario_id=1, nombre="Juan")
    mock_repo.update.return_value = True

    # Mock que lanza excepción
    mock_repo.delete.side_effect = Exception("Error de BD")
```

#### 3. Mock de funciones globales

```python
@patch('app.services.auth_service.bcrypt.checkpw')
def test_login(mock_checkpw, service):
    # Configurar bcrypt mockeado
    mock_checkpw.return_value = True

    # Ejecutar test
    usuario, error = service.login("email@test.com", "password")

    # Verificar
    assert error is None
    mock_checkpw.assert_called_once()
```

#### 4. Mock de datetime

```python
from unittest.mock import patch
from datetime import datetime

@patch('app.services.auth_service.datetime')
def test_con_fecha_fija(mock_datetime):
    # Fijar fecha
    mock_datetime.now.return_value = datetime(2025, 1, 15, 10, 30, 0)

    # Ejecutar test
    resultado = funcion_que_usa_datetime()

    # Verificar
    assert "2025-01-15" in resultado
```

---

## Cobertura de tests

### Medir cobertura

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Ver solo servicios
pytest --cov=app/services --cov-report=term-missing

# Ver solo utils
pytest --cov=app/utils --cov-report=term-missing
```

### Interpretar resultados

```
---------- coverage: platform win32, python 3.x -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
app/services/auth_service.py              45      2    96%   23-24
app/services/usuario_service.py          120      5    96%   78, 92-95
app/utils/validators.py                   80      0   100%
---------------------------------------------------------------------
TOTAL                                    245      7    97%
```

**Columnas**:
- `Stmts`: Total de líneas ejecutables
- `Miss`: Líneas no cubiertas
- `Cover`: Porcentaje de cobertura
- `Missing`: Números de línea sin cubrir

### Objetivos de cobertura

- **Utils**: 100% (funciones puras, fáciles de testear)
- **Services**: 90%+ (validaciones y lógica de negocio)
- **Repositories**: 80%+ (queries SQL)
- **Views**: 60%+ (UI es difícil de testear unitariamente)

---

## Ejemplos de tests

### Test de validadores

```python
from app.utils.validators import Validators

def test_validar_email_valido():
    assert Validators.validar_email("test@example.com") is True

def test_validar_email_invalido():
    assert Validators.validar_email("not-an-email") is False

def test_validar_email_vacio():
    assert Validators.validar_email("") is False
    assert Validators.validar_email(None) is False
```

### Test de servicios con mocks

```python
import pytest
from unittest.mock import Mock, patch
from app.services.empresa_service import EmpresaService

@pytest.fixture
def service():
    with patch('app.services.empresa_service.EmpresaRepository'):
        return EmpresaService()

@pytest.fixture
def mock_repo(service):
    return service._repo

def test_crear_empresa_exitoso(service, mock_repo):
    # Arrange
    mock_repo.create.return_value = 10
    mock_repo.rfc_exists.return_value = False
    datos = {
        "razon_social": "Acme Corp",
        "rfc": "ACM010101ABC",
        "email": "contacto@acme.com"
    }

    # Act
    empresa, error = service.crear_empresa(datos, usuario_actual_id=1)

    # Assert
    assert error is None
    assert empresa is not None
    assert empresa.empresa_id == 10
    assert empresa.rfc == "ACM010101ABC"
    mock_repo.create.assert_called_once()
    mock_repo.rfc_exists.assert_called_once_with("ACM010101ABC")

def test_crear_empresa_sin_razon_social(service):
    # Arrange
    datos = {"razon_social": "", "email": "test@test.com"}

    # Act
    empresa, error = service.crear_empresa(datos, usuario_actual_id=1)

    # Assert
    assert empresa is None
    assert error == "La razon social es requerida"

def test_crear_empresa_rfc_duplicado(service, mock_repo):
    # Arrange
    mock_repo.rfc_exists.return_value = True
    datos = {
        "razon_social": "Acme Corp",
        "rfc": "ACM010101ABC"
    }

    # Act
    empresa, error = service.crear_empresa(datos, usuario_actual_id=1)

    # Assert
    assert empresa is None
    assert error == "Este RFC ya esta registrado"
```

### Test con excepciones

```python
def test_crear_empresa_error_bd(service, mock_repo):
    # Arrange - simular error de BD
    mock_repo.create.side_effect = Exception("UNIQUE constraint failed")
    datos = {
        "razon_social": "Test Corp",
        "rfc": "TST010101ABC"
    }

    # Act
    empresa, error = service.crear_empresa(datos, usuario_actual_id=1)

    # Assert
    assert empresa is None
    assert error is not None  # Mensaje sanitizado
    assert error != "UNIQUE constraint failed"  # No expone detalles técnicos
```

### Test de sanitización

```python
from app.utils.sanitizer import Sanitizer

def test_sanitize_html():
    # XSS attempt
    malicious = "<script>alert('XSS')</script>"
    sanitized = Sanitizer.sanitize_html(malicious)
    assert "<script>" not in sanitized
    assert "&lt;script&gt;" in sanitized

def test_validate_length_ok():
    assert Sanitizer.validate_length("texto", min_length=1, max_length=10) is True

def test_validate_length_too_long():
    assert Sanitizer.validate_length("texto muy largo", max_length=5) is False
```

---

## Mejores prácticas

### 1. Tests independientes

```python
# ❌ MAL - tests dependen de orden
data = []

def test_1_agregar():
    data.append("item")
    assert len(data) == 1

def test_2_eliminar():  # Falla si test_1 no se ejecutó primero
    data.remove("item")
    assert len(data) == 0

# ✅ BIEN - cada test es independiente
def test_agregar():
    data = []
    data.append("item")
    assert len(data) == 1

def test_eliminar():
    data = ["item"]
    data.remove("item")
    assert len(data) == 0
```

### 2. Un concepto por test

```python
# ❌ MAL - test hace demasiado
def test_usuario():
    # Crea usuario
    usuario, _ = service.crear_usuario({...})
    assert usuario is not None

    # Actualiza usuario
    updated, _ = service.actualizar_usuario(usuario.usuario_id, {...})
    assert updated is not None

    # Elimina usuario
    ok, _ = service.eliminar_usuario(usuario.usuario_id)
    assert ok is True

# ✅ BIEN - un test por operación
def test_crear_usuario():
    usuario, error = service.crear_usuario({...})
    assert error is None
    assert usuario is not None

def test_actualizar_usuario():
    usuario, error = service.actualizar_usuario(1, {...})
    assert error is None

def test_eliminar_usuario():
    ok, error = service.eliminar_usuario(1)
    assert error is None
```

### 3. Nombres descriptivos

```python
# ❌ MAL
def test_1():
    pass

def test_email():
    pass

# ✅ BIEN
def test_crear_usuario_con_email_valido_retorna_usuario():
    pass

def test_crear_usuario_con_email_duplicado_retorna_error():
    pass
```

### 4. Usar fixtures para setup repetitivo

```python
# ❌ MAL - duplicación
def test_1():
    service = UsuarioService()
    mock_repo = Mock()
    service._repo = mock_repo
    # test

def test_2():
    service = UsuarioService()
    mock_repo = Mock()
    service._repo = mock_repo
    # test

# ✅ BIEN - fixture reutilizable
@pytest.fixture
def service():
    with patch('app.services.usuario_service.UsuarioRepository'):
        return UsuarioService()

def test_1(service):
    # test

def test_2(service):
    # test
```

### 5. Verificar comportamiento, no implementación

```python
# ❌ MAL - test frágil, acoplado a implementación
def test_crear_usuario(service, mock_repo):
    service.crear_usuario({...})
    # Verifica implementación interna
    assert service._some_internal_var == "value"

# ✅ BIEN - test robusto, verifica comportamiento público
def test_crear_usuario(service, mock_repo):
    mock_repo.create.return_value = 1
    usuario, error = service.crear_usuario({...})
    # Verifica API pública
    assert error is None
    assert usuario.usuario_id == 1
```

---

## Testing de edge cases

Siempre testear:
- ✅ Caso feliz (datos válidos)
- ✅ Valores vacíos/nulos
- ✅ Valores en límites (longitud máxima, valores negativos)
- ✅ Formatos inválidos
- ✅ Condiciones de error (BD, permisos)

```python
# Ejemplo completo de edge cases
def test_crear_usuario_exitoso():  # Caso feliz
    pass

def test_crear_usuario_sin_nombre():  # Campo requerido faltante
    pass

def test_crear_usuario_nombre_muy_largo():  # Límite de longitud
    pass

def test_crear_usuario_email_invalido():  # Formato incorrecto
    pass

def test_crear_usuario_email_duplicado():  # Violación de unicidad
    pass

def test_crear_usuario_error_bd():  # Error de sistema
    pass
```

---

## Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock](https://pypi.org/project/pytest-mock/)
- [pytest-cov](https://pypi.org/project/pytest-cov/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## Próximos pasos

Tests pendientes de implementar:
- [ ] Tests de EmpresaService
- [ ] Tests de ContactoService
- [ ] Tests de CatalogoService
- [ ] Tests de repositories
- [ ] Tests de integración end-to-end
- [ ] CI/CD con GitHub Actions
