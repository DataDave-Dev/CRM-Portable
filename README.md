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
│   ├── database_query.sql          # Esquema completo (60+ tablas)
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

La base de datos se crea automáticamente en la primera ejecución con datos iniciales precargados (roles, catálogos, datos geográficos y un usuario administrador).

### Credenciales por defecto

| Campo | Valor |
|---|---|
| Email | `admin@crm.com` |
| Contraseña | `admin123` |

---

## Módulos implementados

- [x] Autenticación (login con bcrypt)
- [x] Gestión de usuarios (CRUD completo)
- [x] Gestión de catálogos genérica (13 tipos de catálogo)
- [x] Jerarquía geográfica (Paises, Estados, Ciudades)
- [x] Configuración con navegación por pestañas
- [ ] Gestión de contactos y empresas
- [ ] Pipeline de oportunidades
- [ ] Gestión de actividades
- [ ] Campañas de marketing
- [ ] Reportes y dashboards
- [ ] Gestión de documentos
- [ ] Recordatorios y notificaciones

---

## Validaciones

- Correo electrónico con formato válido (regex)
- Teléfono de 10 dígitos
- Contraseña mínimo 8 caracteres
- Campos requeridos y restricciones de unicidad
- Protección contra eliminación de registros referenciados

---

## Equipo

Proyecto académico - **Equipo #1**
Materia: Base de Datos y Lenguajes | FIME | UANL
Catedrático: M.C. Jorge Alejandro Lozano González
