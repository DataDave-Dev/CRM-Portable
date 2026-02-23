# =============================================================================
# Modelo de Contacto
# =============================================================================
# Un Contacto representa a una persona fisica dentro del CRM. Puede ser un
# cliente actual, un prospecto, un proveedor, o cualquier individuo con quien
# la empresa mantiene o busca mantener una relacion comercial.
#
# En el patron Repository, esta clase se usa para convertir filas de la tabla
# "Contactos" en objetos Python. El repositorio ejecuta una consulta SQL
# (SELECT ... FROM Contactos) y por cada fila construye una instancia de esta
# clase usando los valores de cada columna.
#
# Distincion entre campos de base de datos y campos JOIN:
#   - Campos de BD: se leen y escriben directamente en la tabla "Contactos".
#   - Campos JOIN: son valores calculados que provienen de hacer JOIN con otras
#     tablas (Empresas, Catalogos, etc.) en la consulta SQL. Solo existen en
#     el objeto Python para facilitar la visualizacion en la interfaz de usuario.
#     Nunca se insertan ni actualizan en la base de datos.
# =============================================================================

from datetime import datetime


class Contacto:
    def __init__(
        self,
        # Identificador unico del contacto en la base de datos (PRIMARY KEY).
        # Es None cuando se crea un nuevo contacto que aun no se ha guardado.
        contacto_id=None,

        # Nombre(s) de pila del contacto. Campo obligatorio.
        nombre="",

        # Primer apellido del contacto. Campo obligatorio.
        apellido_paterno="",

        # Segundo apellido del contacto. Opcional (None si no aplica).
        apellido_materno=None,

        # Correo electronico principal. Se usa para comunicaciones y como
        # identificador alternativo. Debe ser unico en la base de datos.
        email=None,

        # Correo electronico secundario o alternativo del contacto.
        email_secundario=None,

        # Numero de telefono de la oficina o trabajo del contacto.
        telefono_oficina=None,

        # Numero de telefono movil del contacto.
        telefono_celular=None,

        # Cargo o posicion que ocupa el contacto dentro de su empresa.
        # Ejemplo: "Gerente de Compras", "Director Comercial".
        puesto=None,

        # Area o departamento al que pertenece el contacto en su empresa.
        # Ejemplo: "Ventas", "Tecnologia", "Recursos Humanos".
        departamento=None,

        # Clave foranea (FK) que referencia la tabla "Empresas".
        # Indica a que empresa pertenece este contacto.
        # Puede ser None si el contacto es independiente o freelance.
        empresa_id=None,

        # Direccion fisica del contacto (calle, numero, colonia, etc.).
        direccion=None,

        # Clave foranea (FK) que referencia la tabla de catalogo "Ciudades".
        # Indica la ciudad de residencia o trabajo del contacto.
        ciudad_id=None,

        # Codigo postal correspondiente a la direccion del contacto.
        codigo_postal=None,

        # Fecha de nacimiento del contacto. Se usa para enviar felicitaciones
        # automaticas o personalizar la comunicacion. Formato: "YYYY-MM-DD".
        fecha_nacimiento=None,

        # URL del perfil de LinkedIn del contacto. Util para investigacion
        # previa a reuniones y para mantener la red de contactos actualizada.
        linkedin_url=None,

        # Clave foranea (FK) que referencia el catalogo de "Origenes".
        # Indica como se obtuvo este contacto: referido, web, evento, llamada
        # en frio, etc. Sirve para medir la efectividad de canales de captacion.
        origen_id=None,

        # Clave foranea (FK) que referencia la tabla "Usuarios".
        # Indica el vendedor o empleado responsable de gestionar este contacto.
        propietario_id=None,

        # Bandera que indica si este es el contacto principal de su empresa.
        # 0 = no es principal, 1 = es el contacto principal.
        # Util cuando una empresa tiene multiples contactos registrados.
        es_contacto_principal=0,

        # Bandera que indica si el contacto solicito no ser contactado.
        # 0 = puede contactarse, 1 = no contactar (opt-out).
        # IMPORTANTE: respetar este campo para cumplir con regulaciones de
        # privacidad como GDPR o LFPDPPP (Mexico).
        no_contactar=0,

        # Indica si el registro del contacto esta activo en el sistema.
        # 1 = activo (visible y operable), 0 = inactivo (archivado).
        # Se usa para "eliminar" contactos sin borrarlos fisicamente de la BD.
        activo=1,

        # URL o ruta a la foto o avatar del contacto.
        # Puede ser una ruta local o una URL externa.
        foto_url=None,

        # Marca de tiempo en que se creo el registro en la base de datos.
        # Si no se proporciona, se asigna automaticamente la fecha y hora
        # actuales al momento de instanciar el objeto. Formato: "YYYY-MM-DD HH:MM:SS".
        fecha_creacion=None,

        # Marca de tiempo de la ultima modificacion del registro.
        # Se actualiza cada vez que se edita el contacto. Puede ser None
        # si el registro nunca ha sido modificado desde su creacion.
        fecha_modificacion=None,

        # Clave foranea (FK) al usuario que creo este registro originalmente.
        creado_por=None,

        # Clave foranea (FK) al usuario que realizo la ultima modificacion.
        modificado_por=None,

        # --- Campos JOIN para visualizacion (no se guardan en BD) ----------
        # Los siguientes campos NO forman parte de la tabla "Contactos" en
        # SQLite. Se obtienen mediante JOIN con otras tablas en la consulta
        # SQL del repositorio. Su unico proposito es evitar consultas
        # adicionales al momento de mostrar datos en la interfaz de usuario.

        # Nombre de la empresa a la que pertenece el contacto.
        # Viene de JOIN con la tabla "Empresas" usando empresa_id.
        nombre_empresa=None,

        # Nombre de la ciudad del contacto.
        # Viene de JOIN con el catalogo "Ciudades" usando ciudad_id.
        nombre_ciudad=None,

        # Nombre del origen del contacto (ej. "Referido", "Web", "Evento").
        # Viene de JOIN con el catalogo "Origenes" usando origen_id.
        nombre_origen=None,

        # Nombre completo del usuario propietario/responsable del contacto.
        # Viene de JOIN con la tabla "Usuarios" usando propietario_id.
        nombre_propietario=None,
    ):
        # --- Asignacion de campos de base de datos ---
        self.contacto_id = contacto_id
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.email_secundario = email_secundario
        self.telefono_oficina = telefono_oficina
        self.telefono_celular = telefono_celular
        self.puesto = puesto
        self.departamento = departamento
        self.empresa_id = empresa_id
        self.direccion = direccion
        self.ciudad_id = ciudad_id
        self.codigo_postal = codigo_postal
        self.fecha_nacimiento = fecha_nacimiento
        self.linkedin_url = linkedin_url
        self.origen_id = origen_id
        self.propietario_id = propietario_id
        self.es_contacto_principal = es_contacto_principal
        self.no_contactar = no_contactar
        self.activo = activo
        self.foto_url = foto_url
        # Si no se proporciona fecha_creacion (nuevo registro), se genera
        # automaticamente con la fecha y hora del momento de creacion del objeto.
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.creado_por = creado_por
        self.modificado_por = modificado_por

        # --- Asignacion de campos JOIN (solo para visualizacion) ---
        self.nombre_empresa = nombre_empresa
        self.nombre_ciudad = nombre_ciudad
        self.nombre_origen = nombre_origen
        self.nombre_propietario = nombre_propietario

    def __repr__(self):
        # Representacion de cadena del objeto para facilitar el debugging.
        # Al imprimir o inspeccionar un objeto Contacto en la consola, se
        # mostrara su ID y nombre completo, lo que facilita identificarlo
        # rapidamente sin necesidad de inspeccionar todos sus atributos.
        return f"<Contacto(id={self.contacto_id}, nombre='{self.nombre} {self.apellido_paterno}')>"
