"""
Configuracion global del proyecto CRM.

Este modulo centraliza todas las rutas y constantes que otras partes
del proyecto necesitan para funcionar. Al tener todo en un solo lugar,
basta con cambiar una linea aqui para afectar a todo el sistema (por ejemplo,
si se cambia la ubicacion de la base de datos o el nombre de la aplicacion).

Rutas calculadas automaticamente:
    Se usa os.path para construir rutas absolutas y portables. Esto garantiza
    que el proyecto funcione en cualquier maquina, sin importar donde se clone
    el repositorio. NUNCA se usan rutas absolutas como "C:/Users/juan/proyecto".

Estructura de directorios esperada:
    Proyecto Equipo #1/          <- BASE_DIR (raiz del proyecto)
    ├── db/
    │   ├── crm.db               <- DB_PATH (base de datos SQLite)
    │   └── database_query.sql   <- SCHEMA_PATH (script de creacion de tablas)
    ├── app/
    │   ├── config/
    │   │   └── settings.py      <- ESTE ARCHIVO (3 niveles abajo de BASE_DIR)
    │   └── ...
    └── main.py
"""

import os
import sys

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------

# Detectar si la aplicacion corre como ejecutable PyInstaller o desde el codigo fuente.
#
# Cuando PyInstaller empaqueta la app:
#   sys.frozen    = True
#   sys.executable = ruta al .exe  (ej. C:\CRM-Sistema\CRM-Sistema.exe)
#   sys._MEIPASS  = ruta a _internal/ con los archivos bundleados
#
# Cuando corre desde el codigo fuente:
#   sys.frozen no existe  -> getattr devuelve False
#   __file__ = .../app/config/settings.py (3 niveles abajo de la raiz)

_IS_FROZEN = getattr(sys, "frozen", False)

if _IS_FROZEN:
    # Directorio que contiene el .exe: aqui se guarda crm.db para que sea
    # visible, movible y respaldable junto con la carpeta del ejecutable.
    BASE_DIR = os.path.dirname(sys.executable)

    # El esquema SQL viene dentro de _internal/db/ (definido en crm.spec).
    # sys._MEIPASS apunta a esa carpeta en tiempo de ejecucion.
    SCHEMA_PATH = os.path.join(sys._MEIPASS, "db", "database_query.sql")

    # La base de datos se crea junto al .exe, NO dentro de _internal/.
    # Mover la carpeta CRM-Sistema/ a otra maquina conserva todos los datos.
    DB_PATH = os.path.join(BASE_DIR, "crm.db")
else:
    # Ejecucion desde el codigo fuente.
    #   __file__ = .../app/config/settings.py
    #   dirname  = .../app/config/
    #   dirname  = .../app/
    #   dirname  = .../ (raiz del proyecto)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH     = os.path.join(BASE_DIR, "db", "crm.db")
    SCHEMA_PATH = os.path.join(BASE_DIR, "db", "database_query.sql")

# ---------------------------------------------------------------------------
# Constantes de la aplicacion
# ---------------------------------------------------------------------------

# APP_NAME: nombre que aparece en la barra de titulo de las ventanas.
APP_NAME = "CRM - Sistema de Gestion"

# WINDOW_WIDTH / WINDOW_HEIGHT: dimensiones de la ventana de login y setup.
# La ventana principal (menu) se abre maximizada, por lo que estas
# constantes solo aplican a las ventanas de autenticacion.
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
