# CRM - Sistema de Gestión de Relaciones con Clientes

Aplicación de escritorio para la gestión de relaciones con clientes (CRM), desarrollada como proyecto académico para la materia de **Base de Datos y Lenguajes** en la Facultad de Ingeniería Mecánica y Eléctrica (FIME) de la Universidad Autónoma de Nuevo León (UANL).

<img width="1102" height="739" alt="imagen" src="https://github.com/user-attachments/assets/74fe877d-3dfb-427f-9b57-0e9dd233b76c" />

---

## Lenguaje y tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.x | Lenguaje principal |
| PyQt5 | 5.15.11 | Framework de interfaz gráfica |
| SQLite3 | (incluido en Python) | Motor de base de datos |
| bcrypt | 5.0.0 | Hashing seguro de contraseñas |

---

## Paradigmas y patrones de diseño

- **MVC (Modelo-Vista-Controlador)**: separación clara entre la lógica de negocio, la presentación y el control del flujo.
- **Patrón Repository**: capa de acceso a datos desacoplada de la lógica de negocio.
- **Arquitectura por capas**: cada capa tiene una responsabilidad única.
- **Singleton**: conexión a base de datos reutilizable a nivel global.
- **Signal-Slot (PyQt5)**: comunicación desacoplada entre componentes de la interfaz.

### Flujo de capas

```
Views (Presentación)
    |
Controllers (Control de flujo)
    |
Services (Lógica de negocio)
    |
Repositories (Acceso a datos)
    |
Database (SQLite)
```

---

## Estructura de carpetas

```
Proyecto Equipo #1/
├── app/                            # Paquete principal de la aplicación
│   ├── assets/                     # Iconos SVG para la interfaz
│   ├── config/                     # Configuración de la app y catálogos
│   │   ├── settings.py
│   │   └── catalogos.py
│   ├── database/                   # Capa de base de datos
│   │   ├── connection.py           # Conexión singleton a SQLite
│   │   └── initializer.py         # Creación de esquema y datos iniciales
│   ├── models/                     # Modelos de datos
│   │   ├── Usuario.py
│   │   ├── Rol.py
│   │   └── Catalogo.py
│   ├── repositories/               # Capa de acceso a datos (CRUD)
│   │   ├── usuario_repository.py
│   │   ├── rol_repository.py
│   │   └── catalogo_repository.py
│   ├── services/                   # Capa de lógica de negocio
│   │   ├── auth_service.py
│   │   ├── usuario_service.py
│   │   └── catalogo_service.py
│   ├── controllers/                # Controladores MVC
│   │   ├── login_controller.py
│   │   └── main_controller.py
│   └── views/                      # Vistas e interfaz gráfica
│       ├── ui/                     # Archivos .ui (Qt Designer)
│       ├── login_view.py
│       ├── main_view.py
│       ├── configuracion_view.py
│       ├── catalogo_list_widget.py
│       ├── catalogo_form_dialog.py
│       └── geografia_widget.py
├── db/                             # Base de datos y esquema SQL
│   ├── database_query.sql          # Esquema completo (40+ tablas)
│   └── crm.db                     # Archivo SQLite generado
├── tests/                          # Pruebas (pendiente)
├── Docs/                           # Documentación del proyecto
├── main.py                         # Punto de entrada de la aplicación
├── requirements.txt                # Dependencias de Python
└── README.md
```

---

## Base de datos

El esquema SQLite contiene **40 tablas**, 7 vistas, triggers e índices. A continuación los módulos principales:

| Módulo | Tablas principales | Descripción |
|---|---|---|
| Usuarios | `Usuarios`, `Roles` | Autenticación y control de acceso |
| Contactos | `Empresas`, `Contactos` | Gestión de cuentas y personas |
| Ventas | `Oportunidades`, `Cotizaciones`, `Productos` | Pipeline comercial |
| Actividades | `Actividades`, `TiposActividad` | Llamadas, reuniones, tareas |
| Campañas | `Campanas`, `Segmentos`, `Etiquetas` | Marketing y segmentación |
| Geografía | `Paises`, `Estados`, `Ciudades` | Jerarquía geográfica |
| Catálogos | `Industrias`, `Monedas`, `Prioridades`, etc. | Tablas de configuración |
| Auditoría | `LogAuditoria`, `Notificaciones` | Trazabilidad y alertas |

### Características de la BD

