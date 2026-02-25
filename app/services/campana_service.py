"""
Servicio de gestion de campanas de comunicacion y plantillas de correo.

Validaciones:
    - Plantilla: nombre y asunto requeridos, max 255 cada uno
    - Campana: nombre requerido, max 255 caracteres
    - ConfiguracionCorreo: nombre y email_remitente requeridos
"""

from app.repositories.plantilla_repository import PlantillaRepository
from app.repositories.campana_repository import CampanaRepository
from app.repositories.config_correo_repository import ConfigCorreoRepository
from app.models.Plantilla import Plantilla
from app.models.Campana import Campana
from app.models.ConfiguracionCorreo import ConfiguracionCorreo
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)

_ESTADOS_CAMPANA = ("Borrador", "Programada", "En Progreso", "Completada", "Cancelada")
_TIPOS_CAMPANA = ("Email", "Newsletter", "Promocional", "Transaccional", "Seguimiento")
_PROVEEDORES_CORREO = ("Gmail", "Outlook", "SMTP", "SendGrid", "Mailgun", "Yahoo", "Otro")


class CampanaService:

    def __init__(self):
        self._plantilla_repo = PlantillaRepository()
        self._campana_repo = CampanaRepository()
        self._config_repo = ConfigCorreoRepository()

    # ==========================================
    # PLANTILLAS
    # ==========================================

    def obtener_plantillas(self):
        try:
            plantillas = self._plantilla_repo.find_all()
            logger.debug(f"Se obtuvieron {len(plantillas)} plantillas")
            return plantillas, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener plantillas")
            return None, sanitize_error_message(e)

    def obtener_plantillas_activas(self):
        try:
            return self._plantilla_repo.find_all_activas(), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener plantillas activas")
            return None, sanitize_error_message(e)

    def obtener_plantilla(self, plantilla_id):
        try:
            return self._plantilla_repo.find_by_id(plantilla_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener plantilla {plantilla_id}")
            return None, sanitize_error_message(e)

    def crear_plantilla(self, datos, usuario_id):
        error = self._validar_plantilla(datos)
        if error:
            return None, error

        nueva = Plantilla(
            nombre=datos["nombre"].strip(),
            asunto=datos["asunto"].strip(),
            contenido_html=datos.get("contenido_html", "").strip(),
            contenido_texto=datos.get("contenido_texto", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
            activa=1 if datos.get("activa", True) else 0,
            creado_por=usuario_id,
        )
        try:
            logger.info(f"Creando plantilla: '{nueva.nombre}' por usuario {usuario_id}")
            nueva.plantilla_id = self._plantilla_repo.create(nueva)
            logger.info(f"Plantilla {nueva.plantilla_id} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear plantilla: {nueva.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_plantilla(self, plantilla_id, datos):
        error = self._validar_plantilla(datos)
        if error:
            return None, error

        plantilla = Plantilla(
            plantilla_id=plantilla_id,
            nombre=datos["nombre"].strip(),
            asunto=datos["asunto"].strip(),
            contenido_html=datos.get("contenido_html", "").strip(),
            contenido_texto=datos.get("contenido_texto", "").strip() or None,
            categoria=datos.get("categoria", "").strip() or None,
            activa=1 if datos.get("activa", True) else 0,
        )
        try:
            logger.info(f"Actualizando plantilla {plantilla_id}: '{plantilla.nombre}'")
            self._plantilla_repo.update(plantilla)
            return plantilla, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar plantilla {plantilla_id}")
            return None, sanitize_error_message(e)

    def eliminar_plantilla(self, plantilla_id):
        try:
            logger.info(f"Eliminando plantilla {plantilla_id}")
            self._plantilla_repo.delete(plantilla_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar plantilla {plantilla_id}")
            return False, sanitize_error_message(e)

    def _validar_plantilla(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre de la plantilla es requerido"
        if len(nombre) > 255:
            return "El nombre no puede exceder 255 caracteres"

        asunto = datos.get("asunto", "").strip()
        if not asunto:
            return "El asunto es requerido"
        if len(asunto) > 255:
            return "El asunto no puede exceder 255 caracteres"

        return None

    # ==========================================
    # CAMPANAS
    # ==========================================

    def obtener_campanas(self):
        try:
            campanas = self._campana_repo.find_all()
            logger.debug(f"Se obtuvieron {len(campanas)} campanas")
            return campanas, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener campanas")
            return None, sanitize_error_message(e)

    def obtener_campana(self, campana_id):
        try:
            return self._campana_repo.find_by_id(campana_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener campana {campana_id}")
            return None, sanitize_error_message(e)

    def crear_campana(self, datos, usuario_id):
        error = self._validar_campana(datos)
        if error:
            return None, error

        nueva = Campana(
            nombre=datos["nombre"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            tipo=datos.get("tipo") or None,
            estado="Borrador",
            plantilla_id=datos.get("plantilla_id") or None,
            segmento_id=datos.get("segmento_id") or None,
            fecha_programada=datos.get("fecha_programada") or None,
            presupuesto=datos.get("presupuesto") or None,
            moneda_id=datos.get("moneda_id") or None,
            propietario_id=usuario_id,
        )
        try:
            logger.info(f"Creando campana: '{nueva.nombre}' por usuario {usuario_id}")
            nueva.campana_id = self._campana_repo.create(nueva)
            logger.info(f"Campana {nueva.campana_id} creada exitosamente")
            return nueva, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear campana: {nueva.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_campana(self, campana_id, datos):
        error = self._validar_campana(datos)
        if error:
            return None, error

        campana = Campana(
            campana_id=campana_id,
            nombre=datos["nombre"].strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            tipo=datos.get("tipo") or None,
            estado=datos.get("estado", "Borrador"),
            plantilla_id=datos.get("plantilla_id") or None,
            segmento_id=datos.get("segmento_id") or None,
            fecha_programada=datos.get("fecha_programada") or None,
            presupuesto=datos.get("presupuesto") or None,
            moneda_id=datos.get("moneda_id") or None,
        )
        try:
            logger.info(f"Actualizando campana {campana_id}: '{campana.nombre}'")
            self._campana_repo.update(campana)
            return campana, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar campana {campana_id}")
            return None, sanitize_error_message(e)

    def cambiar_estado(self, campana_id, estado):
        if estado not in _ESTADOS_CAMPANA:
            return False, f"Estado invalido. Debe ser uno de: {', '.join(_ESTADOS_CAMPANA)}"
        try:
            self._campana_repo.update_estado(campana_id, estado)
            logger.info(f"Campana {campana_id} cambiada a estado '{estado}'")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al cambiar estado de campana {campana_id}")
            return False, sanitize_error_message(e)

    def eliminar_campana(self, campana_id):
        try:
            logger.info(f"Eliminando campana {campana_id}")
            self._campana_repo.delete(campana_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar campana {campana_id}")
            return False, sanitize_error_message(e)

    def get_destinatarios(self, campana_id):
        try:
            return self._campana_repo.get_destinatarios(campana_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener destinatarios de campana {campana_id}")
            return None, sanitize_error_message(e)

    def agregar_destinatario(self, campana_id, contacto_id, email_destino):
        if not email_destino or "@" not in email_destino:
            return False, "El email del destinatario no es valido"
        try:
            self._campana_repo.agregar_destinatario(campana_id, contacto_id, email_destino)
            self._actualizar_total_destinatarios(campana_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al agregar destinatario a campana {campana_id}")
            return False, sanitize_error_message(e)

    def cargar_desde_segmento(self, campana_id, segmento_id):
        try:
            n = self._campana_repo.cargar_destinatarios_desde_segmento(campana_id, segmento_id)
            self._actualizar_total_destinatarios(campana_id)
            logger.info(f"Cargados {n} destinatarios del segmento {segmento_id} a campana {campana_id}")
            return n, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al cargar destinatarios desde segmento")
            return 0, sanitize_error_message(e)

    def eliminar_destinatario(self, destinatario_id, campana_id):
        try:
            self._campana_repo.eliminar_destinatario(destinatario_id)
            self._actualizar_total_destinatarios(campana_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar destinatario {destinatario_id}")
            return False, sanitize_error_message(e)

    def _actualizar_total_destinatarios(self, campana_id):
        destinatarios, _ = self.get_destinatarios(campana_id)
        if destinatarios is not None:
            self._campana_repo.update_metricas(campana_id, total_destinatarios=len(destinatarios))

    def _validar_campana(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre de la campana es requerido"
        if len(nombre) > 255:
            return "El nombre no puede exceder 255 caracteres"
        return None

    # ==========================================
    # CONFIGURACION DE CORREO
    # ==========================================

    def obtener_configs_correo(self):
        try:
            configs = self._config_repo.find_all()
            logger.debug(f"Se obtuvieron {len(configs)} configuraciones de correo")
            return configs, None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener configuraciones de correo")
            return None, sanitize_error_message(e)

    def obtener_config_correo(self, config_id):
        try:
            return self._config_repo.find_by_id(config_id), None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener config correo {config_id}")
            return None, sanitize_error_message(e)

    def obtener_config_activa(self):
        try:
            return self._config_repo.find_activa(), None
        except Exception as e:
            AppLogger.log_exception(logger, "Error al obtener config de correo activa")
            return None, sanitize_error_message(e)

    def crear_config_correo(self, datos):
        error = self._validar_config_correo(datos)
        if error:
            return None, error

        config = ConfiguracionCorreo(
            nombre=datos["nombre"].strip(),
            proveedor=datos.get("proveedor", "SMTP"),
            host=datos.get("host", "").strip() or None,
            puerto=int(datos.get("puerto", 587) or 587),
            usar_tls=1 if datos.get("usar_tls", True) else 0,
            usar_ssl=1 if datos.get("usar_ssl", False) else 0,
            email_remitente=datos["email_remitente"].strip(),
            nombre_remitente=datos.get("nombre_remitente", "").strip() or None,
            usuario=datos.get("usuario", "").strip() or None,
            contrasena=datos.get("contrasena", "").strip() or None,
            api_key=datos.get("api_key", "").strip() or None,
            activa=1 if datos.get("activa", False) else 0,
            notas=datos.get("notas", "").strip() or None,
        )
        try:
            logger.info(f"Creando config correo: '{config.nombre}'")
            config.config_id = self._config_repo.create(config)
            if config.activa:
                self._config_repo.activar(config.config_id)
            logger.info(f"Config correo {config.config_id} creada exitosamente")
            return config, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear config correo: {config.nombre}")
            return None, sanitize_error_message(e)

    def actualizar_config_correo(self, config_id, datos):
        error = self._validar_config_correo(datos)
        if error:
            return None, error

        config = ConfiguracionCorreo(
            config_id=config_id,
            nombre=datos["nombre"].strip(),
            proveedor=datos.get("proveedor", "SMTP"),
            host=datos.get("host", "").strip() or None,
            puerto=int(datos.get("puerto", 587) or 587),
            usar_tls=1 if datos.get("usar_tls", True) else 0,
            usar_ssl=1 if datos.get("usar_ssl", False) else 0,
            email_remitente=datos["email_remitente"].strip(),
            nombre_remitente=datos.get("nombre_remitente", "").strip() or None,
            usuario=datos.get("usuario", "").strip() or None,
            contrasena=datos.get("contrasena", "").strip() or None,
            api_key=datos.get("api_key", "").strip() or None,
            activa=1 if datos.get("activa", False) else 0,
            notas=datos.get("notas", "").strip() or None,
        )
        try:
            logger.info(f"Actualizando config correo {config_id}: '{config.nombre}'")
            self._config_repo.update(config)
            if config.activa:
                self._config_repo.activar(config_id)
            return config, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar config correo {config_id}")
            return None, sanitize_error_message(e)

    def activar_config_correo(self, config_id):
        try:
            self._config_repo.activar(config_id)
            logger.info(f"Config correo {config_id} activada")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al activar config correo {config_id}")
            return False, sanitize_error_message(e)

    def eliminar_config_correo(self, config_id):
        try:
            logger.info(f"Eliminando config correo {config_id}")
            self._config_repo.delete(config_id)
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar config correo {config_id}")
            return False, sanitize_error_message(e)

    def _validar_config_correo(self, datos):
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return "El nombre de la configuracion es requerido"
        if len(nombre) > 255:
            return "El nombre no puede exceder 255 caracteres"

        email = datos.get("email_remitente", "").strip()
        if not email:
            return "El email remitente es requerido"
        if "@" not in email or "." not in email.split("@")[-1]:
            return "El email remitente no tiene un formato valido"

        puerto = datos.get("puerto")
        if puerto is not None:
            try:
                p = int(puerto)
                if p < 1 or p > 65535:
                    return "El puerto debe estar entre 1 y 65535"
            except (ValueError, TypeError):
                return "El puerto debe ser un numero valido"

        return None

    @property
    def tipos_campana(self):
        return _TIPOS_CAMPANA

    @property
    def estados_campana(self):
        return _ESTADOS_CAMPANA

    @property
    def proveedores_correo(self):
        return _PROVEEDORES_CORREO
