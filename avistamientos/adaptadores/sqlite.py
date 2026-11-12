"""Adaptador de salida: el SQL y el límite de SQLite permanecen aquí."""
import sqlite3
from pathlib import Path

from avistamientos.nucleo.puertos import RepositorioAvistamientos
from avistamientos.nucleo.validacion import CAMPOS

MAX_SQLITE_ID = 9223372036854775807


def conectar(ruta):
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar(ruta):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    conexion = conectar(ruta)
    try:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS avistamientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    especie TEXT NOT NULL,
                    lugar TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    observador TEXT NOT NULL
                )
            """)
    finally:
        conexion.close()


class RepositorioSQLite(RepositorioAvistamientos):
    def __init__(self, conexion):
        self.conexion = conexion

    def listar(self):
        filas = self.conexion.execute(
            "SELECT id, especie, lugar, fecha, observador FROM avistamientos ORDER BY id"
        ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener(self, identificador):
        if not 1 <= identificador <= MAX_SQLITE_ID:
            return None
        fila = self.conexion.execute(
            "SELECT id, especie, lugar, fecha, observador FROM avistamientos WHERE id = ?",
            (identificador,),
        ).fetchone()
        return dict(fila) if fila is not None else None

    def crear(self, datos):
        with self.conexion:
            cursor = self.conexion.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
                tuple(datos[campo] for campo in CAMPOS),
            )
        return self.obtener(cursor.lastrowid)

    def actualizar(self, identificador, datos):
        with self.conexion:
            cursor = self.conexion.execute(
                "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
                tuple(datos[campo] for campo in CAMPOS) + (identificador,),
            )
        if cursor.rowcount == 0:
            return None
        return self.obtener(identificador)

    def eliminar(self, identificador):
        if not 1 <= identificador <= MAX_SQLITE_ID:
            return False
        with self.conexion:
            cursor = self.conexion.execute(
                "DELETE FROM avistamientos WHERE id = ?", (identificador,)
            )
        return cursor.rowcount != 0

    def resumen(self):
        filas = self.conexion.execute("""
            SELECT especie, COUNT(*) AS cantidad
            FROM avistamientos
            GROUP BY especie
            ORDER BY especie
        """).fetchall()
        return [dict(fila) for fila in filas]
