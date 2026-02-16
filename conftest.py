# configuracion de pytest - agrega el directorio raiz al path para imports

import sys
import os

# agregar directorio raiz al path de Python para que encuentre el modulo app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
