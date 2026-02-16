# Repositorio de empresas - queries contra la tabla Empresas

from app.database.connection import get_connection
from app.models.Empresa import Empresa


class EmpresaRepository:

    def find_all(self):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.*,
                   i.Nombre AS NombreIndustria,
                   t.Nombre AS NombreTamano,
                   c.Nombre AS NombreCiudad,
                   m.Nombre AS NombreMoneda,
                   oc.Nombre AS NombreOrigen,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Empresas e
            LEFT JOIN Industrias i ON e.IndustriaID = i.IndustriaID
            LEFT JOIN TamanosEmpresa t ON e.TamanoID = t.TamanoID
            LEFT JOIN Ciudades c ON e.CiudadID = c.CiudadID
            LEFT JOIN Monedas m ON e.MonedaID = m.MonedaID
            LEFT JOIN OrigenesContacto oc ON e.OrigenID = oc.OrigenID
            LEFT JOIN Usuarios u ON e.PropietarioID = u.UsuarioID
            ORDER BY e.FechaCreacion DESC
            """
        )
        rows = cursor.fetchall()
        return [self._row_to_empresa(row) for row in rows]

    def find_by_id(self, empresa_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT e.*,
                   i.Nombre AS NombreIndustria,
                   t.Nombre AS NombreTamano,
                   c.Nombre AS NombreCiudad,
                   m.Nombre AS NombreMoneda,
                   oc.Nombre AS NombreOrigen,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Empresas e
            LEFT JOIN Industrias i ON e.IndustriaID = i.IndustriaID
            LEFT JOIN TamanosEmpresa t ON e.TamanoID = t.TamanoID
            LEFT JOIN Ciudades c ON e.CiudadID = c.CiudadID
            LEFT JOIN Monedas m ON e.MonedaID = m.MonedaID
            LEFT JOIN OrigenesContacto oc ON e.OrigenID = oc.OrigenID
            LEFT JOIN Usuarios u ON e.PropietarioID = u.UsuarioID
            WHERE e.EmpresaID = ?
            """,
            (empresa_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_empresa(row)

    def create(self, empresa):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Empresas (
                RazonSocial, NombreComercial, RFC, IndustriaID, TamanoID,
                SitioWeb, Telefono, Email, Direccion, CiudadID,
                CodigoPostal, IngresoAnualEstimado, MonedaID, NumEmpleados,
                Descripcion, OrigenID, PropietarioID, Activo,
                CreadoPor, ModificadoPor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                empresa.razon_social,
                empresa.nombre_comercial,
                empresa.rfc,
                empresa.industria_id,
                empresa.tamano_id,
                empresa.sitio_web,
                empresa.telefono,
                empresa.email,
                empresa.direccion,
                empresa.ciudad_id,
                empresa.codigo_postal,
                empresa.ingreso_anual_estimado,
                empresa.moneda_id,
                empresa.num_empleados,
                empresa.descripcion,
                empresa.origen_id,
                empresa.propietario_id,
                empresa.activo,
                empresa.creado_por,
                empresa.modificado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, empresa):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Empresas SET
                RazonSocial = ?, NombreComercial = ?, RFC = ?,
                IndustriaID = ?, TamanoID = ?, SitioWeb = ?,
                Telefono = ?, Email = ?, Direccion = ?,
                CiudadID = ?, CodigoPostal = ?, IngresoAnualEstimado = ?,
                MonedaID = ?, NumEmpleados = ?, Descripcion = ?,
                OrigenID = ?, PropietarioID = ?, Activo = ?,
                ModificadoPor = ?
            WHERE EmpresaID = ?
            """,
            (
                empresa.razon_social,
                empresa.nombre_comercial,
                empresa.rfc,
                empresa.industria_id,
                empresa.tamano_id,
                empresa.sitio_web,
                empresa.telefono,
                empresa.email,
                empresa.direccion,
                empresa.ciudad_id,
                empresa.codigo_postal,
                empresa.ingreso_anual_estimado,
                empresa.moneda_id,
                empresa.num_empleados,
                empresa.descripcion,
                empresa.origen_id,
                empresa.propietario_id,
                empresa.activo,
                empresa.modificado_por,
                empresa.empresa_id,
            ),
        )
        conn.commit()

    def rfc_exists(self, rfc, excluir_id=None):
        conn = get_connection()
        if excluir_id:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Empresas WHERE RFC = ? AND EmpresaID != ?",
                (rfc, excluir_id),
            )
        else:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Empresas WHERE RFC = ?",
                (rfc,),
            )
        result = cursor.fetchone()
        return result["total"] > 0

    @staticmethod
    def _row_to_empresa(row):
        nombre_industria = None
        nombre_tamano = None
        nombre_ciudad = None
        nombre_moneda = None
        nombre_origen = None
        nombre_propietario = None
        try:
            nombre_industria = row["NombreIndustria"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_tamano = row["NombreTamano"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_ciudad = row["NombreCiudad"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_moneda = row["NombreMoneda"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_origen = row["NombreOrigen"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_propietario = row["NombrePropietario"]
        except (KeyError, IndexError):
            pass

        return Empresa(
            empresa_id=row["EmpresaID"],
            razon_social=row["RazonSocial"],
            nombre_comercial=row["NombreComercial"],
            rfc=row["RFC"],
            industria_id=row["IndustriaID"],
            tamano_id=row["TamanoID"],
            sitio_web=row["SitioWeb"],
            telefono=row["Telefono"],
            email=row["Email"],
            direccion=row["Direccion"],
            ciudad_id=row["CiudadID"],
            codigo_postal=row["CodigoPostal"],
            ingreso_anual_estimado=row["IngresoAnualEstimado"],
            moneda_id=row["MonedaID"],
            num_empleados=row["NumEmpleados"],
            descripcion=row["Descripcion"],
            logo_url=row["LogoURL"],
            origen_id=row["OrigenID"],
            propietario_id=row["PropietarioID"],
            activo=row["Activo"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            creado_por=row["CreadoPor"],
            modificado_por=row["ModificadoPor"],
            nombre_industria=nombre_industria,
            nombre_tamano=nombre_tamano,
            nombre_ciudad=nombre_ciudad,
            nombre_moneda=nombre_moneda,
            nombre_origen=nombre_origen,
            nombre_propietario=nombre_propietario,
        )
