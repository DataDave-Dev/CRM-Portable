# Modelo de Recordatorio - representa un registro de la tabla Recordatorios


class Recordatorio:
    def __init__(
        self,
        recordatorio_id=None,
        usuario_id=None,
        titulo="",
        descripcion=None,
        fecha_recordatorio=None,
        contacto_id=None,
        empresa_id=None,
        oportunidad_id=None,
        actividad_id=None,
        tipo_recurrencia=None,
        es_leido=0,
        es_completado=0,
        fecha_creacion=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_contacto=None,
        nombre_empresa=None,
        nombre_oportunidad=None,
    ):
        self.recordatorio_id = recordatorio_id
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_recordatorio = fecha_recordatorio
        self.contacto_id = contacto_id
        self.empresa_id = empresa_id
        self.oportunidad_id = oportunidad_id
        self.actividad_id = actividad_id
        self.tipo_recurrencia = tipo_recurrencia
        self.es_leido = es_leido
        self.es_completado = es_completado
        self.fecha_creacion = fecha_creacion
        self.nombre_contacto = nombre_contacto
        self.nombre_empresa = nombre_empresa
        self.nombre_oportunidad = nombre_oportunidad

    def __repr__(self):
        return f"<Recordatorio(id={self.recordatorio_id}, titulo='{self.titulo}')>"
