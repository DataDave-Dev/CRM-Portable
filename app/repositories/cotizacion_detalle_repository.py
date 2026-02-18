# Repositorio de detalle de cotizaciones - queries contra CotizacionDetalle

from app.database.connection import get_connection


class CotizacionDetalleRepository:

    def find_by_cotizacion(self, cotizacion_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT cd.DetalleID, cd.CotizacionID, cd.ProductoID,
                   cd.Descripcion, cd.Cantidad, cd.PrecioUnitario, cd.Descuento,
                   p.Nombre AS NombreProducto, p.Codigo AS CodigoProducto,
                   p.UnidadMedida,
                   ROUND(cd.Cantidad * cd.PrecioUnitario * (1 - cd.Descuento / 100.0), 2) AS Subtotal
            FROM CotizacionDetalle cd
            INNER JOIN Productos p ON cd.ProductoID = p.ProductoID
            WHERE cd.CotizacionID = ?
            ORDER BY cd.DetalleID
            """,
            (cotizacion_id,),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def delete_by_cotizacion(self, cotizacion_id):
        conn = get_connection()
        conn.execute(
            "DELETE FROM CotizacionDetalle WHERE CotizacionID = ?", (cotizacion_id,)
        )
        conn.commit()

    def create_many(self, cotizacion_id, items):
        # items: lista de dicts con keys producto_id, descripcion, cantidad, precio_unitario, descuento
        conn = get_connection()
        for item in items:
            conn.execute(
                """
                INSERT INTO CotizacionDetalle
                    (CotizacionID, ProductoID, Descripcion, Cantidad, PrecioUnitario, Descuento)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cotizacion_id,
                    item["producto_id"],
                    item.get("descripcion"),
                    item["cantidad"],
                    item["precio_unitario"],
                    item.get("descuento", 0),
                ),
            )
        conn.commit()

    @staticmethod
    def _row_to_dict(row):
        return {
            "detalle_id": row["DetalleID"],
            "cotizacion_id": row["CotizacionID"],
            "producto_id": row["ProductoID"],
            "descripcion": row["Descripcion"],
            "cantidad": row["Cantidad"],
            "precio_unitario": row["PrecioUnitario"],
            "descuento": row["Descuento"] or 0,
            "nombre_producto": row["NombreProducto"],
            "codigo_producto": row["CodigoProducto"],
            "unidad_medida": row["UnidadMedida"],
            "subtotal": row["Subtotal"] or 0,
        }