- Claves foráneas con integridad referencial
- Triggers para timestamps automáticos, historial de etapas y auditoría
- Vistas precalculadas para reportes (pipeline, rendimiento, conversión)
- Modo WAL para mejor rendimiento concurrente

---

## Instalación y ejecución

```bash
# Clonar el repositorio
git clone <url-del-repositorio>

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

### Primera ejecución

La base de datos se crea automáticamente en la primera ejecución con la estructura completa de tablas (roles, catálogos, datos geográficos).

**Al iniciar la aplicación por primera vez**, se mostrará un asistente de configuración inicial que te permitirá crear tu usuario administrador personalizado:

1. La aplicación detecta que no hay usuarios en el sistema
2. Se muestra la ventana de "Configuración Inicial"
3. Completa el formulario con tu información:
   - Nombre
   - Apellido Paterno
   - Correo Electrónico
   - Contraseña (con validación de fortaleza en tiempo real)
   - Confirmación de contraseña
4. Haz clic en "Crear Usuario Administrador"
5. El sistema te redirigirá automáticamente a la pantalla de login
6. Inicia sesión con las credenciales que acabas de crear

**Nota:** No hay credenciales por defecto. El primer usuario siempre debe ser creado manualmente a través del asistente de configuración inicial.

---

## Módulos implementados

- [x] **Autenticación**: Login seguro con bcrypt, actualización de último acceso
- [x] **Gestión de usuarios**: CRUD completo con validaciones robustas
- [x] **Gestión de empresas**: CRUD con validación de RFC, email, teléfono
- [x] **Gestión de contactos**: CRUD con validación de múltiples emails y teléfonos
- [x] **Notas de contacto y empresa**: CRUD con sanitización XSS y auditoría
- [x] **Catálogos genéricos**: 13 tipos de catálogo con caché inteligente
- [x] **Jerarquía geográfica**: Paises, Estados, Ciudades con dependencias
- [x] **Sistema de logging**: Logs rotativos con filtrado de datos sensibles
- [x] **Sistema de auditoría**: Tracking completo de CREATE/UPDATE/DELETE
- [x] **Configuración**: Navegación por pestañas con vistas especializadas
- [ ] Pipeline de oportunidades
- [ ] Gestión de actividades
- [ ] Campañas de marketing
- [ ] Reportes y dashboards
- [ ] Gestión de documentos
- [ ] Recordatorios y notificaciones

---

## Validaciones

El sistema implementa validaciones robustas a través del módulo `app/utils/validators.py`:

- Correo electrónico con formato válido (regex)
- Teléfono de 10 dígitos
- Código postal de 5 dígitos
- RFC mexicano (12-13 caracteres alfanuméricos)
- URLs con formato válido
- Contraseñas con fortaleza mínima:
  - Mínimo 8 caracteres
  - Al menos una mayúscula
  - Al menos una minúscula
  - Al menos un número
  - Validación contra contraseñas comunes
- Campos requeridos y restricciones de unicidad
- Protección contra eliminación de registros referenciados

---

## Mejoras de Seguridad

El proyecto incluye las siguientes mejoras de seguridad implementadas:

### Autenticación Segura
- Contraseñas hasheadas con bcrypt (factor de costo 12)
- Configuración inicial interactiva para crear primer usuario administrador
- Sin credenciales por defecto ni hardcodeadas en el código fuente
- Validación de fortaleza de contraseña en tiempo real durante el registro

### Protección contra Inyección SQL
- Queries parametrizadas en todos los repositorios
- Validación de identificadores SQL (tablas y columnas)
- Whitelist de tablas permitidas en CatalogoRepository
- Validación de columnas en filtros dinámicos

### Validaciones Centralizadas
- Módulo `validators.py` con funciones reutilizables
- Validación de tipos de datos y formatos
- Protección contra entrada maliciosa

### Sanitización de Inputs (Implementado)
- Módulo `sanitizer.py` para prevenir XSS
- Escape automático de HTML en contenido de notas
- Validación de longitud con límites configurables
- Truncado automático de texto excedente

### Sistema de Logging (Implementado)
- Logger centralizado con rotación automática (10MB por archivo)
- Filtrado automático de 15+ tipos de datos sensibles (contraseñas, RFC, tokens, etc.)
- Logs separados: `app.log` (todos los niveles) y `errors.log` (solo errores)
- Registro de operaciones CRUD con usuario responsable
- Stack traces completos en logs de error

### Sistema de Auditoría (Implementado)
- Tabla `LogAuditoria` con registro completo de operaciones
- Tracking de CREATE, UPDATE, DELETE
- Almacenamiento de valores anteriores y nuevos en JSON
- Asociación de operaciones al usuario que las realiza
- IP de origen registrada

### Manejo de Errores (Implementado)
- Sanitización de mensajes de error para usuarios finales
- Reintentos automáticos con backoff exponencial para errores de DB
- Validación de foreign keys antes de insertar
- Mensajes amigables sin exponer detalles técnicos

### Próximas Mejoras Planeadas
- Rate limiting en login
- Encriptación de base de datos con SQLCipher
- Autenticación de dos factores (2FA)

---

## Mejoras de Rendimiento

El proyecto implementa optimizaciones clave para mejorar el rendimiento y escalabilidad:

### Caché de Catálogos
- Sistema de caché en memoria para catálogos frecuentemente consultados
- TTL configurable (5 minutos por defecto)
- Invalidación automática al modificar catálogos
- Reduce consultas repetitivas en carga de formularios
- Implementado en `app/utils/catalog_cache.py`

### Paginación de Datos
- Soporte de paginación en repositorios de Empresas y Contactos
- Límite de 200 registros por página por defecto
- Métodos `find_all(limit, offset)` y `count_all()` en repositorios
- Reduce uso de memoria con grandes volúmenes de datos

### Impacto Esperado
- Reducción de 80% en consultas a BD para carga de formularios
- Uso de memoria estable independiente del volumen de datos

---

## Testing

El proyecto incluye una suite completa de **53 tests unitarios** (100% passing):

### Estructura de Tests
```
tests/
├── test_utils/
│   ├── test_validators.py             # Tests de validaciones (15 tests)
│   ├── test_catalog_cache.py          # Tests de caché (4 tests)
│   └── test_sanitizer.py              # Tests de sanitización (16 tests)
└── test_services/
    ├── test_auth_service.py           # Tests de autenticación (9 tests)
    ├── test_nota_contacto_service.py  # Tests de notas de contacto (9 tests)
    └── test_nota_empresa_service.py   # Tests de notas de empresa (9 tests)
