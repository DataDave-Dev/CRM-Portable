# Modelo de Campana - representa un registro de la tabla Campanas

from datetime import datetime


class Campana:
    def __init__(
        self,
        campana_id=None,
        nombre="",
        descripcion=None,
        tipo=None,
        estado="Borrador",
        plantilla_id=None,
        segmento_id=None,
        fecha_programada=None,
        fecha_envio=None,
        fecha_finalizacion=None,
        total_destinatarios=0,
        total_enviados=0,
        total_entregados=0,
        total_abiertos=0,
        total_clics=0,
        total_rebotados=0,
        total_desuscripciones=0,
        presupuesto=None,
        moneda_id=None,
        propietario_id=None,
        fecha_creacion=None,
        fecha_modificacion=None,
        # campos JOIN
        nombre_plantilla=None,
        nombre_segmento=None,
        nombre_propietario=None,
    ):
        self.campana_id = campana_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.estado = estado
        self.plantilla_id = plantilla_id
        self.segmento_id = segmento_id
        self.fecha_programada = fecha_programada
        self.fecha_envio = fecha_envio
        self.fecha_finalizacion = fecha_finalizacion
        self.total_destinatarios = total_destinatarios or 0
        self.total_enviados = total_enviados or 0
        self.total_entregados = total_entregados or 0
        self.total_abiertos = total_abiertos or 0
        self.total_clics = total_clics or 0
        self.total_rebotados = total_rebotados or 0
        self.total_desuscripciones = total_desuscripciones or 0
        self.presupuesto = presupuesto
        self.moneda_id = moneda_id
        self.propietario_id = propietario_id
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.nombre_plantilla = nombre_plantilla
        self.nombre_segmento = nombre_segmento
        self.nombre_propietario = nombre_propietario

    @property
    def porcentaje_apertura(self):
        if self.total_enviados and self.total_enviados > 0:
            return round(self.total_abiertos / self.total_enviados * 100, 1)
        return 0.0

    @property
    def porcentaje_clics(self):
        if self.total_enviados and self.total_enviados > 0:
            return round(self.total_clics / self.total_enviados * 100, 1)
        return 0.0

    def __repr__(self):
        return f"<Campana(id={self.campana_id}, nombre='{self.nombre}', estado='{self.estado}')>"
