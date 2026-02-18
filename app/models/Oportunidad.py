# Modelo de Oportunidad - representa un registro de la tabla Oportunidades

from datetime import datetime


class Oportunidad:
    def __init__(
        self,
        oportunidad_id=None,
        nombre="",
        empresa_id=None,
        contacto_id=None,
        etapa_id=None,
        monto_estimado=None,
        moneda_id=None,
        probabilidad_cierre=None,
        fecha_cierre_estimada=None,
        fecha_cierre_real=None,
        origen_id=None,
        propietario_id=None,
        motivos_perdida_id=None,
        notas_perdida=None,
        descripcion=None,
        es_ganada=None,  # None = abierta, 1 = ganada, 0 = perdida
        fecha_creacion=None,
        fecha_modificacion=None,
        creado_por=None,
        modificado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_empresa=None,
        nombre_contacto=None,
        nombre_etapa=None,
        nombre_moneda=None,
        nombre_propietario=None,
        nombre_origen=None,
        nombre_motivo_perdida=None,
    ):
        self.oportunidad_id = oportunidad_id
        self.nombre = nombre
        self.empresa_id = empresa_id
        self.contacto_id = contacto_id
        self.etapa_id = etapa_id
        self.monto_estimado = monto_estimado
        self.moneda_id = moneda_id
        self.probabilidad_cierre = probabilidad_cierre
        self.fecha_cierre_estimada = fecha_cierre_estimada
        self.fecha_cierre_real = fecha_cierre_real
        self.origen_id = origen_id
        self.propietario_id = propietario_id
        self.motivos_perdida_id = motivos_perdida_id
        self.notas_perdida = notas_perdida
        self.descripcion = descripcion
        self.es_ganada = es_ganada
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_modificacion = fecha_modificacion
        self.creado_por = creado_por
        self.modificado_por = modificado_por
        self.nombre_empresa = nombre_empresa
        self.nombre_contacto = nombre_contacto
        self.nombre_etapa = nombre_etapa
        self.nombre_moneda = nombre_moneda
        self.nombre_propietario = nombre_propietario
        self.nombre_origen = nombre_origen
        self.nombre_motivo_perdida = nombre_motivo_perdida

    def __repr__(self):
        return f"<Oportunidad(id={self.oportunidad_id}, nombre='{self.nombre}')>"
