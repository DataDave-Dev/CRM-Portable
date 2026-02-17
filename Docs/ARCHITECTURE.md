# Arquitectura del Sistema CRM

Este documento describe la arquitectura del sistema CRM, los patrones de diseño utilizados, y las decisiones arquitectónicas clave.

## Tabla de Contenidos

1. [Visión general](#visión-general)
2. [Patrones de diseño](#patrones-de-diseño)
3. [Arquitectura por capas](#arquitectura-por-capas)
4. [Flujo de datos](#flujo-de-datos)
5. [Componentes clave](#componentes-clave)
6. [Decisiones arquitectónicas](#decisiones-arquitectónicas)

---

## Visión general

El sistema CRM es una aplicación de escritorio construida con Python y PyQt5, que implementa una arquitectura por capas basada en el patrón MVC (Modelo-Vista-Controlador) extendido con capas adicionales de Repository y Service.

### Stack tecnológico

- **Frontend**: PyQt5 5.15.11 (interfaz gráfica de escritorio)
- **Backend**: Python 3.x (lógica de negocio)
- **Base de datos**: SQLite3 con modo WAL
- **Seguridad**: bcrypt 5.0.0 (hashing de contraseñas)
- **Testing**: pytest + pytest-mock

---

## Patrones de diseño

### 1. MVC (Model-View-Controller)

Separación clara entre presentación, lógica y datos.

```
┌──────────┐      ┌──────────────┐      ┌───────┐
│   View   │ ───> │  Controller  │ ───> │ Model │
│  (PyQt5) │ <─── │   (Logic)    │ <─── │(Data) │
└──────────┘      └──────────────┘      └───────┘
```

**Responsabilidades:**
- **View**: Presentación e interacción con usuario (widgets, dialogs)
- **Controller**: Coordinación entre vista y modelo, manejo de eventos
- **Model**: Representación de entidades de negocio (Usuario, Empresa, Contacto)

### 2. Repository Pattern

Abstracción de la capa de acceso a datos.

```python
# Repository encapsula todo el acceso a BD
class UsuarioRepository:
    def find_by_id(self, usuario_id):
        # SQL queries
        pass

    def create(self, usuario):
        # SQL insert
        pass
```

**Ventajas:**
- Desacoplamiento de lógica de negocio y persistencia
- Facilita testing con mocks
- Centraliza queries SQL
- Permite cambiar BD sin afectar servicios

### 3. Service Layer Pattern

Lógica de negocio separada del acceso a datos.

```python
# Service maneja validaciones y lógica de negocio
class UsuarioService:
    def __init__(self):
        self._repo = UsuarioRepository()

    def crear_usuario(self, datos):
        # Validaciones
        # Transformaciones
        # Llamadas al repository
        pass
```

**Ventajas:**
- Validaciones centralizadas
- Lógica de negocio reutilizable
- Transacciones y operaciones complejas
- Fácil de testear

### 4. Singleton Pattern

Conexión única a base de datos compartida.

```python
class DatabaseConnection:
    _instance = None
    _connection = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Ventajas:**
- Una sola conexión a BD para toda la aplicación
- Ahorro de recursos
- Consistencia en configuración (WAL mode, timeout)

### 5. Strategy Pattern

Caché de catálogos con diferentes estrategias.

```python
# Estrategia de caché con TTL
class CatalogCache:
    _cache = {}
    _ttl = 300  # 5 minutos

    @classmethod
    def get(cls, key):
        # Verificar expiración
        # Retornar si válido
        pass

    @classmethod
    def invalidate(cls, key):
        # Limpiar caché
        pass
```

---

## Arquitectura por capas

El sistema está organizado en 7 capas principales:

```
┌─────────────────────────────────────────┐
│  1. PRESENTATION (Views)                │  ← PyQt5 Widgets & Dialogs
├─────────────────────────────────────────┤
│  2. CONTROL (Controllers)               │  ← Coordinación y eventos
├─────────────────────────────────────────┤
│  3. BUSINESS LOGIC (Services)           │  ← Validaciones y reglas
├─────────────────────────────────────────┤
│  4. DATA ACCESS (Repositories)          │  ← CRUD y queries SQL
├─────────────────────────────────────────┤
│  5. MODELS (Domain Entities)            │  ← Usuario, Empresa, etc.
├─────────────────────────────────────────┤
│  6. UTILITIES (Utils)                   │  ← Logger, Validators, etc.
├─────────────────────────────────────────┤
│  7. DATABASE (SQLite)                   │  ← Persistencia
└─────────────────────────────────────────┘
```

### Capa 1: Presentation (Views)

**Responsabilidad**: Interfaz gráfica de usuario

**Componentes**:
- `LoginView`: Pantalla de autenticación
- `MainView`: Ventana principal con menú y navegación
- `ConfiguracionView`: Gestión de configuración
- `CatalogoListWidget`: Lista genérica de catálogos
- `CatalogoFormDialog`: Formulario genérico CRUD
- `GeografiaWidget`: Jerarquía de países/estados/ciudades
- `NotasContactoWidget`: Gestión de notas de contacto
- `NotasEmpresaWidget`: Gestión de notas de empresa

**Principios**:
- No contiene lógica de negocio
- Delega toda operación al controller
- Usa signals/slots para comunicación desacoplada
- Validaciones básicas de UI (QValidator, maxLength)

### Capa 2: Control (Controllers)

**Responsabilidad**: Coordinación entre vista y servicios

**Componentes**:
- `LoginController`: Maneja login y redirección
- `MainController`: Gestiona navegación y estado de sesión

**Principios**:
- Maneja eventos de UI
- Coordina llamadas a servicios
- Gestiona transiciones de estado
- No contiene validaciones de negocio

### Capa 3: Business Logic (Services)

**Responsabilidad**: Lógica de negocio y validaciones

**Componentes**:
- `AuthService`: Autenticación y sesión
- `UsuarioService`: CRUD de usuarios
- `EmpresaService`: CRUD de empresas
- `ContactoService`: CRUD de contactos
- `NotaContactoService`: CRUD de notas de contacto
- `NotaEmpresaService`: CRUD de notas de empresa
- `CatalogoService`: CRUD genérico de catálogos

**Principios**:
- Valida datos de negocio (formato, requeridos, unicidad)
- Transforma datos entre capas
- Aplica reglas de negocio
- Logging completo de operaciones
- Sanitización de errores
- Retorna tuplas (resultado, error)

### Capa 4: Data Access (Repositories)

**Responsabilidad**: Acceso a base de datos

**Componentes**:
- `UsuarioRepository`
- `EmpresaRepository`
- `ContactoRepository`
- `NotaContactoRepository`
- `NotaEmpresaRepository`
- `CatalogoRepository` (genérico)
- `AuditoriaRepository`

**Principios**:
- Queries parametrizadas (prevención SQL injection)
- Retorna modelos de dominio
- Maneja transacciones
- Usa singleton de conexión
- No contiene lógica de negocio

### Capa 5: Models (Domain Entities)

**Responsabilidad**: Representación de entidades

**Componentes**:
- `Usuario`
- `Rol`
- `Empresa`
- `Contacto`
- `NotaContacto`
- `NotaEmpresa`
- `Catalogo` (genérico)

**Principios**:
- POJOs/DTOs simples
- Sin lógica de negocio
- Sin dependencias

### Capa 6: Utilities

**Responsabilidad**: Funcionalidades transversales

**Componentes**:
- `validators.py`: Validaciones reutilizables (email, RFC, teléfono)
- `sanitizer.py`: Sanitización contra XSS
- `logger.py`: Sistema de logging con filtrado de datos sensibles
- `catalog_cache.py`: Caché en memoria con TTL
- `db_retry.py`: Retry automático y sanitización de errores

**Principios**:
- Funciones puras sin estado
- Reutilizables en toda la aplicación
- Sin dependencias de negocio

### Capa 7: Database

**Responsabilidad**: Persistencia de datos

**Características**:
- SQLite con modo WAL (Write-Ahead Logging)
- 40+ tablas normalizadas
- Triggers para timestamps y auditoría
- Vistas para reportes
- Foreign keys con integridad referencial

---

## Flujo de datos

### Operación CRUD típica (Crear Usuario)

```
┌──────┐     (1) Click     ┌────────────┐
│ View │ ───────────────> │ Controller │
└──────┘                   └────────────┘
   ↑                              │
   │                              │ (2) crear_usuario(datos)
   │                              ↓
   │                       ┌─────────┐
   │                       │ Service │ ← Validaciones
   │                       └─────────┘
   │                              │
   │                              │ (3) create(usuario)
   │                              ↓
   │                       ┌────────────┐
   │                       │ Repository │ ← SQL INSERT
   │                       └────────────┘
   │                              │
   │                              │ (4) usuario_id
   │                              ↓
   │ (5) Actualizar UI    ┌─────────┐
   └───────────────────── │ Service │ ← Logger + Auditoría
                          └─────────┘
```

**Pasos detallados**:

1. **Vista → Controller**: Usuario hace clic en "Guardar"
   - Vista valida formato básico (QValidator)
   - Recopila datos del formulario
   - Llama al método del controller

2. **Controller → Service**: Delega operación
   ```python
   usuario, error = self._service.crear_usuario(datos_formulario)
   if error:
       QMessageBox.warning(self.view, "Error", error)
   else:
       QMessageBox.information(self.view, "Éxito", "Usuario creado")
   ```

3. **Service → Repository**: Valida y persiste
   ```python
   # Validaciones de negocio
   if not email or not re.match(patron, email):
       return None, "Email inválido"

   # Hashear contraseña
   hash = bcrypt.hashpw(...)

   # Crear modelo
   usuario = Usuario(nombre=..., email=..., contrasena_hash=hash)

   # Persistir
   usuario_id = self._repo.create(usuario)
   ```

4. **Repository → Database**: Ejecuta SQL
   ```python
   query = """
   INSERT INTO Usuarios (nombre, email, contrasena_hash, ...)
   VALUES (?, ?, ?, ...)
   """
   cursor.execute(query, (usuario.nombre, usuario.email, ...))
   return cursor.lastrowid
   ```

5. **Vuelta a Vista**: Actualiza UI
   - Service registra en log
   - Service registra en auditoría
   - Controller recibe resultado
   - Controller actualiza vista

### Flujo de autenticación

```
┌───────────┐
│ LoginView │
└───────┬───┘
        │ (1) login(email, password)
        ↓
┌──────────────────┐
│ LoginController  │
└────────┬─────────┘
         │ (2) login(email, password)
         ↓
  ┌────────────┐
  │ AuthService│ ← Validar email
  └──────┬─────┘
         │ (3) find_by_email(email)
         ↓
  ┌─────────────────┐
  │UsuarioRepository│ ← SELECT * FROM Usuarios
  └────────┬────────┘
           │ (4) Usuario con hash
           ↓
    ┌────────────┐
    │ AuthService│ ← bcrypt.checkpw()
    └──────┬─────┘
           │ (5) update_ultimo_acceso()
           ↓
    ┌─────────────────┐
    │UsuarioRepository│ ← UPDATE Usuarios
    └────────┬────────┘
             │ (6) Usuario autenticado
             ↓
      ┌──────────────────┐
      │ LoginController  │ ← Guardar sesión
      └────────┬─────────┘
               │ (7) Mostrar MainView
               ↓
          ┌──────────┐
          │ MainView │
          └──────────┘
```

---

## Componentes clave

### 1. Sistema de Logging

**Ubicación**: `app/utils/logger.py`

**Características**:
- Logger centralizado con `AppLogger`
- Rotación automática (10MB por archivo, 5 backups)
- Filtrado recursivo de 15+ tipos de datos sensibles
- Dos archivos: `app.log` (todos) y `errors.log` (solo errores)
- Helpers para logging consistente

**Ejemplo de uso**:
```python
from app.utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)

# Logging normal
logger.info(f"Usuario {usuario_id} creado")

# Con filtrado automático de contraseña
datos = {"email": "user@test.com", "contrasena": "secret123"}
logger.debug(f"Datos: {datos}")  # contrasena se filtra automáticamente

# Logging de excepciones
try:
    # operación
    pass
except Exception as e:
    AppLogger.log_exception(logger, "Contexto del error")
```

### 2. Sistema de Auditoría

**Ubicación**: `app/repositories/auditoria_repository.py`

**Características**:
- Tabla `LogAuditoria` para tracking de operaciones
- Registra CREATE, UPDATE, DELETE
- Almacena valores anteriores y nuevos en JSON
- Asocia operación a usuario responsable
- IP de origen registrada

**Ejemplo de uso**:
```python
from app.repositories.auditoria_repository import AuditoriaRepository

auditoria_repo = AuditoriaRepository()

# Después de crear
auditoria_repo.registrar_accion(
    usuario_id=usuario_actual_id,
    accion="CREATE",
    entidad_tipo="Contacto",
    entidad_id=contacto_id,
    valores_nuevos={"nombre": "Juan", "email": "juan@test.com"}
)

# Después de actualizar
auditoria_repo.registrar_accion(
    usuario_id=usuario_actual_id,
    accion="UPDATE",
    entidad_tipo="Contacto",
    entidad_id=contacto_id,
    valores_anteriores={"nombre": "Juan", "email": "juan@test.com"},
    valores_nuevos={"nombre": "Juan Carlos", "email": "juan@test.com"}
)
```

### 3. Caché de Catálogos

**Ubicación**: `app/utils/catalog_cache.py`

**Características**:
- Caché en memoria con TTL (5 minutos por defecto)
- Invalidación manual al modificar catálogos
- Reducción del 80% en consultas repetitivas
- Thread-safe con verificación de expiración

**Ejemplo de uso**:
```python
from app.utils.catalog_cache import CatalogCache

# Obtener (si existe y no expiró)
industrias = CatalogCache.get('industrias')
if industrias is None:
    # Cache miss o expirado, consultar BD
    industrias = repo.find_all()
    CatalogCache.set('industrias', industrias)

# Invalidar al modificar
CatalogCache.invalidate('industrias')
```

### 4. Sanitización XSS

**Ubicación**: `app/utils/sanitizer.py`

**Características**:
- Escape de HTML con `html.escape()`
- Validación y truncado de longitud
- Constantes de longitud máxima configurables
- Prevención de XSS en notas

**Ejemplo de uso**:
```python
from app.utils.sanitizer import Sanitizer

# Sanitizar contenido
contenido = "<script>alert('XSS')</script>"
sanitizado = Sanitizer.sanitize_string(contenido, max_length=5000)
# Resultado: "&lt;script&gt;alert('XSS')&lt;/script&gt;"

# Validar longitud
if not Sanitizer.validate_length(titulo, max_length=200):
    return None, "Título muy largo"
```

### 5. Manejo de Errores DB

**Ubicación**: `app/utils/db_retry.py`

**Características**:
- Decorador `@retry_on_db_error` para reintentos automáticos
- Backoff exponencial (0.1s, 0.2s, 0.4s)
- Sanitización de mensajes de error para usuarios
- Validación de foreign keys antes de insertar

**Ejemplo de uso**:
```python
from app.utils.db_retry import retry_on_db_error, sanitize_error_message

# Decorador para reintentos
@retry_on_db_error(max_retries=3, delay=0.1, backoff=2)
def insertar_datos(self, datos):
    # Operación que puede fallar por "database locked"
    cursor.execute(...)

# Sanitizar errores
try:
    # operación
    pass
except Exception as e:
    mensaje_usuario = sanitize_error_message(e)
    # "La base de datos está ocupada" en vez de "database is locked"
```

---

## Decisiones arquitectónicas

### 1. ¿Por qué SQLite en vez de PostgreSQL/MySQL?

**Decisión**: SQLite con modo WAL

**Razones**:
- ✅ Aplicación de escritorio (no cliente-servidor)
- ✅ Sin necesidad de instalar servidor de BD
- ✅ Portabilidad: un solo archivo `.db`
- ✅ Suficiente para volúmenes de CRM pequeño/mediano
- ✅ Modo WAL permite concurrencia de lecturas

**Trade-offs**:
- ❌ Escalabilidad limitada vs PostgreSQL
- ❌ Sin usuarios y permisos a nivel BD
- ✅ Simplicidad de deployment

### 2. ¿Por qué Repository + Service en vez de solo Service?

**Decisión**: Dos capas separadas

**Razones**:
- ✅ Separación de responsabilidades (SRP)
- ✅ Repositories: solo SQL, sin validaciones
- ✅ Services: solo negocio, sin SQL
- ✅ Facilita testing (mock repositories)
- ✅ Reutilización de repositories en múltiples services

**Ejemplo**:
```python
# UsuarioRepository puede ser usado por:
# - UsuarioService
# - AuthService
# - AuditoriaService (para obtener nombre de usuario)
```

### 3. ¿Por qué bcrypt en vez de hashlib (SHA-256)?

**Decisión**: bcrypt para contraseñas

**Razones**:
- ✅ Diseñado específicamente para contraseñas
- ✅ Salted automáticamente
- ✅ Adaptativo (puede aumentar costo computacional)
- ✅ Resistente a ataques de fuerza bruta
- ❌ SHA-256 es demasiado rápido (vulnerable a rainbow tables)

### 4. ¿Por qué caché con TTL en vez de invalidación manual?

**Decisión**: Híbrido - TTL + invalidación manual

**Razones**:
- ✅ TTL protege contra datos obsoletos si falla invalidación
- ✅ Invalidación manual da control explícito
- ✅ Mejor de ambos mundos
- ✅ TTL de 5 minutos es razonable para catálogos

### 5. ¿Por qué logging con filtrado automático?

**Decisión**: Logger con filtrado recursivo de datos sensibles

**Razones**:
- ✅ Seguridad by design
- ✅ Desarrolladores no pueden loguear contraseñas accidentalmente
- ✅ Cumplimiento GDPR/LFPDPPP (protección de datos personales)
- ✅ Filtrado recursivo cubre casos complejos (nested dicts)
- ✅ Lista configurable de campos sensibles

---

## Diagramas

### Diagrama de componentes

```
┌────────────────────────────────────────────────────┐
│                   APLICACIÓN CRM                    │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Login   │  │   Main   │  │  Configuración   │ │
│  │  View    │  │  View    │  │      View        │ │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
│       │             │                  │           │
│  ┌────┴──────────────┴──────────────────┴─────┐   │
│  │            Controllers Layer               │   │
│  └────────────────────┬───────────────────────┘   │
│                       │                           │
│  ┌────────────────────┴───────────────────────┐   │
│  │      Services Layer (Business Logic)      │   │
│  │  - Auth  - Usuario  - Empresa  - Contacto │   │
│  │  - Notas - Catálogos                      │   │
│  └────────────────────┬───────────────────────┘   │
│                       │                           │
│  ┌────────────────────┴───────────────────────┐   │
│  │    Repositories Layer (Data Access)       │   │
│  │  - Usuario - Empresa - Contacto - Notas   │   │
│  │  - Catálogos - Auditoría                  │   │
│  └────────────────────┬───────────────────────┘   │
│                       │                           │
│  ┌────────────────────┴───────────────────────┐   │
│  │         Utils (Cross-cutting)             │   │
│  │  - Logger  - Sanitizer  - Validators      │   │
│  │  - Cache   - DB Retry                     │   │
│  └───────────────────────────────────────────┘   │
│                       │                           │
│                       ↓                           │
│              ┌─────────────────┐                  │
│              │  SQLite (WAL)   │                  │
│              │   crm.db        │                  │
│              └─────────────────┘                  │
└────────────────────────────────────────────────────┘
```

---

## Conclusión

Esta arquitectura proporciona:
- ✅ **Mantenibilidad**: Capas bien definidas
- ✅ **Testabilidad**: Desacoplamiento con Repository/Service
- ✅ **Seguridad**: Logging con filtrado, sanitización XSS, bcrypt
- ✅ **Rendimiento**: Caché, paginación, WAL mode
- ✅ **Trazabilidad**: Logging completo + auditoría CRUD
- ✅ **Robustez**: Retry automático, validaciones múltiples niveles
