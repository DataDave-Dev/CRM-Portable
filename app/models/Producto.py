# Modelo de Producto - representa un registro de la tabla Productos

from datetime import datetime


class Producto:
    def __init__(
        self,
        producto_id=None,
        codigo=None,
        nombre="",
        descripcion=None,
        categoria=None,
        precio_unitario=None,
        moneda_id=None,
        unidad_medida=None,
        activo=1,
        fecha_creacion=None,
        # campos JOIN para visualizacion
        nombre_moneda=None,
    ):
        self.producto_id = producto_id
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio_unitario = precio_unitario
        self.moneda_id = moneda_id
        self.unidad_medida = unidad_medida
        self.activo = activo
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.nombre_moneda = nombre_moneda

    def __repr__(self):
        return f"<Producto(id={self.producto_id}, codigo='{self.codigo}', nombre='{self.nombre}')>"
