"""
Modulo de inicializacion de la base de datos.

Este modulo se encarga de dos responsabilidades concretas:
  1. Crear la estructura completa de la base de datos (tablas, indices, datos
     semilla) la primera vez que la aplicacion se ejecuta, leyendo el archivo
     SQL de esquema definido en SCHEMA_PATH.
  2. Verificar si ya existen usuarios registrados en el sistema, lo que sirve
     para decidir si se debe mostrar la pantalla de registro inicial o ir
     directamente al login.

Cuando se llama initialize_database():
    - Si el archivo .db YA existe en disco, la funcion regresa inmediatamente
      sin hacer nada. Esto garantiza idempotencia: ejecutar la funcion varias
      veces no borra ni recrea las tablas existentes.
    - Si el archivo .db NO existe, SQLite lo crea al abrir la conexion, y
      luego se ejecuta el script SQL completo para construir el esquema y
      cargar datos iniciales (catálogos, configuraciones, etc.).

Cuando se llama has_users():
    - Se consulta cuantos registros hay en la tabla Usuarios.
    - Devuelve True si hay al menos uno, False si la tabla esta vacia.
    - Se usa en el flujo de arranque para saber si la app necesita mostrar
      el formulario de creacion del primer usuario administrador.

Uso tipico (en el punto de entrada de la aplicacion):
    from app.database.initializer import initialize_database, has_users

    initialize_database()           # crea BD si no existe
    if not has_users():
        show_registro_screen()      # primer arranque
    else:
        show_login_screen()         # arranques normales
"""

import os

# DB_PATH: ruta absoluta al archivo SQLite (ej. .../db/crm.db)
# SCHEMA_PATH: ruta absoluta al archivo .sql con el esquema de la BD
from app.config.settings import DB_PATH, SCHEMA_PATH

# get_connection devuelve la conexion thread-local ya configurada con los
# PRAGMAs necesarios (foreign_keys, WAL, row_factory). Ver connection.py.
from app.database.connection import get_connection


def initialize_database():
    """
    Inicializa la base de datos SQLite si todavia no existe.

    Logica de idempotencia:
        SQLite crea el archivo .db en cuanto se abre una conexion hacia el.
        Para evitar recrear la base de datos en cada inicio de la aplicacion,
        usamos os.path.exists(DB_PATH) como guardia. Si el archivo ya existe
        en disco, significa que la BD fue creada anteriormente y puede contener
        datos de usuario, por lo que salimos inmediatamente sin tocar nada.

    Que hace si la BD NO existe:
        1. Llama a get_connection(), que crea el archivo .db vacio y devuelve
           una conexion configurada con los PRAGMAs necesarios.
        2. Lee el contenido completo del archivo SQL ubicado en SCHEMA_PATH.
           Ese archivo contiene sentencias CREATE TABLE, CREATE INDEX,
           INSERT de datos semilla, etc.
        3. Ejecuta todo el contenido SQL de una sola vez usando executescript().
        4. Hace commit para persistir los cambios en el archivo .db.

    Returns:
        None
    """
    # Guardamos de crear la BD si el archivo ya existe.
    # os.path.exists devuelve True si la ruta apunta a un archivo o directorio
    # que existe en el sistema de archivos, independientemente del SO.
    if os.path.exists(DB_PATH):
        return  # La base de datos ya fue inicializada anteriormente; no hacemos nada.

    # Obtenemos (o creamos) la conexion para el hilo actual.
    # Como DB_PATH no existe aun, sqlite3.connect lo creara en disco.
    conn = get_connection()

    # Abrimos el archivo .sql de esquema en modo lectura.
    # encoding="utf-8" asegura que los caracteres especiales (tildes, enies)
    # del SQL se lean correctamente sin importar la configuracion regional del SO.
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()  # Leemos todo el contenido del .sql como texto.

    # executescript() ejecuta multiples sentencias SQL separadas por punto y
    # coma (;) de una sola vez. A diferencia de execute(), que solo acepta una
    # sentencia, executescript() esta disenado precisamente para cargar scripts
    # completos. Ademas, antes de ejecutar el script, hace un COMMIT implicito
    # de cualquier transaccion pendiente, y no requiere llamar commit() al final
    # (aunque nosotros lo hacemos por claridad y consistencia).
    conn.executescript(schema_sql)

    # Confirmamos los cambios para que queden guardados en el archivo .db.
    # Sin commit(), los cambios podrian perderse si la aplicacion termina
    # de forma inesperada antes de que SQLite los persista en disco.
    conn.commit()


def has_users():
    """
    Verifica si existe al menos un usuario registrado en la base de datos.

    Esta funcion se utiliza durante el arranque de la aplicacion para
    determinar el flujo de navegacion inicial:
      - Si no hay usuarios (primer arranque tras crear la BD), la app debe
        mostrar un formulario para registrar al primer administrador.
      - Si ya hay usuarios, la app va directamente a la pantalla de login.

    La consulta usa COUNT(*) que es la forma mas eficiente de contar filas
    en SQLite: no carga los datos de cada fila en memoria, solo devuelve
    el numero total de registros que cumplen la condicion (en este caso
    todos los de la tabla Usuarios).

    Returns:
        bool: True si hay uno o mas usuarios en la tabla Usuarios,
              False si la tabla esta completamente vacia.
    """
    # Reutilizamos la conexion existente del hilo actual.
    conn = get_connection()

    # Ejecutamos una consulta de agregacion para contar todos los usuarios.
    # fetchone() devuelve la primera (y unica) fila del resultado.
    # Como row_factory = sqlite3.Row, podemos acceder por indice [0] para
    # obtener el valor numerico del COUNT.
    cursor = conn.execute("SELECT COUNT(*) FROM Usuarios")

    # cursor.fetchone()[0] extrae el numero entero del resultado.
    # Comparamos con 0: si es mayor, hay al menos un usuario => True.
    # Si es igual a 0, la tabla esta vacia => False.
    return cursor.fetchone()[0] > 0
