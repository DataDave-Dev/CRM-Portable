# Repositorio de productos en oportunidades - queries contra OportunidadProductos

from app.database.connection import get_connection


class OportunidadProductoRepository:

    def find_by_oportunidad(self, oportunidad_id):
        # retorna lista de dicts con info de cada producto en la oportunidad
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT op.OportunidadProductoID, op.OportunidadID, op.ProductoID,
                   op.Cantidad, op.PrecioUnitario, op.Descuento, op.Notas,
                   p.Nombre AS NombreProducto, p.Codigo AS CodigoProducto,
                   p.UnidadMedida,
                   ROUND(op.Cantidad * op.PrecioUnitario * (1 - op.Descuento / 100.0), 2) AS Subtotal
            FROM OportunidadProductos op
            INNER JOIN Productos p ON op.ProductoID = p.ProductoID
            WHERE op.OportunidadID = ?
            ORDER BY op.OportunidadProductoID
            """,
            (oportunidad_id,),
        )
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def delete_by_oportunidad(self, oportunidad_id):
        conn = get_connection()
        conn.execute(
            "DELETE FROM OportunidadProductos WHERE OportunidadID = ?",
            (oportunidad_id,),
        )
        conn.commit()

    def create(self, oportunidad_id, producto_id, cantidad, precio_unitario, descuento, notas):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO OportunidadProductos
                (OportunidadID, ProductoID, Cantidad, PrecioUnitario, Descuento, Notas)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (oportunidad_id, producto_id, cantidad, precio_unitario, descuento, notas),
        )
        conn.commit()
        return cursor.lastrowid

    def create_many(self, oportunidad_id, items):
        # items: lista de dicts con keys producto_id, cantidad, precio_unitario, descuento, notas
        conn = get_connection()
        for item in items:
            conn.execute(
                """
                INSERT INTO OportunidadProductos
                    (OportunidadID, ProductoID, Cantidad, PrecioUnitario, Descuento, Notas)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    oportunidad_id,
                    item["producto_id"],
                    item["cantidad"],
                    item["precio_unitario"],
                    item.get("descuento", 0),
                    item.get("notas"),
                ),
            )
        conn.commit()

    @staticmethod
    def _row_to_dict(row):
        return {
            "oportunidad_producto_id": row["OportunidadProductoID"],
            "oportunidad_id": row["OportunidadID"],
            "producto_id": row["ProductoID"],
            "cantidad": row["Cantidad"],
            "precio_unitario": row["PrecioUnitario"],
            "descuento": row["Descuento"] or 0,
            "notas": row["Notas"],
            "nombre_producto": row["NombreProducto"],
            "codigo_producto": row["CodigoProducto"],
            "unidad_medida": row["UnidadMedida"],
            "subtotal": row["Subtotal"] or 0,
        }
