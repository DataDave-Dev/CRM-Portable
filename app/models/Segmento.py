# Modelo de Segmento - representa un registro de la tabla Segmentos

from datetime import datetime


class Segmento:
    def __init__(
        self,
        segmento_id=None,
        nombre="",
        descripcion=None,
        tipo_entidad="Contactos",
        cantidad_registros=None,
        creado_por=None,
        fecha_creacion=None,
        fecha_modificacion=None,
        # campo JOIN para visualizacion
        nombre_creador=None,
    ):
        self.segmento_id = segmento_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_entidad = tipo_entidad
        self.cantidad_registros = cantidad_registros
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.nombre_creador = nombre_creador

    def __repr__(self):
        return f"<Segmento(id={self.segmento_id}, nombre='{self.nombre}')>"
