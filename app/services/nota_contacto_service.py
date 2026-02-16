# Logica de negocio para gestionar notas de contacto

from app.repositories.nota_contacto_repository import NotaContactoRepository
from app.models.NotaContacto import NotaContacto


class NotaContactoService:
    def __init__(self):
        self._repo = NotaContactoRepository()

    def obtener_por_contacto(self, contacto_id):
        # obtiene todas las notas de un contacto especifico
        try:
            return self._repo.find_by_contacto(contacto_id), None
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

        contacto_id = datos.get("contacto_id")
        if not contacto_id:
            return None, "El ID del contacto es requerido"

        nueva_nota = NotaContacto(
            contacto_id=contacto_id,
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

        nota = NotaContacto(
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
