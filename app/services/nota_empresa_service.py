"""
Servicio de gestion de notas de empresa para el sistema CRM.

Este modulo proporciona la logica de negocio para gestionar notas asociadas a empresas,
con las mismas caracteristicas de sanitizacion, validacion y auditoria que las notas
de contacto.

Validaciones implementadas:
    - Campo requerido: contenido
    - Titulo: maximo 200 caracteres
    - Contenido: entre 1 y 5000 caracteres
    - Sanitizacion HTML para prevenir XSS
    - Foreign key: empresa_id debe existir

Auditoria:
    - Registra CREATE, UPDATE, DELETE en tabla LogAuditoria
    - Guarda valores anteriores y nuevos en formato JSON
    - Asocia operaciones al usuario que las realiza

Attributes:
    logger: Logger configurado con filtrado automatico de datos sensibles.
"""

from app.repositories.nota_empresa_repository import NotaEmpresaRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.NotaEmpresa import NotaEmpresa
from app.utils.sanitizer import Sanitizer
from app.utils.logger import AppLogger
from app.utils.db_retry import sanitize_error_message

logger = AppLogger.get_logger(__name__)


class NotaEmpresaService:
    """
    Servicio de gestion de notas de empresa.

    Proporciona metodos CRUD para notas asociadas a empresas con sanitizacion
    automatica de contenido, validaciones de longitud, y auditoria completa.
    """

    def __init__(self):
        """Inicializa el servicio de notas de empresa."""
        self._repo = NotaEmpresaRepository()
        self._auditoria_repo = AuditoriaRepository()

    def obtener_por_empresa(self, empresa_id):
        """Obtiene todas las notas de una empresa especifica."""
        # obtiene todas las notas de una empresa especifica
        try:
            logger.debug(f"Obteniendo notas para empresa {empresa_id}")
            notas = self._repo.find_by_empresa(empresa_id)
            logger.info(f"Se encontraron {len(notas)} notas para empresa {empresa_id}")
            return notas, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al obtener notas de empresa {empresa_id}")
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
        Crea una nueva nota asociada a una empresa.

        Args:
            datos (dict): Datos de la nota (empresa_id, contenido, titulo, es_privada)
            usuario_actual_id (int): ID del usuario que crea la nota

        Returns:
            tuple: (NotaEmpresa|None, str|None)
        """
        # validar campos requeridos
        contenido = datos.get("contenido", "").strip()
        if not contenido:
            return None, "El contenido de la nota es requerido"

        # validar longitud del contenido
        if not Sanitizer.validate_length(contenido, min_length=1, max_length=Sanitizer.MAX_CONTENIDO_LENGTH):
            return None, f"El contenido debe tener entre 1 y {Sanitizer.MAX_CONTENIDO_LENGTH} caracteres"

        empresa_id = datos.get("empresa_id")
        if not empresa_id:
            return None, "El ID de la empresa es requerido"

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

        nueva_nota = NotaEmpresa(
            empresa_id=empresa_id,
            titulo=titulo,
            contenido=contenido,
            es_privada=datos.get("es_privada", 0),
            creado_por=usuario_actual_id,
        )

        try:
            logger.info(f"Creando nota para empresa {empresa_id} por usuario {usuario_actual_id}")
            nota_id = self._repo.create(nueva_nota)
            nueva_nota.nota_id = nota_id

            # registrar en auditoria
            self._auditoria_repo.registrar_accion(
                usuario_id=usuario_actual_id,
                accion="CREATE",
                entidad_tipo="NotaEmpresa",
                entidad_id=nota_id,
                valores_nuevos={"empresa_id": empresa_id, "titulo": titulo, "contenido": contenido, "es_privada": nueva_nota.es_privada}
            )

            logger.info(f"Nota {nota_id} creada exitosamente")
            return nueva_nota, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al crear nota para empresa {empresa_id}")
            return None, sanitize_error_message(e)

    def actualizar_nota(self, nota_id, datos, usuario_actual_id=None):
        """Actualiza una nota existente con sanitizacion y auditoria."""
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

        nota = NotaEmpresa(
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
                    entidad_tipo="NotaEmpresa",
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
        """Elimina una nota del sistema y registra en auditoria."""
        # obtener nota anterior para auditoria
        nota_anterior, _ = self.obtener_por_id(nota_id)
        valores_anteriores = None
        if nota_anterior:
            valores_anteriores = {
                "empresa_id": nota_anterior.empresa_id,
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
                    entidad_tipo="NotaEmpresa",
                    entidad_id=nota_id,
                    valores_anteriores=valores_anteriores
                )

            logger.info(f"Nota {nota_id} eliminada exitosamente")
            return True, None
        except Exception as e:
            AppLogger.log_exception(logger, f"Error al eliminar nota {nota_id}")
            return False, sanitize_error_message(e)
