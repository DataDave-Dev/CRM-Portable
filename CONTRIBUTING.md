# Guía de Contribución - CRM

Bienvenido al proyecto CRM del Equipo #1. Esta guía te ayudará a configurar tu entorno de desarrollo y contribuir al proyecto de manera efectiva.

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Flujo de Trabajo con Git](#flujo-de-trabajo-con-git)
5. [Convenciones de Código](#convenciones-de-código)
6. [Ejecutar Tests](#ejecutar-tests)
7. [Crear Pull Requests](#crear-pull-requests)
8. [Buenas Prácticas](#buenas-prácticas)
9. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.x** - [Descargar aquí](https://www.python.org/downloads/)
- **Git** - [Descargar aquí](https://git-scm.com/downloads)
- **Editor de código** - Recomendamos [VS Code](https://code.visualstudio.com/)
- **Git Bash** (Windows) - Normalmente se instala con Git

### Verificar instalación

```bash
# Verificar Python
python --version

# Verificar Git
git --version
```

---

## Configuración Inicial

### 1. Clonar el repositorio

```bash
# Clonar el proyecto
git clone <URL-DEL-REPOSITORIO>

# Entrar al directorio
cd "CRM-Portable"
```

### 2. Configurar Git (primera vez)

```bash
# Configurar tu nombre
git config --global user.name "Tu Nombre"

# Configurar tu email
git config --global user.email "tu.email@ejemplo.com"
```

### 3. Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows (Git Bash):
source .venv/Scripts/activate

# En Windows (CMD):
.venv\Scripts\activate.bat

# En Linux/Mac:
source .venv/bin/activate
```

**Nota:** Tu terminal debe mostrar `(.venv)` al inicio cuando el entorno esté activado.

### 4. Instalar dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

### 5. Primera ejecución

```bash
# Ejecutar la aplicación
python main.py
```

Al ejecutar por primera vez, verás el asistente de configuración inicial donde crearás tu usuario administrador.

---

## Estructura del Proyecto

Familiarízate con la organización del código:

```
app/
├── assets/              # Iconos SVG
├── config/              # Configuración y catálogos
├── database/            # Conexión y esquema de BD
├── models/              # Modelos de datos (Usuario, Rol, etc.)
├── repositories/        # Capa de acceso a datos (CRUD)
├── services/            # Lógica de negocio
├── controllers/         # Controladores MVC
└── views/               # Interfaces gráficas (PyQt5)
    └── ui/              # Archivos .ui de Qt Designer

db/                      # Base de datos SQLite
├── database_query.sql   # Esquema completo
└── crm.db              # BD generada (no commitear)

tests/                   # Tests unitarios
├── test_utils/
└── test_services/
```

### Capas de la aplicación (patrón MVC)

```
Views → Controllers → Services → Repositories → Database
```

- **Views**: Interfaz gráfica (PyQt5)
- **Controllers**: Control de flujo y eventos
- **Services**: Lógica de negocio y validaciones
- **Repositories**: Operaciones CRUD a la BD

---

## Flujo de Trabajo con Git

### 1. Antes de empezar a trabajar

```bash
# Asegúrate de estar en la rama main
git checkout main

# Actualizar tu código con los cambios remotos
git pull origin main
```

### 2. Crear una rama para tu tarea

Usa nombres descriptivos para las ramas:

```bash
# Formato: tipo/descripcion-corta
git checkout -b feature/agregar-dashboard
git checkout -b fix/corregir-login
git checkout -b refactor/mejorar-validaciones
```

**Tipos de ramas:**
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bugs
- `refactor/` - Refactorización de código
- `docs/` - Documentación
- `test/` - Agregar o mejorar tests

### 3. Hacer cambios

```bash
# Ver archivos modificados
git status

# Ver diferencias
git diff

# Agregar archivos específicos al staging
git add app/controllers/nuevo_controller.py
git add app/views/nueva_view.py

# O agregar todos los cambios
git add .
```

### 4. Crear commits

**Formato de commits:**

```
tipo: descripción breve

Descripción detallada (opcional)
```

**Ejemplos:**

```bash
git commit -m "feat: agregar módulo de reportes

Implementa vista de reportes con filtros por fecha
y exportación a PDF"

git commit -m "fix: corregir validación de email en registro"

git commit -m "refactor: simplificar lógica de autenticación"
```

**Tipos de commits:**
- `feat:` - Nueva característica
- `fix:` - Corrección de bug
- `refactor:` - Refactorización
- `test:` - Agregar tests
- `docs:` - Documentación
- `style:` - Formato de código (sin cambiar lógica)
- `chore:` - Tareas de mantenimiento

### 5. Subir cambios

```bash
# Primera vez (crear rama remota)
git push -u origin feature/tu-rama

# Siguientes veces
git push
```

### 6. Mantener tu rama actualizada

```bash
# Cambiar a main
git checkout main

# Actualizar main
git pull origin main

# Volver a tu rama
git checkout feature/tu-rama

# Integrar cambios de main
git merge main

# Resolver conflictos si los hay (ver más abajo)
```

---

## Convenciones de Código

### Python (PEP 8)

```python
# Nombres de clases: PascalCase
class UsuarioService:
    pass

# Nombres de funciones y variables: snake_case
def validar_email(email: str) -> bool:
    usuario_activo = True

# Constantes: MAYÚSCULAS
MAX_INTENTOS_LOGIN = 3

# Imports ordenados
import os
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from app.services import auth_service
```

### Documentación de funciones

```python
def crear_usuario(nombre: str, email: str) -> Usuario:
    """
    Crea un nuevo usuario en el sistema.

    Args:
        nombre: Nombre completo del usuario
        email: Correo electrónico válido

    Returns:
        Usuario: Objeto Usuario creado

    Raises:
        ValueError: Si el email ya existe
    """
    # Implementación...
```

### Validaciones

Usa siempre el módulo `app/utils/validators.py`:

```python
from app.utils.validators import validar_email, validar_password

# Validar antes de procesar
if not validar_email(email):
    raise ValueError("Email inválido")
```

### Queries SQL

**SIEMPRE usa queries parametrizadas:**

```python
# Correcto
cursor.execute("SELECT * FROM Usuarios WHERE email = ?", (email,))

# Incorrecto (vulnerable a SQL injection)
cursor.execute(f"SELECT * FROM Usuarios WHERE email = '{email}'")
```

---

## Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con salida detallada
pytest -v

# Tests de un módulo específico
pytest tests/test_utils/test_validators.py

# Tests con coverage (si está instalado)
pytest --cov=app
```

### Crear nuevos tests

```python
# tests/test_services/test_nuevo_servicio.py
import pytest
from app.services.nuevo_servicio import NuevoServicio

def test_funcion_basica():
    """Descripción clara de qué se está probando"""
    # Arrange (preparar)
    servicio = NuevoServicio()

    # Act (actuar)
    resultado = servicio.hacer_algo()

    # Assert (verificar)
    assert resultado == esperado
```

---

## Crear Pull Requests

### 1. Asegúrate de que todo funcione

```bash
# Ejecutar tests
pytest

# Ejecutar la aplicación
python main.py
```

### 2. Sube tu rama

```bash
git push origin feature/tu-rama
```

### 3. Crear el PR en GitHub

1. Ve al repositorio en GitHub
2. Verás un botón "Compare & pull request"
3. Completa el formulario:

```markdown
## Descripción
[Describe qué hace este PR]

## Cambios realizados
- Agregué módulo de reportes
- Implementé exportación a PDF
- Agregué tests para validaciones

## Tipo de cambio
- [ ] Nueva funcionalidad (feature)
- [ ] Corrección de bug (fix)
- [ ] Refactorización (refactor)
- [ ] Documentación (docs)

## Checklist
- [ ] El código sigue las convenciones del proyecto
- [ ] Agregué tests para los nuevos cambios
- [ ] Todos los tests pasan
- [ ] Actualicé la documentación si es necesario
- [ ] No hay archivos de base de datos (crm.db) en el commit
```

### 4. Espera revisión

Un compañero revisará tu código y podrá:
- Aprobar el PR
- Solicitar cambios
- Hacer comentarios

### 5. Realizar cambios solicitados

```bash
# Hacer los cambios
git add .
git commit -m "fix: aplicar feedback del code review"
git push
```

El PR se actualizará automáticamente.

---

## Buenas Prácticas

### Commits frecuentes y pequeños

```bash
# Mal (un commit gigante)
git commit -m "feat: implementar todo el módulo de ventas"

# Bien (commits pequeños y lógicos)
git commit -m "feat: agregar modelo de Venta"
git commit -m "feat: implementar VentaRepository"
git commit -m "feat: agregar VentaService con validaciones"
git commit -m "feat: crear vista de lista de ventas"
```

### No commitear archivos temporales

Archivos que **NO** deben estar en Git:
- `crm.db` (base de datos)
- `__pycache__/`
- `.venv/`
- `.DS_Store`
- `.idea/`
- `*.pyc`

El `.gitignore` ya está configurado para ignorar estos archivos.

### Revisar cambios antes de commit

```bash
# Ver qué archivos cambiarán
git status

# Ver las diferencias línea por línea
git diff

# Ver diferencias de archivos staged
git add app/services/nuevo.py
git diff --staged
```

### Escribir buenos mensajes de commit

```bash
# Mal
git commit -m "fix"
git commit -m "cambios"
git commit -m "asldkfj"

# Bien
git commit -m "fix: corregir validación de RFC en formulario de empresa"
git commit -m "feat: agregar filtro por fecha en lista de contactos"
git commit -m "refactor: extraer lógica de validación a utils/validators.py"
```

---

## Solución de Problemas

### Resolver conflictos en merge

Si al hacer `git merge main` aparecen conflictos:

```bash
# Git te dirá qué archivos tienen conflictos
git status

# Abre cada archivo y busca:
<<<<<<< HEAD
tu código
=======
código de main
>>>>>>> main

# Edita el archivo manualmente, decide qué código mantener
# y elimina las marcas <<<<<<, =======, >>>>>>>

# Después de resolver:
git add archivo_resuelto.py
git commit -m "merge: resolver conflictos con main"
```

### Deshacer cambios no commiteados

```bash
# Deshacer cambios en un archivo específico
git checkout -- app/services/archivo.py

# Deshacer todos los cambios
git reset --hard
```

### Ver historial de commits

```bash
# Ver commits recientes
git log --oneline --graph

# Ver cambios de un commit específico
git show <commit-hash>
```

### Cambiar a otra rama sin perder trabajo

```bash
# Guardar cambios temporalmente
git stash

# Cambiar de rama
git checkout otra-rama

# Recuperar cambios después
git checkout tu-rama
git stash pop
```

### Error: "Your branch is behind"

```bash
# Actualizar tu rama local
git pull origin main
```

### Error: "Cannot push to remote"

```bash
# Alguien más hizo cambios. Primero haz pull:
git pull origin tu-rama

# Luego push:
git push
```

---

## Recursos Adicionales

### Documentación del proyecto
- [README.md](README.md) - Documentación general
- [db/database_query.sql](db/database_query.sql) - Esquema de base de datos

### Aprende más sobre Git
- [Git - Guía sencilla](https://rogerdudler.github.io/git-guide/index.es.html)
- [Learn Git Branching (interactivo)](https://learngitbranching.js.org/?locale=es_ES)

### Python y PyQt5
- [PEP 8 - Guía de estilo](https://peps.python.org/pep-0008/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

---

## Contacto

Si tienes dudas:

1. Revisa esta guía primero
2. Pregunta en el grupo del equipo
3. Revisa el código existente para ver ejemplos
4. Consulta con el equipo en clase

---

## Resumen rápido

```bash
# 1. Actualizar main
git checkout main
git pull origin main

# 2. Crear rama
git checkout -b feature/mi-tarea

# 3. Hacer cambios y commit
git add .
git commit -m "feat: descripción del cambio"

# 4. Subir cambios
git push -u origin feature/mi-tarea

# 5. Crear Pull Request en GitHub

# 6. Después de aprobar PR, actualizar main
git checkout main
git pull origin main
```

---

Gracias por contribuir al proyecto. Cada commit nos acerca más a tener un CRM completo y funcional.

**Equipo #1 - Base de Datos y Lenguajes - FIME UANL**
