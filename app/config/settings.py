# Configuracion general del proyecto (rutas, nombre de la app, etc)

import os

# sacar la ruta raiz del proyecto (subimos 3 niveles desde este archivo)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "db", "crm.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "database_query.sql")

APP_NAME = "CRM - Sistema de Gestion"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500