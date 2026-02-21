# Modelo de Actividad - representa un registro de la tabla Actividades

from datetime import datetime


class Actividad:
    def __init__(
        self,
        actividad_id=None,
        tipo_actividad_id=None,
        asunto="",
        descripcion=None,
        contacto_id=None,
        empresa_id=None,
        oportunidad_id=None,
        propietario_id=None,
        prioridad_id=None,
        estado_actividad_id=None,
        fecha_inicio=None,
        fecha_fin=None,
        fecha_vencimiento=None,
        duracion_minutos=None,
        ubicacion=None,
        resultado=None,
        fecha_creacion=None,
        fecha_modificacion=None,
        creado_por=None,
        modificado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_tipo_actividad=None,
        nombre_contacto=None,
        nombre_empresa=None,
        nombre_oportunidad=None,
        nombre_propietario=None,
        nombre_prioridad=None,
        nombre_estado_actividad=None,
    ):
        self.actividad_id = actividad_id
        self.tipo_actividad_id = tipo_actividad_id
        self.asunto = asunto
        self.descripcion = descripcion
        self.contacto_id = contacto_id
        self.empresa_id = empresa_id
        self.oportunidad_id = oportunidad_id
        self.propietario_id = propietario_id
        self.prioridad_id = prioridad_id
        self.estado_actividad_id = estado_actividad_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.fecha_vencimiento = fecha_vencimiento
        self.duracion_minutos = duracion_minutos
        self.ubicacion = ubicacion
        self.resultado = resultado
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.creado_por = creado_por
        self.modificado_por = modificado_por
        self.nombre_tipo_actividad = nombre_tipo_actividad
        self.nombre_contacto = nombre_contacto
        self.nombre_empresa = nombre_empresa
        self.nombre_oportunidad = nombre_oportunidad
        self.nombre_propietario = nombre_propietario
        self.nombre_prioridad = nombre_prioridad
        self.nombre_estado_actividad = nombre_estado_actividad

    def __repr__(self):
        return f"<Actividad(id={self.actividad_id}, asunto='{self.asunto}')>"
