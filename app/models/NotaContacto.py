# Modelo de NotaContacto - representa un registro de la tabla NotasContacto

from datetime import datetime


class NotaContacto:
    def __init__(
        self,
        nota_id=None,
        contacto_id=None,
        titulo=None,
        contenido="",
        es_privada=0,
        fecha_creacion=None,
        creado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_contacto=None,
        nombre_creador=None,
    ):
        self.nota_id = nota_id
        self.contacto_id = contacto_id
        self.titulo = titulo
        self.contenido = contenido
        self.es_privada = es_privada
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.creado_por = creado_por
        self.nombre_contacto = nombre_contacto
        self.nombre_creador = nombre_creador

    def __repr__(self):
        return f"<NotaContacto(id={self.nota_id}, contacto_id={self.contacto_id}, titulo='{self.titulo}')>"
