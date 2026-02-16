# Repositorio de contactos - queries contra la tabla Contactos

from app.database.connection import get_connection
from app.models.Contacto import Contacto


class ContactoRepository:

    def find_all(self, limit=None, offset=0):
        # obtiene contactos con paginacion opcional
        conn = get_connection()
        query = """
            SELECT ct.*,
                   e.RazonSocial AS NombreEmpresa,
                   c.Nombre AS NombreCiudad,
                   oc.Nombre AS NombreOrigen,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Contactos ct
            LEFT JOIN Empresas e ON ct.EmpresaID = e.EmpresaID
            LEFT JOIN Ciudades c ON ct.CiudadID = c.CiudadID
            LEFT JOIN OrigenesContacto oc ON ct.OrigenID = oc.OrigenID
            LEFT JOIN Usuarios u ON ct.PropietarioID = u.UsuarioID
            ORDER BY ct.FechaCreacion DESC
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor = conn.execute(query)
        rows = cursor.fetchall()
        return [self._row_to_contacto(row) for row in rows]

    def count_all(self):
        # cuenta total de contactos para calcular paginas
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) as total FROM Contactos")
        return cursor.fetchone()["total"]

    def find_by_id(self, contacto_id):
        conn = get_connection()
        cursor = conn.execute(
            """
            SELECT ct.*,
                   e.RazonSocial AS NombreEmpresa,
                   c.Nombre AS NombreCiudad,
                   oc.Nombre AS NombreOrigen,
                   (u.Nombre || ' ' || u.ApellidoPaterno) AS NombrePropietario
            FROM Contactos ct
            LEFT JOIN Empresas e ON ct.EmpresaID = e.EmpresaID
            LEFT JOIN Ciudades c ON ct.CiudadID = c.CiudadID
            LEFT JOIN OrigenesContacto oc ON ct.OrigenID = oc.OrigenID
            LEFT JOIN Usuarios u ON ct.PropietarioID = u.UsuarioID
            WHERE ct.ContactoID = ?
            """,
            (contacto_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_contacto(row)

    def create(self, contacto):
        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO Contactos (
                Nombre, ApellidoPaterno, ApellidoMaterno, Email,
                EmailSecundario, TelefonoOficina, TelefonoCelular,
                Puesto, Departamento, EmpresaID, Direccion,
                CiudadID, CodigoPostal, FechaNacimiento, LinkedInURL,
                OrigenID, PropietarioID, EsContactoPrincipal,
                NoContactar, Activo, CreadoPor, ModificadoPor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contacto.nombre,
                contacto.apellido_paterno,
                contacto.apellido_materno,
                contacto.email,
                contacto.email_secundario,
                contacto.telefono_oficina,
                contacto.telefono_celular,
                contacto.puesto,
                contacto.departamento,
                contacto.empresa_id,
                contacto.direccion,
                contacto.ciudad_id,
                contacto.codigo_postal,
                contacto.fecha_nacimiento,
                contacto.linkedin_url,
                contacto.origen_id,
                contacto.propietario_id,
                contacto.es_contacto_principal,
                contacto.no_contactar,
                contacto.activo,
                contacto.creado_por,
                contacto.modificado_por,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, contacto):
        conn = get_connection()
        conn.execute(
            """
            UPDATE Contactos SET
                Nombre = ?, ApellidoPaterno = ?, ApellidoMaterno = ?,
                Email = ?, EmailSecundario = ?, TelefonoOficina = ?,
                TelefonoCelular = ?, Puesto = ?, Departamento = ?,
                EmpresaID = ?, Direccion = ?, CiudadID = ?,
                CodigoPostal = ?, FechaNacimiento = ?, LinkedInURL = ?,
                OrigenID = ?, PropietarioID = ?, EsContactoPrincipal = ?,
                NoContactar = ?, Activo = ?, ModificadoPor = ?
            WHERE ContactoID = ?
            """,
            (
                contacto.nombre,
                contacto.apellido_paterno,
                contacto.apellido_materno,
                contacto.email,
                contacto.email_secundario,
                contacto.telefono_oficina,
                contacto.telefono_celular,
                contacto.puesto,
                contacto.departamento,
                contacto.empresa_id,
                contacto.direccion,
                contacto.ciudad_id,
                contacto.codigo_postal,
                contacto.fecha_nacimiento,
                contacto.linkedin_url,
                contacto.origen_id,
                contacto.propietario_id,
                contacto.es_contacto_principal,
                contacto.no_contactar,
                contacto.activo,
                contacto.modificado_por,
                contacto.contacto_id,
            ),
        )
        conn.commit()

    def email_exists(self, email, excluir_id=None):
        conn = get_connection()
        if excluir_id:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Contactos WHERE Email = ? AND ContactoID != ?",
                (email, excluir_id),
            )
        else:
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM Contactos WHERE Email = ?",
                (email,),
            )
        result = cursor.fetchone()
        return result["total"] > 0

    @staticmethod
    def _row_to_contacto(row):
        nombre_empresa = None
        nombre_ciudad = None
        nombre_origen = None
        nombre_propietario = None
        try:
            nombre_empresa = row["NombreEmpresa"]
        except (KeyError, IndexError):
            pass
        try:
            nombre_ciudad = row["NombreCiudad"]
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

        return Contacto(
            contacto_id=row["ContactoID"],
            nombre=row["Nombre"],
            apellido_paterno=row["ApellidoPaterno"],
            apellido_materno=row["ApellidoMaterno"],
            email=row["Email"],
            email_secundario=row["EmailSecundario"],
            telefono_oficina=row["TelefonoOficina"],
            telefono_celular=row["TelefonoCelular"],
            puesto=row["Puesto"],
            departamento=row["Departamento"],
            empresa_id=row["EmpresaID"],
            direccion=row["Direccion"],
            ciudad_id=row["CiudadID"],
            codigo_postal=row["CodigoPostal"],
            fecha_nacimiento=row["FechaNacimiento"],
            linkedin_url=row["LinkedInURL"],
            origen_id=row["OrigenID"],
            propietario_id=row["PropietarioID"],
            es_contacto_principal=row["EsContactoPrincipal"],
            no_contactar=row["NoContactar"],
            activo=row["Activo"],
            foto_url=row["FotoURL"],
            fecha_creacion=row["FechaCreacion"],
            fecha_modificacion=row["FechaModificacion"],
            creado_por=row["CreadoPor"],
            modificado_por=row["ModificadoPor"],
            nombre_empresa=nombre_empresa,
            nombre_ciudad=nombre_ciudad,
            nombre_origen=nombre_origen,
            nombre_propietario=nombre_propietario,
        )
