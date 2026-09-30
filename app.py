"""API REST de avistamientos de aves: Flask + SQLite."""

import argparse
import re
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, g, jsonify, request, url_for
from werkzeug.exceptions import BadRequest, HTTPException


CAMPOS = ("especie", "lugar", "fecha", "observador")
MAX_SQLITE_ID = 9223372036854775807


def get_db():
    """Abre una conexión por petición y permite leer filas por columna."""
    if "db" not in g:
        from flask import current_app

        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def validar_avistamiento():
    """POST y PUT necesitan un objeto JSON con los cuatro campos de texto."""
    if not request.is_json:
        raise BadRequest("Envía el cuerpo con Content-Type: application/json.")

    datos = request.get_json()
    if not isinstance(datos, dict):
        raise BadRequest("El cuerpo debe ser un objeto JSON.")

    faltantes = [campo for campo in CAMPOS if campo not in datos]
    if faltantes:
        raise BadRequest("Faltan campos obligatorios: " + ", ".join(faltantes) + ".")

    adicionales = sorted(set(datos) - set(CAMPOS))
    if adicionales:
        raise BadRequest(
            "Campos no permitidos: " + ", ".join(adicionales)
            + ". El id lo asigna el sistema."
        )

    limpios = {}
    for campo in CAMPOS:
        valor = datos[campo]
        if not isinstance(valor, str) or not valor.strip():
            raise BadRequest(f"El campo '{campo}' debe ser texto no vacío.")
        limpios[campo] = valor.strip()

    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", limpios["fecha"]):
        raise BadRequest("La fecha debe tener el formato AAAA-MM-DD.")
    try:
        date.fromisoformat(limpios["fecha"])
    except ValueError as error:
        raise BadRequest("La fecha indicada no existe en el calendario.") from error

    return limpios


def buscar_avistamiento(avistamiento_id):
    # SQLite almacena sus identificadores como enteros de 64 bits.
    if not 1 <= avistamiento_id <= MAX_SQLITE_ID:
        return None
    return get_db().execute(
        "SELECT id, especie, lugar, fecha, observador FROM avistamientos WHERE id = ?",
        (avistamiento_id,),
    ).fetchone()


def create_app(test_config=None):
    """Crea la aplicación; las pruebas pueden usar otra base de datos."""
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(Path(__file__).resolve().parent / "data" / "avistamientos.db"),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    @app.teardown_appcontext
    def cerrar_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # IF NOT EXISTS conserva los datos cuando se reinicia el servidor.
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS avistamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                lugar TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observador TEXT NOT NULL
            )
        """)
        db.commit()

    @app.errorhandler(HTTPException)
    def error_http(error):
        # Conserva el código y cabeceras HTTP, pero devuelve el error en JSON.
        respuesta = error.get_response()
        respuesta.data = app.json.dumps({"error": error.description})
        respuesta.content_type = "application/json"
        return respuesta

    @app.errorhandler(500)
    def error_interno(_error):
        return jsonify(error="Error interno del servidor."), 500

    @app.get("/avistamientos")
    def listar_avistamientos():
        filas = get_db().execute(
            "SELECT id, especie, lugar, fecha, observador FROM avistamientos ORDER BY id"
        ).fetchall()
        return jsonify([dict(fila) for fila in filas]), 200

    @app.get("/avistamientos/resumen")
    def resumen_avistamientos():
        filas = get_db().execute("""
            SELECT especie, COUNT(*) AS cantidad
            FROM avistamientos
            GROUP BY especie
            ORDER BY especie
        """).fetchall()
        return jsonify([dict(fila) for fila in filas]), 200

    @app.get("/avistamientos/<int:avistamiento_id>")
    def obtener_avistamiento(avistamiento_id):
        fila = buscar_avistamiento(avistamiento_id)
        if fila is None:
            return jsonify(error="Avistamiento no encontrado."), 404
        return jsonify(dict(fila)), 200

    @app.post("/avistamientos")
    def crear_avistamiento():
        datos = validar_avistamiento()
        db = get_db()
        # Los ? separan los datos del SQL: no se concatenan entradas del usuario.
        with db:
            cursor = db.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
                tuple(datos[campo] for campo in CAMPOS),
            )
            nuevo_id = cursor.lastrowid
        respuesta = jsonify(dict(buscar_avistamiento(nuevo_id)))
        respuesta.status_code = 201
        respuesta.headers["Location"] = url_for(
            "obtener_avistamiento", avistamiento_id=nuevo_id
        )
        return respuesta

    @app.put("/avistamientos/<int:avistamiento_id>")
    def actualizar_avistamiento(avistamiento_id):
        if buscar_avistamiento(avistamiento_id) is None:
            return jsonify(error="Avistamiento no encontrado."), 404
        datos = validar_avistamiento()
        db = get_db()
        with db:
            cursor = db.execute(
                "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
                tuple(datos[campo] for campo in CAMPOS) + (avistamiento_id,),
            )
        if cursor.rowcount == 0:
            return jsonify(error="Avistamiento no encontrado."), 404
        return jsonify(dict(buscar_avistamiento(avistamiento_id))), 200

    @app.delete("/avistamientos/<int:avistamiento_id>")
    def eliminar_avistamiento(avistamiento_id):
        if not 1 <= avistamiento_id <= MAX_SQLITE_ID:
            return jsonify(error="Avistamiento no encontrado."), 404
        db = get_db()
        with db:
            cursor = db.execute(
                "DELETE FROM avistamientos WHERE id = ?", (avistamiento_id,)
            )
        if cursor.rowcount == 0:
            return jsonify(error="Avistamiento no encontrado."), 404
        return jsonify(mensaje="Avistamiento eliminado.", id=avistamiento_id), 200

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API REST de avistamientos de aves")
    parser.add_argument("--port", type=int, default=5000, help="Puerto local (por defecto: 5000)")
    args = parser.parse_args()
    create_app().run(host="127.0.0.1", port=args.port, debug=False)
