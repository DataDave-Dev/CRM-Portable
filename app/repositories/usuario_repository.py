# Repositorio de usuarios - queries contra la tabla Usuarios

from app.database.connection import get_connection
from app.models.Usuario import Usuario


class UsuarioRepository:

    def find_by_email(self, email):
        # buscar usuario activo por email
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM Usuarios WHERE Email = ? AND Activo = 1",
            (email,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_usuario(row)

    def update_ultimo_acceso(self, usuario_id, timestamp):
        conn = get_connection()
        conn.execute(
            "UPDATE Usuarios SET UltimoAcceso = ? WHERE UsuarioID = ?",
            (timestamp, usuario_id),
        )
        conn.commit()

    @staticmethod
    def _row_to_usuario(row):
        # convertir el Row de sqlite a nuestro modelo Usuario
        return Usuario(
            usuario_id=row["UsuarioID"],
            nombre=row["Nombre"],
            apellido_paterno=row["ApellidoPaterno"],
            apellido_materno=row["ApellidoMaterno"],
            email=row["Email"],
            telefono=row["Telefono"],
            contrasena_hash=row["ContrasenaHash"],
            rol_id=row["RolID"],
            activo=row["Activo"],
            foto_perfil=row["FotoPerfil"],
            fecha_creacion=row["FechaCreacion"],
            ultimo_acceso=row["UltimoAcceso"],
        )
