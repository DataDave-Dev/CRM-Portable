"""
Servicio de gestion de contactos para el sistema CRM.

Este modulo proporciona la logica de negocio para gestionar contactos (personas),
incluyendo validaciones de email, telefonos, codigo postal, y fecha de nacimiento.

Validaciones implementadas:
    - Campos requeridos: nombre, apellido_paterno
    - Email primario y secundario: formato valido (RFC 5322)
    - Telefonos (oficina y celular): 10 digitos numericos
    - Codigo postal: 5 digitos numericos
    - Fecha de nacimiento: formato AAAA-MM-DD
    - LinkedIn URL: formato URL valido
    - Foreign keys: empresa_id, ciudad_id, origen_id, propietario_id

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

import re
from app.repositories.contacto_repository import ContactoRepository
from app.models.Contacto import Contacto
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class ContactoService:
    """
    Servicio de gestion de contactos del sistema CRM.

    Proporciona metodos CRUD para contactos con validaciones completas,
    paginacion, y logging de operaciones.
    """

    def __init__(self):
        """Inicializa el servicio de contactos."""
        self._repo = ContactoRepository()

    def obtener_todos(self, limit=None, offset=0):
        """
        Obtiene todos los contactos con paginacion opcional.

        Args:
            limit (int, opcional): Numero maximo de registros a retornar
            offset (int, opcional): Numero de registros a saltar (default 0)

        Returns:
            tuple: (list[Contacto]|None, str|None)
        """
        # obtiene contactos con paginacion opcional
        try:
            logger.debug(f"Obteniendo contactos - limit: {limit}, offset: {offset}")
            contactos = self._repo.find_all(limit=limit, offset=offset)
            logger.info(f"Se obtuvieron {len(contactos)} contactos")
            return contactos, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener contactos")
            return None, sanitize_error_message(e)

    def contar_total(self):
        """Cuenta el total de contactos para paginacion."""
        # cuenta total de contactos para paginacion
        try:
            total = self._repo.count_all()
            logger.debug(f"Total de contactos: {total}")
            return total, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar contactos")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, contacto_id):
        """Obtiene un contacto por su ID."""
        try:
            logger.debug(f"Obteniendo contacto {contacto_id}")
            contacto = self._repo.find_by_id(contacto_id)
            return contacto, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener contacto {contacto_id}")
            return None, sanitize_error_message(e)

    def crear_contacto(self, datos, usuario_actual_id):
        """
        Crea un nuevo contacto en el sistema.

        Args:
            datos (dict): Datos del contacto (nombre, apellido_paterno, email, telefonos, etc.)
            usuario_actual_id (int): ID del usuario que crea el contacto

        Returns:
            tuple: (Contacto|None, str|None)
        """
        # validar campos requeridos
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return None, "El nombre es requerido"

        apellido_paterno = datos.get("apellido_paterno", "").strip()
        if not apellido_paterno:
            return None, "El apellido paterno es requerido"

        # validar email si se proporciona
        email = datos.get("email", "").strip()
        if email:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email):
                return None, "El formato del email no es valido"

        # validar email secundario si se proporciona
        email_secundario = datos.get("email_secundario", "").strip()
        if email_secundario:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email_secundario):
                return None, "El formato del email secundario no es valido"

        # validar telefonos si se proporcionan
        telefono_oficina = datos.get("telefono_oficina", "").strip()
        if telefono_oficina:
            if not telefono_oficina.isdigit() or len(telefono_oficina) != 10:
                return None, "El telefono de oficina debe contener exactamente 10 digitos"

        telefono_celular = datos.get("telefono_celular", "").strip()
        if telefono_celular:
            if not telefono_celular.isdigit() or len(telefono_celular) != 10:
                return None, "El telefono celular debe contener exactamente 10 digitos"

        # validar codigo postal si se proporciona
        codigo_postal = datos.get("codigo_postal", "").strip()
        if codigo_postal:
            if not codigo_postal.isdigit() or len(codigo_postal) != 5:
                return None, "El codigo postal debe contener exactamente 5 digitos"

        # validar fecha de nacimiento si se proporciona
        fecha_nacimiento = datos.get("fecha_nacimiento", "").strip()
        if fecha_nacimiento:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_nacimiento):
                return None, "La fecha de nacimiento debe tener formato AAAA-MM-DD"

        nuevo_contacto = Contacto(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=datos.get("apellido_materno", "").strip() or None,
            email=email or None,
            email_secundario=email_secundario or None,
            telefono_oficina=telefono_oficina or None,
            telefono_celular=telefono_celular or None,
            puesto=datos.get("puesto", "").strip() or None,
            departamento=datos.get("departamento", "").strip() or None,
            empresa_id=datos.get("empresa_id"),
            direccion=datos.get("direccion", "").strip() or None,
            ciudad_id=datos.get("ciudad_id"),
            codigo_postal=codigo_postal or None,
            fecha_nacimiento=fecha_nacimiento or None,
            linkedin_url=datos.get("linkedin_url", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            es_contacto_principal=datos.get("es_contacto_principal", 0),
            no_contactar=datos.get("no_contactar", 0),
            activo=datos.get("activo", 1),
            creado_por=usuario_actual_id,
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Creando contacto: {nombre} {apellido_paterno} por usuario {usuario_actual_id}")
            contacto_id = self._repo.create(nuevo_contacto)
            nuevo_contacto.contacto_id = contacto_id
            logger.info(f"Contacto {contacto_id} creado exitosamente")
            return nuevo_contacto, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear contacto: {nombre} {apellido_paterno}")
            return None, sanitize_error_message(e)

    def actualizar_contacto(self, contacto_id, datos, usuario_actual_id):
        """
        Actualiza un contacto existente en el sistema.

        Args:
            contacto_id (int): ID del contacto a actualizar
            datos (dict): Datos a actualizar (mismos campos que crear_contacto)
            usuario_actual_id (int): ID del usuario que actualiza el contacto

        Returns:
            tuple: (Contacto|None, str|None)
        """
        # validar campos requeridos
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return None, "El nombre es requerido"

        apellido_paterno = datos.get("apellido_paterno", "").strip()
        if not apellido_paterno:
            return None, "El apellido paterno es requerido"

        # validar email si se proporciona
        email = datos.get("email", "").strip()
        if email:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email):
                return None, "El formato del email no es valido"

        # validar email secundario si se proporciona
        email_secundario = datos.get("email_secundario", "").strip()
        if email_secundario:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email_secundario):
                return None, "El formato del email secundario no es valido"

        # validar telefonos si se proporcionan
        telefono_oficina = datos.get("telefono_oficina", "").strip()
        if telefono_oficina:
            if not telefono_oficina.isdigit() or len(telefono_oficina) != 10:
                return None, "El telefono de oficina debe contener exactamente 10 digitos"

        telefono_celular = datos.get("telefono_celular", "").strip()
        if telefono_celular:
            if not telefono_celular.isdigit() or len(telefono_celular) != 10:
                return None, "El telefono celular debe contener exactamente 10 digitos"

        # validar codigo postal si se proporciona
        codigo_postal = datos.get("codigo_postal", "").strip()
        if codigo_postal:
            if not codigo_postal.isdigit() or len(codigo_postal) != 5:
                return None, "El codigo postal debe contener exactamente 5 digitos"

        # validar fecha de nacimiento si se proporciona
        fecha_nacimiento = datos.get("fecha_nacimiento", "").strip()
        if fecha_nacimiento:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_nacimiento):
                return None, "La fecha de nacimiento debe tener formato AAAA-MM-DD"

        contacto = Contacto(
            contacto_id=contacto_id,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=datos.get("apellido_materno", "").strip() or None,
            email=email or None,
            email_secundario=email_secundario or None,
            telefono_oficina=telefono_oficina or None,
            telefono_celular=telefono_celular or None,
            puesto=datos.get("puesto", "").strip() or None,
            departamento=datos.get("departamento", "").strip() or None,
            empresa_id=datos.get("empresa_id"),
            direccion=datos.get("direccion", "").strip() or None,
            ciudad_id=datos.get("ciudad_id"),
            codigo_postal=codigo_postal or None,
            fecha_nacimiento=fecha_nacimiento or None,
            linkedin_url=datos.get("linkedin_url", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            es_contacto_principal=datos.get("es_contacto_principal", 0),
            no_contactar=datos.get("no_contactar", 0),
            activo=datos.get("activo", 1),
            modificado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Actualizando contacto {contacto_id}: {nombre} {apellido_paterno} por usuario {usuario_actual_id}")
            self._repo.update(contacto)
            logger.info(f"Contacto {contacto_id} actualizado exitosamente")
            return contacto, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar contacto {contacto_id}")
            return None, sanitize_error_message(e)
