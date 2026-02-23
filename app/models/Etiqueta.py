# Modelo de Etiqueta - representa un registro de la tabla Etiquetas

from datetime import datetime


class Etiqueta:
    def __init__(
        self,
        etiqueta_id=None,
        nombre="",
        color=None,
        categoria=None,
        fecha_creacion=None,
        # campos calculados (COUNT de asignaciones)
        num_contactos=0,
        num_empresas=0,
    ):
        self.etiqueta_id = etiqueta_id
        self.nombre = nombre
        self.color = color
        self.categoria = categoria
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.num_contactos = num_contactos or 0
        self.num_empresas = num_empresas or 0

    def __repr__(self):
        return f"<Etiqueta(id={self.etiqueta_id}, nombre='{self.nombre}')>"
