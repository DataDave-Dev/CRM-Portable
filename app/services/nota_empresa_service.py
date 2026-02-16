# Logica de negocio para gestionar notas de empresa

from app.repositories.nota_empresa_repository import NotaEmpresaRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.NotaEmpresa import NotaEmpresa
from app.utils.sanitizer import Sanitizer


class NotaEmpresaService:
    def __init__(self):
        self._repo = NotaEmpresaRepository()
        self._auditoria_repo = AuditoriaRepository()

    def obtener_por_empresa(self, empresa_id):
        # obtiene todas las notas de una empresa especifica
        try:
            return self._repo.find_by_empresa(empresa_id), None
        except Exception as e:
            return None, f"Error al obtener notas: {str(e)}"

    def obtener_por_id(self, nota_id):
        try:
            return self._repo.find_by_id(nota_id), None
        except Exception as e:
            return None, f"Error al obtener nota: {str(e)}"

    def crear_nota(self, datos, usuario_actual_id):
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

            return nueva_nota, None
        except Exception as e:
            return None, f"Error al crear nota: {str(e)}"

    def actualizar_nota(self, nota_id, datos, usuario_actual_id=None):
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

            return nota, None
        except Exception as e:
            return None, f"Error al actualizar nota: {str(e)}"

    def eliminar_nota(self, nota_id, usuario_actual_id=None):
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

            return True, None
        except Exception as e:
            return False, f"Error al eliminar nota: {str(e)}"
