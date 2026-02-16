# Logica de negocio para gestionar contactos

import re
from app.repositories.contacto_repository import ContactoRepository
from app.models.Contacto import Contacto


class ContactoService:
    def __init__(self):
        self._repo = ContactoRepository()

    def obtener_todos(self, limit=None, offset=0):
        # obtiene contactos con paginacion opcional
        try:
            return self._repo.find_all(limit=limit, offset=offset), None
        except Exception as e:
            return None, f"Error al obtener contactos: {str(e)}"

    def contar_total(self):
        # cuenta total de contactos para paginacion
        try:
            return self._repo.count_all(), None
        except Exception as e:
            return None, f"Error al contar contactos: {str(e)}"

    def obtener_por_id(self, contacto_id):
        try:
            return self._repo.find_by_id(contacto_id), None
        except Exception as e:
            return None, f"Error al obtener contacto: {str(e)}"

    def crear_contacto(self, datos, usuario_actual_id):
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
            contacto_id = self._repo.create(nuevo_contacto)
            nuevo_contacto.contacto_id = contacto_id
            return nuevo_contacto, None
        except Exception as e:
            return None, f"Error al crear contacto: {str(e)}"

    def actualizar_contacto(self, contacto_id, datos, usuario_actual_id):
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
            self._repo.update(contacto)
            return contacto, None
        except Exception as e:
            return None, f"Error al actualizar contacto: {str(e)}"
