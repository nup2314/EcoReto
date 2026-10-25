import os
import psycopg
from psycopg.rows import dict_row


def conectar_db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta configurar DATABASE_URL")
    return psycopg.connect(url, row_factory=dict_row)


def consultar(sql, params=(), uno=False):
    """SELECT: devuelve una fila (uno=True) o una lista de filas."""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() if uno else cur.fetchall()
    finally:
        conexion.close()


def ejecutar(sql, params=()):
    """INSERT / UPDATE / DELETE con commit."""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cur:
            cur.execute(sql, params)
        conexion.commit()
    finally:
        conexion.close()
