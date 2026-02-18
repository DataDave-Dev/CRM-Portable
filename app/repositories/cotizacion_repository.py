# Repositorio de cotizaciones - queries contra la tabla Cotizaciones

from app.database.connection import get_connection
from app.models.Cotizacion import Cotizacion


class CotizacionRepository:

    def find_all(self, limit=None, offset=0):
        conn = get_connection()
        query = """
            SELECT c.*,
                   o.Nombre AS NombreOportunidad,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   m.Nombre AS NombreMoneda
            FROM Cotizaciones c
            LEFT JOIN Oportunidades o ON c.OportunidadID = o.OportunidadID
            LEFT JOIN Contactos ct ON c.ContactoID = ct.ContactoID
            LEFT JOIN Monedas m ON c.MonedaID = m.MonedaID
            ORDER BY c.FechaCreacion DESC
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        cursor = conn.execute(query)
        return [self._row_to_cotizacion(row) for row in cursor.fetchall()]

    def count_all(self):
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) as total FROM Cotizaciones")
        return cursor.fetchone()["total"]

    def find_by_id(self, cotizacion_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT c.*,
                   o.Nombre AS NombreOportunidad,
                   (ct.Nombre || ' ' || ct.ApellidoPaterno) AS NombreContacto,
                   m.Nombre AS NombreMoneda
            FROM Cotizaciones c
            LEFT JOIN Oportunidades o ON c.OportunidadID = o.OportunidadID
            LEFT JOIN Contactos ct ON c.ContactoID = ct.ContactoID
            LEFT JOIN Monedas m ON c.MonedaID = m.MonedaID
            WHERE c.CotizacionID = ?
            """,
            (cotizacion_id,),
        )
        row = cursor.fetchone()
        return self._row_to_cotizacion(row) if row else None

    def create(self, cotizacion):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Cotizaciones (
                NumeroCotizacion, OportunidadID, ContactoID, FechaEmision,
                FechaVigencia, Subtotal, IVA, Total, MonedaID,
                Estado, Notas, TerminosCondiciones, CreadoPor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cotizacion.numero_cotizacion,
                cotizacion.oportunidad_id,
                cotizacion.contacto_id,
                cotizacion.fecha_emision,
                cotizacion.fecha_vigencia,
                cotizacion.subtotal,
                cotizacion.iva,
                cotizacion.total,
                cotizacion.moneda_id,
                cotizacion.estado,
                cotizacion.notas,
                cotizacion.terminos_condiciones,
                cotizacion.creado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, cotizacion):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Cotizaciones SET
                NumeroCotizacion = ?, OportunidadID = ?, ContactoID = ?,
                FechaEmision = ?, FechaVigencia = ?, Subtotal = ?, IVA = ?,
                Total = ?, MonedaID = ?, Estado = ?, Notas = ?, TerminosCondiciones = ?
            WHERE CotizacionID = ?
            """,
            (
                cotizacion.numero_cotizacion,
                cotizacion.oportunidad_id,
                cotizacion.contacto_id,
                cotizacion.fecha_emision,
                cotizacion.fecha_vigencia,
                cotizacion.subtotal,
                cotizacion.iva,
                cotizacion.total,
                cotizacion.moneda_id,
                cotizacion.estado,
                cotizacion.notas,
                cotizacion.terminos_condiciones,
                cotizacion.cotizacion_id,
            ),
        )
        conn.commit()

    def numero_exists(self, numero, excluir_id=None):
        conn = get_connection()
        if excluir_id:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Cotizaciones WHERE NumeroCotizacion = ? AND CotizacionID != ?",
                (numero, excluir_id),
            )
        else:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Cotizaciones WHERE NumeroCotizacion = ?", (numero,)
            )
        return cursor.fetchone()["total"] > 0

    def get_ultimo_secuencial(self, year):
        # obtiene el ultimo numero secuencial del año para generar el siguiente
        conn = get_connection()
        prefix = f"COT-{year}-"
        cursor = conn.execute(
            "SELECT MAX(CAST(SUBSTR(NumeroCotizacion, ?) AS INTEGER)) as ultimo FROM Cotizaciones WHERE NumeroCotizacion LIKE ?",
            (len(prefix) + 1, f"{prefix}%"),
        )
        row = cursor.fetchone()
        return row["ultimo"] or 0

    @staticmethod
    def _row_to_cotizacion(row):
        nombre_oportunidad = None
        nombre_contacto = None
        nombre_moneda = None
        try:
            nombre_oportunidad = row["NombreOportunidad"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_contacto = row["NombreContacto"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_moneda = row["NombreMoneda"]
        except (KeyError, IndexError):
            pass
        return Cotizacion(
            cotizacion_id=row["CotizacionID"],
            numero_cotizacion=row["NumeroCotizacion"],
            oportunidad_id=row["OportunidadID"],
            contacto_id=row["ContactoID"],
            fecha_emision=row["FechaEmision"],
            fecha_vigencia=row["FechaVigencia"],
            subtotal=row["Subtotal"],
            iva=row["IVA"],
            total=row["Total"],
            moneda_id=row["MonedaID"],
            estado=row["Estado"],
            notas=row["Notas"],
            terminos_condiciones=row["TerminosCondiciones"],
            creado_por=row["CreadoPor"],
            fecha_creacion=row["FechaCreacion"],
            nombre_oportunidad=nombre_oportunidad,
            nombre_contacto=nombre_contacto,
            nombre_moneda=nombre_moneda,
        )
