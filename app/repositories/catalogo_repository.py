# Repositorio generico para catalogos - CRUD parametrizado por configuracion

import re
import sqlite3
from app.database.connection import get_connection
from app.models.Catalogo import Catalogo


class CatalogoRepository:

    # whitelist de tablas permitidas para evitar SQL injection
    ALLOWED_TABLES = {
        'EtapasVenta', 'MotivosPerdida', 'TiposActividad', 'Prioridades',
        'EstadosActividad', 'Industrias', 'TamanosEmpresa', 'OrigenesContacto',
        'Monedas', 'Paises', 'Estados', 'Ciudades'
    }

    def __init__(self, config):
        self._config = config
        self._table = config['table']
        self._id_col = config['id_column']
        self._columns = [c['name'] for c in config['columns']]
        self._order_by = config.get('order_by', self._columns[0])
        self._fk_column = config.get('fk_column')  # columna de foreign key para catalogos jerarquicos

        # validar identificadores SQL al inicializar
        self._validate_identifiers()

    def _validate_identifiers(self):
        # validar que tabla esta en whitelist
        if self._table not in self.ALLOWED_TABLES:
            raise ValueError(f"Tabla no permitida: {self._table}")

        # validar formato de identificadores SQL (solo letras, numeros y guion bajo)
        sql_identifier_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

        if not sql_identifier_pattern.match(self._id_col):
            raise ValueError(f"Columna ID invalida: {self._id_col}")

        for col in self._columns:
            if not sql_identifier_pattern.match(col):
                raise ValueError(f"Columna invalida: {col}")

        # validar columna FK si existe (para catalogos jerarquicos como geografia)
        if self._fk_column and not sql_identifier_pattern.match(self._fk_column):
            raise ValueError(f"Columna FK invalida: {self._fk_column}")

    def find_all(self, filters=None):
        conn = get_connection()
        query = f"SELECT {self._id_col}, {', '.join(self._columns)} FROM {self._table}"
        params = []

        if filters:
            # validar que columnas en filters estan en columnas permitidas
            conditions = []
            for col, val in filters.items():
                # permitir: columnas configuradas, id_column o fk_column (para jerarquias)
                if col not in self._columns and col != self._id_col and col != self._fk_column:
                    raise ValueError(f"Columna '{col}' no permitida para filtrado")
                conditions.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY {self._order_by}"
        cursor = conn.execute(query, params)
        return [self._row_to_catalogo(row) for row in cursor.fetchall()]

    def find_by_id(self, id_value):
        conn = get_connection()
        query = f"SELECT {self._id_col}, {', '.join(self._columns)} FROM {self._table} WHERE {self._id_col} = ?"
        cursor = conn.execute(query, (id_value,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_catalogo(row)

    def create(self, data):
        conn = get_connection()
        cols = list(data.keys())
        placeholders = ", ".join(["?"] * len(cols))
        query = f"INSERT INTO {self._table} ({', '.join(cols)}) VALUES ({placeholders})"
        cursor = conn.execute(query, list(data.values()))
        conn.commit()
        return cursor.lastrowid

    def update(self, id_value, data):
        conn = get_connection()
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {self._table} SET {set_clause} WHERE {self._id_col} = ?"
        params = list(data.values()) + [id_value]
        conn.execute(query, params)
        conn.commit()

    def delete(self, id_value):
        conn = get_connection()
        try:
            conn.execute(f"DELETE FROM {self._table} WHERE {self._id_col} = ?", (id_value,))
            conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, "No se puede eliminar porque esta siendo utilizado por otros registros"

    def name_exists(self, column, value, exclude_id=None):
        conn = get_connection()
        if exclude_id:
            cursor = conn.execute(
                f"SELECT COUNT(*) as total FROM {self._table} WHERE {column} = ? AND {self._id_col} != ?",
                (value, exclude_id),
            )
        else:
            cursor = conn.execute(
                f"SELECT COUNT(*) as total FROM {self._table} WHERE {column} = ?",
                (value,),
            )
        return cursor.fetchone()["total"] > 0

    def count_references(self, id_value):
        conn = get_connection()
        total = 0
        for ref in self._config.get('referenced_by', []):
            cursor = conn.execute(
                f"SELECT COUNT(*) as total FROM {ref['table']} WHERE {ref['column']} = ?",
                (id_value,),
            )
            total += cursor.fetchone()["total"]
        return total

    def _row_to_catalogo(self, row):
        kwargs = {}
        for col in self._columns:
            try:
                kwargs[col] = row[col]
            except (KeyError, IndexError):
                kwargs[col] = None
        return Catalogo(id_value=row[self._id_col], **kwargs)
