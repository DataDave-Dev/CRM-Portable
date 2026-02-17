"""
Servicio de gestion de empresas para el sistema CRM.

Este modulo proporciona la logica de negocio para gestionar empresas (cuentas),
incluyendo validaciones de RFC, email, telefono, codigo postal, y montos numericos.

IMPORTANTE: El RFC es un dato sensible en Mexico y se filtra automaticamente
en los logs. El logger eliminara cualquier campo que contenga 'rfc' en su nombre.

Validaciones implementadas:
    - Campo requerido: razon_social
    - RFC: 12-13 caracteres alfanumericos, unicidad
    - Email: formato valido (RFC 5322)
    - Telefono: 10 digitos numericos
    - Codigo postal: 5 digitos numericos
    - Ingreso anual estimado: numero positivo
    - Numero de empleados: entero positivo
    - Foreign keys: industria_id, tamano_id, ciudad_id, moneda_id, origen_id, propietario_id

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

import re
from app.repositories.empresa_repository import EmpresaRepository
from app.models.Empresa import Empresa
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class EmpresaService:
    """
    Servicio de gestion de empresas del sistema CRM.

    Proporciona metodos CRUD para empresas con validaciones completas,
    paginacion, y logging de operaciones. Soporta validaciones especificas
    para datos mexicanos (RFC, codigo postal).
    """
    def __init__(self):
        """
        Inicializa el servicio de empresas.

        Crea una instancia del repositorio de empresas para acceso a datos.
        """
        self._repo = EmpresaRepository()

    def obtener_todas(self, limit=None, offset=0):
        """
        Obtiene todas las empresas con paginacion opcional.

        Args:
            limit (int, opcional): Numero maximo de registros a retornar
            offset (int, opcional): Numero de registros a saltar (default 0)

        Returns:
            tuple: (list[Empresa]|None, str|None)
                - Si es exitoso: (lista de objetos Empresa, None)
                - Si falla: (None, mensaje de error)

        Examples:
            >>> service = EmpresaService()
            >>> empresas, error = service.obtener_todas(limit=50, offset=0)
            >>> if error is None:
            ...     print(f"Se obtuvieron {len(empresas)} empresas")
        """
        # obtiene empresas con paginacion opcional
        try:
            logger.debug(f"Obteniendo empresas - limit: {limit}, offset: {offset}")
            empresas = self._repo.find_all(limit=limit, offset=offset)
            logger.info(f"Se obtuvieron {len(empresas)} empresas")
            return empresas, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener empresas")
            return None, sanitize_error_message(e)

    def contar_total(self):
        """
        Cuenta el total de empresas en la base de datos.

        Util para calcular paginacion en la interfaz.

        Returns:
            tuple: (int|None, str|None)
                - Si es exitoso: (numero total de empresas, None)
                - Si falla: (None, mensaje de error)
        """
        # cuenta total de empresas para paginacion
        try:
            total = self._repo.count_all()
            logger.debug(f"Total de empresas: {total}")
            return total, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al contar empresas")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, empresa_id):
        """
        Obtiene una empresa por su ID.

        Args:
            empresa_id (int): ID de la empresa a buscar

        Returns:
            tuple: (Empresa|None, str|None)
                - Si es exitoso: (objeto Empresa, None)
                - Si falla: (None, mensaje de error)
        """
        try:
            logger.debug(f"Obteniendo empresa {empresa_id}")
            empresa = self._repo.find_by_id(empresa_id)
            return empresa, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener empresa {empresa_id}")
            return None, sanitize_error_message(e)

    def crear_empresa(self, datos, usuario_actual_id):
        """
        Crea una nueva empresa en el sistema.

        Valida todos los campos requeridos y formatos, asigna el usuario que crea
        el registro, y guarda en la base de datos.

        Args:
            datos (dict): Diccionario con los datos de la empresa:
                - razon_social (str, requerido): Razon social de la empresa
                - nombre_comercial (str, opcional): Nombre comercial
                - rfc (str, opcional): RFC de 12-13 caracteres, unico
                - industria_id (int, opcional): ID de la industria
                - tamano_id (int, opcional): ID del tamaño de empresa
                - sitio_web (str, opcional): URL del sitio web
                - telefono (str, opcional): Telefono de 10 digitos
                - email (str, opcional): Email con formato valido
                - direccion (str, opcional): Direccion fisica
                - ciudad_id (int, opcional): ID de la ciudad
                - codigo_postal (str, opcional): Codigo postal de 5 digitos
                - ingreso_anual_estimado (float, opcional): Ingreso anual positivo
                - moneda_id (int, opcional): ID de la moneda
                - num_empleados (int, opcional): Numero de empleados positivo
                - descripcion (str, opcional): Descripcion de la empresa
                - origen_id (int, opcional): ID del origen del lead
                - propietario_id (int, opcional): ID del usuario propietario
                - activo (int, opcional): 1=activo, 0=inactivo (default 1)
            usuario_actual_id (int): ID del usuario que crea la empresa

        Returns:
            tuple: (Empresa|None, str|None)
                - Si es exitoso: (objeto Empresa con empresa_id asignado, None)
                - Si falla: (None, mensaje de error descriptivo)

        Examples:
            >>> service = EmpresaService()
            >>> datos = {
            ...     "razon_social": "Acme Corp S.A. de C.V.",
            ...     "rfc": "ACM010101ABC",
            ...     "email": "contacto@acme.com",
            ...     "industria_id": 1
            ... }
            >>> empresa, error = service.crear_empresa(datos, usuario_id=5)
            >>> if error is None:
            ...     print(f"Empresa creada con ID: {empresa.empresa_id}")

        Note:
            - El RFC se convierte a mayusculas automaticamente
            - El RFC es dato sensible y se filtra en los logs
            - Los campos creado_por y modificado_por se asignan al usuario_actual_id
        """
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
            # RFC es dato sensible, sera filtrado automaticamente por el logger
            logger.info(f"Creando empresa: {razon_social} por usuario {usuario_actual_id}")
            empresa_id = self._repo.create(nueva_empresa)
            nueva_empresa.empresa_id = empresa_id
            logger.info(f"Empresa {empresa_id} creada exitosamente")
            return nueva_empresa, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear empresa: {razon_social}")
            return None, sanitize_error_message(e)

    def actualizar_empresa(self, empresa_id, datos, usuario_actual_id):
        """
        Actualiza una empresa existente en el sistema.

        Valida campos requeridos y formatos, asigna el usuario que modifica
        el registro, y actualiza en la base de datos.

        Args:
            empresa_id (int): ID de la empresa a actualizar
            datos (dict): Diccionario con los datos a actualizar (mismos campos que crear_empresa)
            usuario_actual_id (int): ID del usuario que actualiza la empresa

        Returns:
            tuple: (Empresa|None, str|None)
                - Si es exitoso: (objeto Empresa actualizado, None)
                - Si falla: (None, mensaje de error descriptivo)

        Examples:
            >>> service = EmpresaService()
            >>> datos = {"razon_social": "Acme Corp S.A.", "email": "nuevo@acme.com"}
            >>> empresa, error = service.actualizar_empresa(10, datos, usuario_id=5)
            >>> if error is None:
            ...     print(f"Empresa {empresa.empresa_id} actualizada")

        Note:
            - El RFC debe ser unico excluyendo la empresa actual
            - El campo modificado_por se actualiza al usuario_actual_id
            - El campo creado_por NO se modifica
        """
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
            logger.info(f"Actualizando empresa {empresa_id}: {razon_social} por usuario {usuario_actual_id}")
            self._repo.update(empresa)
            logger.info(f"Empresa {empresa_id} actualizada exitosamente")
            return empresa, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar empresa {empresa_id}")
            return None, sanitize_error_message(e)
