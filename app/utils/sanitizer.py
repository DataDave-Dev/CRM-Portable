"""
Utilidades de sanitizacion y limpieza de datos para el CRM.

Este modulo provee herramientas para limpiar y normalizar datos antes de
guardarlos en la base de datos o mostrarlos en la interfaz. La sanitizacion
se enfoca en:

  1. Prevencion de XSS: Aunque es una app de escritorio (no web), algunos datos
     podrian mostrarse en componentes que renderizan HTML (como QTextEdit con
     richtext). Escapar caracteres HTML previene que contenido malicioso cause
     problemas si los datos se exportan o se muestran en un visor web.

  2. Normalizacion: Quitar espacios extra, convertir a minusculas donde aplique,
     eliminar caracteres no deseados.

  3. Truncado: Asegurar que los textos no excedan los limites de la BD o la UI.

Diferencia con validators.py:
    - validators.py: Verifica si un dato ES VALIDO (retorna error si no lo es).
    - sanitizer.py:  TRANSFORMA el dato para limpiarlo (retorna el dato limpio).
    Tipicamente se valida ANTES de sanitizar, o se sanitiza y luego valida.
"""

import re
import html


class Sanitizer:
    """
    Coleccion de metodos estaticos para limpiar y normalizar datos.

    Limites de longitud definidos como constantes de clase.
    Reflejan los limites de los campos en la base de datos y la interfaz.
    Estos valores deben mantenerse sincronizados con el schema SQL.
    """

    # Limite para campos de titulo (ej. titulo de una nota, asunto de actividad)
    MAX_TITULO_LENGTH = 200

    # Limite para campos de contenido largo (ej. cuerpo de notas, descripciones)
    MAX_CONTENIDO_LENGTH = 5000

    # Limite para campos de nombre (nombre de persona, empresa, catalogo)
    MAX_NOMBRE_LENGTH = 100

    # Limite para emails segun el estandar RFC 5321 (maximo 254 caracteres)
    MAX_EMAIL_LENGTH = 254

    # Limite para numeros de telefono (incluyendo formato con separadores)
    MAX_TELEFONO_LENGTH = 20

    @staticmethod
    def sanitize_html(text):
        """
        Escapa caracteres especiales de HTML en un texto.

        Convierte caracteres como <, >, &, ", ' en sus equivalentes HTML
        (&lt;, &gt;, &amp;, &quot;, &#x27;) para que se muestren literalmente
        en lugar de ser interpretados como etiquetas HTML.

        Parametros:
            text: Texto a limpiar. Si es None o vacio, se retorna sin cambios.

        Returns:
            El texto con caracteres HTML escapados, o el mismo valor si era None/vacio.

        Ejemplo:
            sanitize_html("<script>alert('xss')</script>")
            -> "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        """
        if not text:
            return text  # retornar None o cadena vacia sin modificar
        return html.escape(str(text))

    @staticmethod
    def sanitize_string(text, max_length=None):
        """
        Limpia y normaliza una cadena de texto para almacenamiento.

        Operaciones realizadas:
        1. Normalizar espacios: " texto   con   espacios " -> "texto con espacios"
           (quita espacios al inicio/fin y colapsa multiples espacios internos a uno)
        2. Escapar HTML: previene XSS y caracteres problematicos en displays
        3. Truncar: si excede max_length, cortar al limite exacto

        Parametros:
            text      : Texto a limpiar. Si es None o vacio, se retorna sin cambios.
            max_length: Longitud maxima permitida. Si es None, no se trunca.

        Returns:
            El texto limpio y normalizado, o el mismo valor si era None/vacio.
        """
        if not text:
            return text

        # Paso 1: Normalizar espacios
        # str.split() sin argumentos divide por cualquier whitespace (espacio, tab, newline)
        # " ".join() vuelve a unir con exactamente un espacio entre cada parte
        cleaned = " ".join(str(text).split())

        # Paso 2: Escapar caracteres HTML para prevenir problemas de visualizacion
        cleaned = html.escape(cleaned)

        # Paso 3: Truncar si la cadena resultante excede el limite permitido
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned

    @staticmethod
    def sanitize_email(email):
        """
        Valida y normaliza una direccion de correo electronico.

        Operaciones:
        1. Quitar espacios al inicio y al final (trim)
        2. Convertir a minusculas (los emails son case-insensitive por convencion)
        3. Validar el formato con una expresion regular basica
        4. Verificar que no exceda el limite de longitud (254 caracteres, RFC 5321)

        Si el email no es valido, retorna None en lugar de el email corregido.
        Esto indica al llamador que el dato no es aceptable y debe rechazarse.

        Parametros:
            email: Direccion de email a procesar.

        Returns:
            El email en minusculas y sin espacios si es valido, o None si no es valido.
        """
        if not email:
            return None  # campo vacio = no se proporciono email (puede ser opcional)

        # Normalizar: quitar espacios y convertir a minusculas
        email = email.strip().lower()

        # Validar formato basico con regex
        # Esta es una validacion rapida; Validator.validate_email hace la misma verificacion
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return None  # formato invalido

        # Verificar que no exceda el limite del estandar RFC 5321
        if len(email) > Sanitizer.MAX_EMAIL_LENGTH:
            return None  # demasiado largo para ser un email valido

        return email

    @staticmethod
    def sanitize_phone(phone):
        """
        Limpia un numero de telefono eliminando caracteres no numericos validos.

        Acepta numeros con formato (ej: "81 1234-5678", "(81) 1234 5678") y los
        limpia manteniendo solo los caracteres: digitos 0-9, +, -, (, ), espacio.
        Esto permite almacenar el numero con su formato original pero sin
        caracteres completamente ajenos.

        Parametros:
            phone: Numero de telefono a limpiar (puede tener formato mixto).

        Returns:
            El numero limpio con solo caracteres validos, o None si quedo vacio
            despues de la limpieza.
        """
        if not phone:
            return None

        # Eliminar cualquier caracter que no sea: digito, +, -, (, ), espacio
        # La clase de caracteres [^0-9+\-() ] niega los caracteres validos
        cleaned = re.sub(r'[^0-9+\-() ]', '', str(phone))

        # Normalizar espacios multiples a uno solo
        cleaned = " ".join(cleaned.split())

        # Aplicar limite de longitud para evitar valores absurdamente largos
        if len(cleaned) > Sanitizer.MAX_TELEFONO_LENGTH:
            cleaned = cleaned[:Sanitizer.MAX_TELEFONO_LENGTH]

        # Si despues de limpiar no quedo nada, retornar None
        return cleaned if cleaned else None

    @staticmethod
    def validate_length(text, min_length=None, max_length=None):
        """
        Verifica si un texto cumple con los limites de longitud dados.

        Diferencia con Validator.validate_length:
            Este metodo retorna bool (True/False), mientras que el de Validator
            retorna None o un mensaje de error. Usar este cuando solo se necesita
            saber si es valido sin importar el mensaje.

        Parametros:
            text      : Texto a verificar.
            min_length: Longitud minima (inclusive). None = sin minimo.
            max_length: Longitud maxima (inclusive). None = sin maximo.

        Returns:
            True si cumple los limites (o si text es None/vacio y min es 0 o None).
            False si no cumple algun limite.
        """
        if not text:
            # Texto vacio es valido solo si no hay minimo o el minimo es 0
            return min_length is None or min_length == 0

        text_length = len(str(text))

        if min_length is not None and text_length < min_length:
            return False  # muy corto

        if max_length is not None and text_length > max_length:
            return False  # muy largo

        return True  # cumple todos los limites

    @staticmethod
    def truncate(text, max_length, suffix="..."):
        """
        Trunca un texto a una longitud maxima agregando un sufijo indicador.

        Util para mostrar textos largos en la interfaz (ej. en celdas de tabla)
        sin cortar abruptamente: agrega "..." para indicar que hay mas contenido.

        Parametros:
            text      : Texto a truncar.
            max_length: Longitud maxima del resultado INCLUYENDO el sufijo.
            suffix    : Cadena que se agrega al final. Por defecto "...".

        Returns:
            El texto original si cabe en max_length, o el texto truncado + sufijo.

        Ejemplo:
            truncate("Esta es una descripcion muy larga", 20, "...")
            -> "Esta es una descr..."  (17 chars del texto + 3 de "...")
        """
        if not text or len(text) <= max_length:
            return text  # el texto cabe completo, no truncar

        # Dejar espacio para el sufijo al calcular cuanto texto cabe
        # ej: max_length=20, suffix="..." (3 chars) -> caben 17 chars del texto
        return text[:max_length - len(suffix)] + suffix
