# Modelo de Notificacion - representa un registro de la tabla Notificaciones


class Notificacion:
    def __init__(
        self,
        notificacion_id=None,
        usuario_id=None,
        tipo="",
        titulo="",
        mensaje=None,
        entidad_tipo=None,
        entidad_id=None,
        url=None,
        es_leida=0,
        fecha_creacion=None,
        fecha_lectura=None,
    ):
        self.notificacion_id = notificacion_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.titulo = titulo
        self.mensaje = mensaje
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.url = url
        self.es_leida = es_leida
        self.fecha_creacion = fecha_creacion
        self.fecha_lectura = fecha_lectura

    def __repr__(self):
        return f"<Notificacion(id={self.notificacion_id}, titulo='{self.titulo}')>"
