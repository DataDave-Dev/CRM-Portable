# Repositorio de productos - queries contra la tabla Productos

from app.database.connection import get_connection
from app.models.Producto import Producto


class ProductoRepository:

    def find_all(self, limit=None, offset=0):
        conn = get_connection()
        query = """
            SELECT p.*, m.Nombre AS NombreMoneda
            FROM Productos p
            LEFT JOIN Monedas m ON p.MonedaID = m.MonedaID
            ORDER BY p.Nombre
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        cursor = conn.execute(query)
        return [self._row_to_producto(row) for row in cursor.fetchall()]

    def count_all(self):
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) as total FROM Productos")
        return cursor.fetchone()["total"]

    def find_by_id(self, producto_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT p.*, m.Nombre AS NombreMoneda
            FROM Productos p
            LEFT JOIN Monedas m ON p.MonedaID = m.MonedaID
            WHERE p.ProductoID = ?
            """,
            (producto_id,),
        )
        row = cursor.fetchone()
        return self._row_to_producto(row) if row else None

    def find_activos(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT p.*, m.Nombre AS NombreMoneda
            FROM Productos p
            LEFT JOIN Monedas m ON p.MonedaID = m.MonedaID
            WHERE p.Activo = 1
            ORDER BY p.Nombre
            """
        )
        return [self._row_to_producto(row) for row in cursor.fetchall()]

    def create(self, producto):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Productos (Codigo, Nombre, Descripcion, Categoria,
                PrecioUnitario, MonedaID, UnidadMedida, Activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                producto.codigo,
                producto.nombre,
                producto.descripcion,
                producto.categoria,
                producto.precio_unitario,
                producto.moneda_id,
                producto.unidad_medida,
                producto.activo,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, producto):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Productos SET
                Codigo = ?, Nombre = ?, Descripcion = ?, Categoria = ?,
                PrecioUnitario = ?, MonedaID = ?, UnidadMedida = ?, Activo = ?
            WHERE ProductoID = ?
            """,
            (
                producto.codigo,
                producto.nombre,
                producto.descripcion,
                producto.categoria,
                producto.precio_unitario,
                producto.moneda_id,
                producto.unidad_medida,
                producto.activo,
                producto.producto_id,
            ),
        )
        conn.commit()

    def codigo_exists(self, codigo, excluir_id=None):
        conn = get_connection()
        if excluir_id:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Productos WHERE Codigo = ? AND ProductoID != ?",
                (codigo, excluir_id),
            )
        else:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Productos WHERE Codigo = ?", (codigo,)
            )
        return cursor.fetchone()["total"] > 0

    @staticmethod
    def _row_to_producto(row):
        nombre_moneda = None
        try:
            nombre_moneda = row["NombreMoneda"]
        except (KeyError, IndexError):
            pass
        return Producto(
            producto_id=row["ProductoID"],
            codigo=row["Codigo"],
            nombre=row["Nombre"],
            descripcion=row["Descripcion"],
            categoria=row["Categoria"],
            precio_unitario=row["PrecioUnitario"],
            moneda_id=row["MonedaID"],
            unidad_medida=row["UnidadMedida"],
            activo=row["Activo"],
            fecha_creacion=row["FechaCreacion"],
            nombre_moneda=nombre_moneda,
        )
