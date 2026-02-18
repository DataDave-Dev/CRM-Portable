# Modelo de Cotizacion - representa un registro de la tabla Cotizaciones

from datetime import datetime


class Cotizacion:
    def __init__(
        self,
        cotizacion_id=None,
        numero_cotizacion="",
        oportunidad_id=None,
        contacto_id=None,
        fecha_emision=None,
        fecha_vigencia=None,
        subtotal=None,
        iva=None,
        total=None,
        moneda_id=None,
        estado="Borrador",
        notas=None,
        terminos_condiciones=None,
        creado_por=None,
        fecha_creacion=None,
        # campos JOIN para visualizacion
        nombre_oportunidad=None,
        nombre_contacto=None,
        nombre_moneda=None,
    ):
        self.cotizacion_id = cotizacion_id
        self.numero_cotizacion = numero_cotizacion
        self.oportunidad_id = oportunidad_id
        self.contacto_id = contacto_id
        self.fecha_emision = fecha_emision or datetime.now().strftime("%Y-%m-%d")
        self.fecha_vigencia = fecha_vigencia
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.moneda_id = moneda_id
        self.estado = estado
        self.notas = notas
        self.terminos_condiciones = terminos_condiciones
        self.creado_por = creado_por
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.nombre_oportunidad = nombre_oportunidad
        self.nombre_contacto = nombre_contacto
        self.nombre_moneda = nombre_moneda

    def __repr__(self):
        return f"<Cotizacion(id={self.cotizacion_id}, numero='{self.numero_cotizacion}')>"
