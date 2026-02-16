# Logica de negocio para gestionar empresas

import re
from app.repositories.empresa_repository import EmpresaRepository
from app.models.Empresa import Empresa


class EmpresaService:
    def __init__(self):
        self._repo = EmpresaRepository()

    def obtener_todas(self, limit=None, offset=0):
        # obtiene empresas con paginacion opcional
        try:
            return self._repo.find_all(limit=limit, offset=offset), None
        except Exception as e:
            return None, f"Error al obtener empresas: {str(e)}"

    def contar_total(self):
        # cuenta total de empresas para paginacion
        try:
            return self._repo.count_all(), None
        except Exception as e:
            return None, f"Error al contar empresas: {str(e)}"

    def obtener_por_id(self, empresa_id):
        try:
            return self._repo.find_by_id(empresa_id), None
        except Exception as e:
            return None, f"Error al obtener empresa: {str(e)}"

    def crear_empresa(self, datos, usuario_actual_id):
        # validar campos requeridos
        razon_social = datos.get("razon_social", "").strip()
        if not razon_social:
            return None, "La razon social es requerida"

        # validar RFC si se proporciona
        rfc = datos.get("rfc", "").strip()
        if rfc:
            if not re.match(r"^[A-Za-z0-9]{12,13}$", rfc):
                return None, "El RFC debe contener 12 o 13 caracteres alfanumericos"
            if self._repo.rfc_exists(rfc):
                return None, "Este RFC ya esta registrado"

        # validar email si se proporciona
        email = datos.get("email", "").strip()
        if email:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email):
                return None, "El formato del email no es valido"

        # validar telefono si se proporciona
        telefono = datos.get("telefono", "").strip()
        if telefono:
            if not telefono.isdigit() or len(telefono) != 10:
                return None, "El telefono debe contener exactamente 10 digitos"

        # validar codigo postal si se proporciona
        codigo_postal = datos.get("codigo_postal", "").strip()
        if codigo_postal:
            if not codigo_postal.isdigit() or len(codigo_postal) != 5:
                return None, "El codigo postal debe contener exactamente 5 digitos"

        # validar ingreso anual si se proporciona
        ingreso_anual = datos.get("ingreso_anual_estimado")
        if ingreso_anual is not None and ingreso_anual != "":
            try:
                ingreso_anual = float(ingreso_anual)
                if ingreso_anual < 0:
                    return None, "El ingreso anual estimado no puede ser negativo"
            except (ValueError, TypeError):
                return None, "El ingreso anual estimado debe ser un numero valido"
        else:
            ingreso_anual = None

        # validar numero de empleados si se proporciona
        num_empleados = datos.get("num_empleados")
        if num_empleados is not None and num_empleados != "":
            try:
                num_empleados = int(num_empleados)
                if num_empleados < 0:
                    return None, "El numero de empleados no puede ser negativo"
            except (ValueError, TypeError):
                return None, "El numero de empleados debe ser un numero entero valido"
        else:
            num_empleados = None

        nueva_empresa = Empresa(
            razon_social=razon_social,
            nombre_comercial=datos.get("nombre_comercial", "").strip() or None,
            rfc=rfc.upper() or None,
            industria_id=datos.get("industria_id"),
            tamano_id=datos.get("tamano_id"),
            sitio_web=datos.get("sitio_web", "").strip() or None,
            telefono=telefono or None,
            email=email or None,
            direccion=datos.get("direccion", "").strip() or None,
            ciudad_id=datos.get("ciudad_id"),
            codigo_postal=codigo_postal or None,
            ingreso_anual_estimado=ingreso_anual,
            moneda_id=datos.get("moneda_id"),
            num_empleados=num_empleados,
            descripcion=datos.get("descripcion", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            activo=datos.get("activo", 1),
            creado_por=usuario_actual_id,
            modificado_por=usuario_actual_id,
        )

        try:
            empresa_id = self._repo.create(nueva_empresa)
            nueva_empresa.empresa_id = empresa_id
            return nueva_empresa, None
        except Exception as e:
            return None, f"Error al crear empresa: {str(e)}"

    def actualizar_empresa(self, empresa_id, datos, usuario_actual_id):
        # validar campos requeridos
        razon_social = datos.get("razon_social", "").strip()
        if not razon_social:
            return None, "La razon social es requerida"

        # validar RFC si se proporciona
        rfc = datos.get("rfc", "").strip()
        if rfc:
            if not re.match(r"^[A-Za-z0-9]{12,13}$", rfc):
                return None, "El RFC debe contener 12 o 13 caracteres alfanumericos"
            if self._repo.rfc_exists(rfc, excluir_id=empresa_id):
                return None, "Este RFC ya esta registrado por otra empresa"

        # validar email si se proporciona
        email = datos.get("email", "").strip()
        if email:
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, email):
                return None, "El formato del email no es valido"

        # validar telefono si se proporciona
        telefono = datos.get("telefono", "").strip()
        if telefono:
            if not telefono.isdigit() or len(telefono) != 10:
                return None, "El telefono debe contener exactamente 10 digitos"

        # validar codigo postal si se proporciona
        codigo_postal = datos.get("codigo_postal", "").strip()
        if codigo_postal:
            if not codigo_postal.isdigit() or len(codigo_postal) != 5:
                return None, "El codigo postal debe contener exactamente 5 digitos"

        # validar ingreso anual si se proporciona
        ingreso_anual = datos.get("ingreso_anual_estimado")
        if ingreso_anual is not None and ingreso_anual != "":
            try:
                ingreso_anual = float(ingreso_anual)
                if ingreso_anual < 0:
                    return None, "El ingreso anual estimado no puede ser negativo"
            except (ValueError, TypeError):
                return None, "El ingreso anual estimado debe ser un numero valido"
        else:
            ingreso_anual = None

        # validar numero de empleados si se proporciona
        num_empleados = datos.get("num_empleados")
        if num_empleados is not None and num_empleados != "":
            try:
                num_empleados = int(num_empleados)
                if num_empleados < 0:
                    return None, "El numero de empleados no puede ser negativo"
            except (ValueError, TypeError):
                return None, "El numero de empleados debe ser un numero entero valido"
        else:
            num_empleados = None

        empresa = Empresa(
            empresa_id=empresa_id,
            razon_social=razon_social,
            nombre_comercial=datos.get("nombre_comercial", "").strip() or None,
            rfc=rfc.upper() or None,
            industria_id=datos.get("industria_id"),
            tamano_id=datos.get("tamano_id"),
            sitio_web=datos.get("sitio_web", "").strip() or None,
            telefono=telefono or None,
            email=email or None,
            direccion=datos.get("direccion", "").strip() or None,
            ciudad_id=datos.get("ciudad_id"),
            codigo_postal=codigo_postal or None,
            ingreso_anual_estimado=ingreso_anual,
            moneda_id=datos.get("moneda_id"),
            num_empleados=num_empleados,
            descripcion=datos.get("descripcion", "").strip() or None,
            origen_id=datos.get("origen_id"),
            propietario_id=datos.get("propietario_id"),
            activo=datos.get("activo", 1),
            modificado_por=usuario_actual_id,
        )

        try:
            self._repo.update(empresa)
            return empresa, None
        except Exception as e:
            return None, f"Error al actualizar empresa: {str(e)}"
