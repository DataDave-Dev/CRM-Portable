# Logica de negocio para gestionar notas de empresa

from app.repositories.nota_empresa_repository import NotaEmpresaRepository
from app.models.NotaEmpresa import NotaEmpresa


class NotaEmpresaService:
    def __init__(self):
        self._repo = NotaEmpresaRepository()

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

        empresa_id = datos.get("empresa_id")
        if not empresa_id:
            return None, "El ID de la empresa es requerido"

        nueva_nota = NotaEmpresa(
            empresa_id=empresa_id,
            titulo=datos.get("titulo", "").strip() or None,
            contenido=contenido,
            es_privada=datos.get("es_privada", 0),
            creado_por=usuario_actual_id,
        )

        try:
            nota_id = self._repo.create(nueva_nota)
            nueva_nota.nota_id = nota_id
            return nueva_nota, None
        except Exception as e:
            return None, f"Error al crear nota: {str(e)}"

    def actualizar_nota(self, nota_id, datos):
        # validar campos requeridos
        contenido = datos.get("contenido", "").strip()
        if not contenido:
            return None, "El contenido de la nota es requerido"

        nota = NotaEmpresa(
            nota_id=nota_id,
            titulo=datos.get("titulo", "").strip() or None,
            contenido=contenido,
            es_privada=datos.get("es_privada", 0),
        )

        try:
            self._repo.update(nota)
            return nota, None
        except Exception as e:
            return None, f"Error al actualizar nota: {str(e)}"

    def eliminar_nota(self, nota_id):
        try:
            self._repo.delete(nota_id)
            return True, None
        except Exception as e:
            return False, f"Error al eliminar nota: {str(e)}"
