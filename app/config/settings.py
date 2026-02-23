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

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------

# BASE_DIR: ruta absoluta a la carpeta raiz del proyecto.
#
# Como calcularla:
#   __file__ es la ruta de este archivo settings.py en tiempo de ejecucion.
#   os.path.abspath convierte cualquier ruta relativa a absoluta.
#   os.path.dirname sube un nivel en el arbol de directorios.
#   Al aplicarlo tres veces subimos:
#     1er dirname: config/      -> app/
#     2do dirname: app/         -> Proyecto Equipo #1/
#     3er dirname: no aplica    (ya estamos en la raiz, solo usamos 2 para este archivo)
#
# NOTA: En realidad son 3 os.path.dirname anidados:
#   __file__ = .../app/config/settings.py
#   dirname  = .../app/config/
#   dirname  = .../app/
#   dirname  = .../ (raiz del proyecto = BASE_DIR)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# DB_PATH: ruta absoluta al archivo de base de datos SQLite.
# SQLite guarda toda la base de datos en este unico archivo binario.
# Si el archivo no existe, sqlite3.connect() lo crea automaticamente.
# El archivo se encuentra en la carpeta "db/" dentro del proyecto.
DB_PATH = os.path.join(BASE_DIR, "db", "crm.db")

# SCHEMA_PATH: ruta absoluta al script SQL con la estructura de la base de datos.
# Este archivo contiene las sentencias CREATE TABLE, CREATE INDEX, INSERT de datos
# iniciales (catalogos, roles, etc.) para construir la BD desde cero.
# Se ejecuta solo la primera vez (cuando crm.db no existe aun).
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
