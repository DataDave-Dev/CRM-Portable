# Modelo de NotaEmpresa - representa un registro de la tabla NotasEmpresa

from datetime import datetime


class NotaEmpresa:
    def __init__(
        self,
        nota_id=None,
        empresa_id=None,
        titulo=None,
        contenido="",
        es_privada=0,
        fecha_creacion=None,
        creado_por=None,
        # campos JOIN para visualizacion (no se guardan en BD)
        nombre_empresa=None,
        nombre_creador=None,
    ):
        self.nota_id = nota_id
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.contenido = contenido
        self.es_privada = es_privada
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.creado_por = creado_por
        self.nombre_empresa = nombre_empresa
        self.nombre_creador = nombre_creador

    def __repr__(self):
        return f"<NotaEmpresa(id={self.nota_id}, empresa_id={self.empresa_id}, titulo='{self.titulo}')>"
