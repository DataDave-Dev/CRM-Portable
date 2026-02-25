# Modelo de PlantillaCorreo - representa un registro de la tabla PlantillasCorreo

from datetime import datetime


class Plantilla:
    def __init__(
        self,
        plantilla_id=None,
        nombre="",
        asunto="",
        contenido_html="",
        contenido_texto=None,
        categoria=None,
        activa=1,
        creado_por=None,
        fecha_creacion=None,
        fecha_modificacion=None,
        # campo JOIN para visualizacion
        nombre_creador=None,
    ):
        self.plantilla_id = plantilla_id
        self.nombre = nombre
        self.asunto = asunto
        self.contenido_html = contenido_html
        self.contenido_texto = contenido_texto
        self.categoria = categoria
        self.activa = activa
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.nombre_creador = nombre_creador

    def __repr__(self):
        return f"<Plantilla(id={self.plantilla_id}, nombre='{self.nombre}')>"
