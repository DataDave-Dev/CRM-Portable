"""
Servicio de gestion de notas de contacto para el sistema CRM.

Este modulo proporciona la logica de negocio para gestionar notas asociadas a contactos,
incluyendo validaciones de longitud, sanitizacion XSS, y auditoria CRUD completa.

Validaciones implementadas:
    - Campo requerido: contenido
    - Titulo: maximo 200 caracteres
    - Contenido: entre 1 y 5000 caracteres
    - Sanitizacion HTML para prevenir XSS
    - Foreign key: contacto_id debe existir

Auditoria:
    - Registra CREATE, UPDATE, DELETE en tabla LogAuditoria
    - Guarda valores anteriores y nuevos en formato JSON
    - Asocia operaciones al usuario que las realiza

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

from app.repositories.nota_contacto_repository import NotaContactoRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.NotaContacto import NotaContacto
from app.utils.sanitizer import Sanitizer
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class NotaContactoService:
    """
    Servicio de gestion de notas de contacto.

    Proporciona metodos CRUD para notas asociadas a contactos con sanitizacion
    automatica de contenido, validaciones de longitud, y auditoria completa.
    """

    def __init__(self):
        """Inicializa el servicio de notas de contacto."""
        self._repo = NotaContactoRepository()
        self._auditoria_repo = AuditoriaRepository()

    def obtener_por_contacto(self, contacto_id):
        """
        Obtiene todas las notas de un contacto especifico.

        Args:
            contacto_id (int): ID del contacto

        Returns:
            tuple: (list[NotaContacto]|None, str|None)
        """
        # obtiene todas las notas de un contacto especifico
        try:
            logger.debug(f"Obteniendo notas para contacto {contacto_id}")
            notas = self._repo.find_by_contacto(contacto_id)
            logger.info(f"Se encontraron {len(notas)} notas para contacto {contacto_id}")
            return notas, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener notas de contacto {contacto_id}")
            return None, sanitize_error_message(e)

    def obtener_por_id(self, nota_id):
        """Obtiene una nota especifica por su ID."""
        try:
            logger.debug(f"Obteniendo nota {nota_id}")
            nota = self._repo.find_by_id(nota_id)
            return nota, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener nota {nota_id}")
            return None, sanitize_error_message(e)

    def crear_nota(self, datos, usuario_actual_id):
        """
        Crea una nueva nota asociada a un contacto.

        Args:
            datos (dict): Datos de la nota:
                - contacto_id (int, requerido): ID del contacto
                - contenido (str, requerido): Contenido de 1-5000 caracteres
                - titulo (str, opcional): Titulo de hasta 200 caracteres
                - es_privada (int, opcional): 1=privada, 0=publica (default 0)
            usuario_actual_id (int): ID del usuario que crea la nota

        Returns:
            tuple: (NotaContacto|None, str|None)

        Note:
            - El contenido se sanitiza automaticamente contra XSS
            - La operacion se registra en auditoria
        """
        # validar campos requeridos
        contenido = datos.get("contenido", "").strip()
        if not contenido:
            return None, "El contenido de la nota es requerido"

        # validar longitud del contenido
        if not Sanitizer.validate_length(contenido, min_length=1, max_length=Sanitizer.MAX_CONTENIDO_LENGTH):
            return None, f"El contenido debe tener entre 1 y {Sanitizer.MAX_CONTENIDO_LENGTH} caracteres"

        contacto_id = datos.get("contacto_id")
        if not contacto_id:
            return None, "El ID del contacto es requerido"

        # sanitizar titulo
        titulo = datos.get("titulo", "").strip()
        if titulo:
            if not Sanitizer.validate_length(titulo, max_length=Sanitizer.MAX_TITULO_LENGTH):
                return None, f"El titulo no puede exceder {Sanitizer.MAX_TITULO_LENGTH} caracteres"
            titulo = Sanitizer.sanitize_string(titulo, max_length=Sanitizer.MAX_TITULO_LENGTH)
        else:
            titulo = None

        # sanitizar contenido
        contenido = Sanitizer.sanitize_string(contenido, max_length=Sanitizer.MAX_CONTENIDO_LENGTH)

        nueva_nota = NotaContacto(
            contacto_id=contacto_id,
            titulo=titulo,
            contenido=contenido,
            es_privada=datos.get("es_privada", 0),
            creado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Creando nota para contacto {contacto_id} por usuario {usuario_actual_id}")
            nota_id = self._repo.create(nueva_nota)
            nueva_nota.nota_id = nota_id

            # registrar en auditoria
            self._auditoria_repo.registrar_accion(
                usuario_id=usuario_actual_id,
                accion="CREATE",
                entidad_tipo="NotaContacto",
                entidad_id=nota_id,
                valores_nuevos={"contacto_id": contacto_id, "titulo": titulo, "contenido": contenido, "es_privada": nueva_nota.es_privada}
            )

            logger.info(f"Nota {nota_id} creada exitosamente")
            return nueva_nota, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear nota para contacto {contacto_id}")
            return None, sanitize_error_message(e)

    def actualizar_nota(self, nota_id, datos, usuario_actual_id=None):
        """
        Actualiza una nota existente.

        Args:
            nota_id (int): ID de la nota a actualizar
            datos (dict): Datos a actualizar (titulo, contenido, es_privada)
            usuario_actual_id (int, opcional): ID del usuario que actualiza

        Returns:
            tuple: (NotaContacto|None, str|None)

        Note:
            - Se registra en auditoria con valores anteriores y nuevos
            - El contenido se sanitiza contra XSS
        """
        # obtener nota anterior para auditoria
        nota_anterior, _ = self.obtener_por_id(nota_id)
        valores_anteriores = None
        if nota_anterior:
            valores_anteriores = {
                "titulo": nota_anterior.titulo,
                "contenido": nota_anterior.contenido,
                "es_privada": nota_anterior.es_privada
            }

        # validar campos requeridos
        contenido = datos.get("contenido", "").strip()
        if not contenido:
            return None, "El contenido de la nota es requerido"

        # validar longitud del contenido
        if not Sanitizer.validate_length(contenido, min_length=1, max_length=Sanitizer.MAX_CONTENIDO_LENGTH):
            return None, f"El contenido debe tener entre 1 y {Sanitizer.MAX_CONTENIDO_LENGTH} caracteres"

        # sanitizar titulo
        titulo = datos.get("titulo", "").strip()
        if titulo:
            if not Sanitizer.validate_length(titulo, max_length=Sanitizer.MAX_TITULO_LENGTH):
                return None, f"El titulo no puede exceder {Sanitizer.MAX_TITULO_LENGTH} caracteres"
            titulo = Sanitizer.sanitize_string(titulo, max_length=Sanitizer.MAX_TITULO_LENGTH)
        else:
            titulo = None

        # sanitizar contenido
        contenido = Sanitizer.sanitize_string(contenido, max_length=Sanitizer.MAX_CONTENIDO_LENGTH)

        nota = NotaContacto(
            nota_id=nota_id,
            titulo=titulo,
            contenido=contenido,
            es_privada=datos.get("es_privada", 0),
        )

        try:
            logger.info(f"Actualizando nota {nota_id}")
            self._repo.update(nota)

            # registrar en auditoria
            if usuario_actual_id:
                self._auditoria_repo.registrar_accion(
                    usuario_id=usuario_actual_id,
                    accion="UPDATE",
                    entidad_tipo="NotaContacto",
                    entidad_id=nota_id,
                    valores_anteriores=valores_anteriores,
                    valores_nuevos={"titulo": titulo, "contenido": contenido, "es_privada": nota.es_privada}
                )

            logger.info(f"Nota {nota_id} actualizada exitosamente")
            return nota, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al actualizar nota {nota_id}")
            return None, sanitize_error_message(e)

    def eliminar_nota(self, nota_id, usuario_actual_id=None):
        """
        Elimina una nota del sistema.

        Args:
            nota_id (int): ID de la nota a eliminar
            usuario_actual_id (int, opcional): ID del usuario que elimina

        Returns:
            tuple: (bool|None, str|None)

        Note:
            - Se registra en auditoria con valores anteriores antes de eliminar
        """
        # obtener nota anterior para auditoria
        nota_anterior, _ = self.obtener_por_id(nota_id)
        valores_anteriores = None
        if nota_anterior:
            valores_anteriores = {
                "contacto_id": nota_anterior.contacto_id,
                "titulo": nota_anterior.titulo,
                "contenido": nota_anterior.contenido,
                "es_privada": nota_anterior.es_privada
            }

        try:
            logger.info(f"Eliminando nota {nota_id}")
            self._repo.delete(nota_id)

            # registrar en auditoria
            if usuario_actual_id:
                self._auditoria_repo.registrar_accion(
                    usuario_id=usuario_actual_id,
                    accion="DELETE",
                    entidad_tipo="NotaContacto",
                    entidad_id=nota_id,
                    valores_anteriores=valores_anteriores
                )

            logger.info(f"Nota {nota_id} eliminada exitosamente")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar nota {nota_id}")
            return False, sanitize_error_message(e)