```

### Cobertura de Tests (53 tests - 100% passing)

- **Validadores** (15 tests): 100% de cobertura
  - Validación de email, teléfono, código postal
  - Validación de RFC, URLs
  - Validación de fortaleza de contraseña
  - Validación de rangos numéricos y longitud de texto

- **Autenticación** (9 tests): Tests críticos de seguridad
  - Login exitoso con credenciales correctas
  - Login con email inexistente
  - Login con contraseña incorrecta
  - Login con usuario inactivo
  - Validación de campos vacíos
  - Actualización de último acceso
  - Manejo de errores de base de datos

- **Caché de Catálogos** (4 tests): Tests de rendimiento
  - Verificación de caché en memoria
  - Invalidación de caché
  - Caché con filtros
  - Configuración de TTL

- **Sanitización** (16 tests): Seguridad contra XSS
  - Sanitización de HTML y caracteres especiales
  - Validación de longitud de texto
  - Validación de rangos numéricos
  - Truncado automático de texto largo

- **Notas de Contacto** (9 tests): CRUD completo
  - Creación exitosa con validaciones
  - Validación de contenido requerido
  - Validación de longitud de título y contenido
  - Actualización y eliminación
  - Manejo de errores

- **Notas de Empresa** (9 tests): CRUD completo
  - Misma cobertura que notas de contacto
  - Validaciones de sanitización
  - Integración con auditoría

### Ejecutar Tests
```bash
# Instalar dependencias de testing
pip install pytest pytest-mock

# Ejecutar todos los tests
pytest

# Ejecutar tests con verbose
pytest -v

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ejecutar tests de un módulo específico
pytest tests/test_utils/test_validators.py
```

### Próximos Tests Planeados
- Tests de servicios de Empresas y Contactos (CRUD completo)
- Tests de repositorios
- Tests de integración end-to-end
- Configuración de CI/CD con GitHub Actions

---

## Equipo

Proyecto académico - **Equipo #1**
Materia: Base de Datos y Lenguajes | FIME | UANL
Catedrático: M.C. Jorge Alejandro Lozano González
