# Guía de Desarrollo - CRM Sistema

Esta guía proporciona información detallada para desarrolladores que trabajan en el proyecto CRM.

## Tabla de Contenidos

1. [Configuración del entorno](#configuración-del-entorno)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Convenciones de código](#convenciones-de-código)
4. [Flujo de trabajo](#flujo-de-trabajo)
5. [Buenas prácticas](#buenas-prácticas)
6. [Debugging](#debugging)

---

## Configuración del entorno

### Requisitos previos

- Python 3.8 o superior
- Git
- Editor de código (recomendado: VS Code o PyCharm)

### Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd "Proyecto Equipo #1"

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install pytest pytest-mock pytest-cov
```

### Configuración del IDE

#### VS Code

Instalar extensiones recomendadas:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- Qt for Python

Configuración en `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

---

## Estructura del proyecto

```
Proyecto Equipo #1/
├── app/
│   ├── assets/              # Recursos SVG (iconos de la UI)
│   ├── config/              # Configuración
│   │   ├── settings.py      # Configuración general
│   │   └── catalogos.py     # Definición de catálogos
│   ├── database/            # Capa de base de datos
│   │   ├── connection.py    # Conexión thread-local a SQLite
│   │   └── initializer.py   # Inicialización de esquema
│   ├── models/              # Modelos de datos (DTOs)
│   │   ├── Usuario.py, Rol.py, Catalogo.py
│   │   ├── Empresa.py, Contacto.py
│   │   ├── NotaContacto.py, NotaEmpresa.py
│   │   ├── Oportunidad.py, Producto.py, Cotizacion.py
│   │   ├── Actividad.py
│   │   ├── Segmento.py, Etiqueta.py
│   │   ├── Plantilla.py, Campana.py
│   │   └── ConfiguracionCorreo.py
│   ├── repositories/        # Capa de acceso a datos (CRUD + SQL)
│   ├── services/            # Lógica de negocio y validaciones
│   ├── controllers/         # Controladores MVC (login, main)
│   ├── views/               # Vistas PyQt5
│   │   ├── ui/              # Archivos .ui de Qt Designer
│   │   │   ├── main/, auth/, users/
│   │   │   ├── clientes/, ventas/, catalogos/
│   │   │   ├── actividades/, segmentacion/
│   │   │   ├── comunicacion/, configuracion/, geografia/
│   └── utils/               # Utilidades transversales
│       ├── validators.py    # Validaciones (email, RFC, teléfono)
│       ├── sanitizer.py     # Sanitización XSS
│       ├── logger.py        # Sistema de logging con filtrado
│       ├── catalog_cache.py # Caché en memoria con TTL
│       └── db_retry.py      # Retry y sanitización de errores
├── tests/                   # Tests unitarios
├── docs/                    # Documentación
├── db/                      # Base de datos
│   ├── database_query.sql   # Esquema completo (41+ tablas)
│   └── crm.db               # BD generada (no commitear)
└── logs/                    # Archivos de log (generados)
```

### Convención de nombres de archivos

- Modelos: `PascalCase.py` (ej: `Usuario.py`)
- Repositorios: `snake_case_repository.py` (ej: `usuario_repository.py`)
- Servicios: `snake_case_service.py` (ej: `auth_service.py`)
- Vistas: `snake_case_view.py` o `snake_case_widget.py`
- Tests: `test_<module>.py` (ej: `test_auth_service.py`)

---

## Convenciones de código

### Estilo de código

Seguimos PEP 8 con algunas adaptaciones:

```python
# Importaciones en orden:
# 1. Librerías estándar
# 2. Librerías de terceros
# 3. Módulos locales
import re
from datetime import datetime

from PyQt5.QtWidgets import QWidget
import bcrypt

from app.repositories.usuario_repository import UsuarioRepository
from app.utils.logger import AppLogger


# Constantes en MAYÚSCULAS
MAX_TITULO_LENGTH = 200
DEFAULT_PAGE_SIZE = 50

# Clases en PascalCase
class UsuarioService:
    pass

# Métodos y variables en snake_case
def crear_usuario(datos_usuario):
    nombre_completo = f"{datos_usuario['nombre']} {datos_usuario['apellido']}"
    return nombre_completo
```

### Docstrings

Usar Google Style Python Docstrings:

```python
def crear_usuario(self, datos_usuario):
    """
    Crea un nuevo usuario en el sistema.

    Args:
        datos_usuario (dict): Diccionario con los datos del usuario:
            - nombre (str, requerido): Nombre del usuario
            - email (str, requerido): Correo electrónico único
            - contrasena (str, requerido): Contraseña mínimo 8 caracteres

    Returns:
        tuple: (Usuario|None, str|None)
            - Si es exitoso: (objeto Usuario con usuario_id asignado, None)
            - Si falla: (None, mensaje de error descriptivo)

    Examples:
        >>> service = UsuarioService()
        >>> datos = {"nombre": "Juan", "email": "juan@example.com", "contrasena": "Pass123"}
        >>> usuario, error = service.crear_usuario(datos)
        >>> if error is None:
        ...     print(f"Usuario creado con ID: {usuario.usuario_id}")

    Note:
        - La contraseña se hashea con bcrypt antes de guardar
        - El email debe ser único en el sistema
    """
    pass
```

### Comentarios

```python
# Comentarios de una línea para explicar lógica compleja
if self._repo.email_exists(email, excluir_id=usuario_id):
    return None, "Este email ya está registrado por otro usuario"

# IMPORTANTE: Comentarios críticos de seguridad en MAYÚSCULAS
# IMPORTANTE: NUNCA loguear la contraseña en texto plano
logger.info(f"Actualizando contraseña para usuario {usuario_id}")
```

---

## Flujo de trabajo

### Agregar una nueva entidad

Ejemplo: agregar "Productos"

#### 1. Crear modelo (`app/models/Producto.py`)

```python
class Producto:
    def __init__(self, producto_id=None, nombre=None, precio=None, **kwargs):
        self.producto_id = producto_id
        self.nombre = nombre
        self.precio = precio
```

#### 2. Crear repositorio (`app/repositories/producto_repository.py`)

```python
from app.database.connection import DatabaseConnection
from app.models.Producto import Producto

class ProductoRepository:
    def __init__(self):
        self._conn = DatabaseConnection.get_instance()

    def find_all(self):
        # Implementar query
        pass

    def find_by_id(self, producto_id):
        # Implementar query
        pass

    def create(self, producto):
        # Implementar insert
        pass

    def update(self, producto):
        # Implementar update
        pass

    def delete(self, producto_id):
        # Implementar delete
        pass
```

#### 3. Crear servicio (`app/services/producto_service.py`)

```python
"""
Servicio de gestión de productos para el sistema CRM.

Validaciones implementadas:
    - Campo requerido: nombre
    - Precio: número positivo
"""

from app.repositories.producto_repository import ProductoRepository
from app.models.Producto import Producto
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

class ProductoService:
    """Servicio de gestión de productos."""

    def __init__(self):
        """Inicializa el servicio de productos."""
        self._repo = ProductoRepository()

    def obtener_todos(self):
        """Obtiene todos los productos."""
        try:
            logger.debug("Obteniendo productos")
            productos = self._repo.find_all()
            logger.info(f"Se obtuvieron {len(productos)} productos")
            return productos, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener productos")
            return None, sanitize_error_message(e)

    def crear_producto(self, datos, usuario_actual_id):
        """
        Crea un nuevo producto.

        Args:
            datos (dict): Datos del producto
            usuario_actual_id (int): ID del usuario que crea

        Returns:
            tuple: (Producto|None, str|None)
        """
        # Validaciones
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return None, "El nombre es requerido"

        precio = datos.get("precio")
        if precio is not None:
            try:
                precio = float(precio)
                if precio < 0:
                    return None, "El precio no puede ser negativo"
            except (ValueError, TypeError):
                return None, "El precio debe ser un número válido"

        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio
        )

        try:
            logger.info(f"Creando producto: {nombre} por usuario {usuario_actual_id}")
            producto_id = self._repo.create(nuevo_producto)
            nuevo_producto.producto_id = producto_id
            logger.info(f"Producto {producto_id} creado exitosamente")
            return nuevo_producto, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear producto: {nombre}")
            return None, sanitize_error_message(e)
```

#### 4. Crear vista (widget o dialog)

```python
from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton, QVBoxLayout

class ProductosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._service = ProductoService()

    def _setup_ui(self):
        # Crear componentes UI
        pass

    def _cargar_productos(self):
        productos, error = self._service.obtener_todos()
        if error:
            # Mostrar error
            return
        # Llenar tabla con productos
```

#### 5. Crear tests (`tests/test_services/test_producto_service.py`)

```python
import pytest
from unittest.mock import Mock, patch
from app.services.producto_service import ProductoService

@pytest.fixture
def service():
    with patch('app.services.producto_service.ProductoRepository'):
        return ProductoService()

@pytest.fixture
def mock_repo(service):
    return service._repo

def test_crear_producto_exitoso(service, mock_repo):
    mock_repo.create.return_value = 1
    datos = {"nombre": "Producto A", "precio": 100.50}

    producto, error = service.crear_producto(datos, usuario_actual_id=1)

    assert error is None
    assert producto is not None
    assert producto.producto_id == 1
    assert producto.nombre == "Producto A"
    assert producto.precio == 100.50

def test_crear_producto_sin_nombre(service):
    datos = {"nombre": "", "precio": 100}

    producto, error = service.crear_producto(datos, usuario_actual_id=1)

    assert producto is None
    assert error == "El nombre es requerido"
```

---

## Buenas prácticas

### Seguridad

#### 1. NUNCA loguear datos sensibles

```python
# ❌ MAL
logger.info(f"Usuario {email} con contraseña {password}")

# ✅ BIEN
# IMPORTANTE: NUNCA loguear la contraseña
logger.info(f"Creando usuario: {email}")
```

#### 2. Usar queries parametrizadas

```python
# ❌ MAL - Inyección SQL
query = f"SELECT * FROM Usuarios WHERE email = '{email}'"

# ✅ BIEN - Parametrizada
query = "SELECT * FROM Usuarios WHERE email = ?"
cursor.execute(query, (email,))
```

#### 3. Hashear contraseñas con bcrypt

```python
import bcrypt

# Hashear
contrasena_hash = bcrypt.hashpw(
    contrasena.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

# Verificar
if bcrypt.checkpw(password.encode("utf-8"), hash_almacenado.encode("utf-8")):
    # Contraseña correcta
    pass
```

### Validaciones

Validar en tres niveles:

1. **Vista**: Validación básica en UI (QValidator, maxLength)
2. **Servicio**: Validación de negocio (campos requeridos, formatos)
3. **Base de datos**: Constraints (UNIQUE, NOT NULL, CHECK, FK)

```python
# Servicio
def crear_usuario(self, datos):
    # Validar campos requeridos
    email = datos.get("email", "").strip()
    if not email:
        return None, "El email es requerido"

    # Validar formato
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return None, "El formato del email no es válido"

    # Validar unicidad
    if self._repo.email_exists(email):
        return None, "Este email ya está registrado"
```

### Logging

Usar niveles apropiados:

```python
logger.debug("Información detallada para debugging")
logger.info("Operación normal completada")
logger.warning("Algo inesperado pero manejable")
logger.error("Error que impide completar operación")
logger.critical("Error crítico del sistema")

# Usar helper para excepciones
try:
    # código
    pass
except Exception as e:
    AppLogger.log_exception(logger, "Contexto del error")
    return None, sanitize_error_message(e)
```

### Manejo de errores

Retornar tuplas (resultado, error):

```python
# ✅ BIEN - Patrón consistente
def obtener_usuario(self, usuario_id):
    try:
        usuario = self._repo.find_by_id(usuario_id)
        if usuario is None:
            return None, "Usuario no encontrado"
        return usuario, None
    except Exception as e:
        return None, sanitize_error_message(e)

# Usar
usuario, error = service.obtener_usuario(5)
if error:
    QMessageBox.warning(self, "Error", error)
    return
# Continuar con usuario
```

---

## Debugging

### Logs

Los logs se encuentran en:
- `logs/app.log`: Todos los niveles (DEBUG, INFO, WARNING, ERROR)
- `logs/errors.log`: Solo errores con stack traces completos

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Ver solo errores
tail -f logs/errors.log

# Buscar errores específicos
grep "Error al crear usuario" logs/app.log
```

### Debugging en PyCharm

1. Configurar breakpoints en el código
2. Run > Debug 'main'
3. Inspeccionar variables en el debugger

### Debugging en VS Code

1. Agregar configuración en `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: CRM",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal"
        }
    ]
}
```
2. Agregar breakpoints
3. F5 para iniciar debugging

### Base de datos

```bash
# Abrir base de datos con SQLite
sqlite3 db/crm.db

# Comandos útiles
.tables                    # Listar tablas
.schema Usuarios          # Ver esquema de tabla
SELECT * FROM Usuarios;   # Query
.quit                     # Salir
```

---

## Tests

Ejecutar tests:

```bash
# Todos los tests
pytest

# Con verbose
pytest -v

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_services/test_auth_service.py
pytest tests/test_services/test_auth_service.py::test_login_exitoso
```

Ver cobertura:
```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir en navegador
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

---

## Recursos

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [pytest Documentation](https://docs.pytest.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
