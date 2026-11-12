"""Punto de composición y arranque de la API de avistamientos."""
import argparse
from pathlib import Path

from flask import Flask, g

from avistamientos.adaptadores.http import registrar_http
from avistamientos.adaptadores.reloj import RelojSistema
from avistamientos.adaptadores.sqlite import RepositorioSQLite, conectar, inicializar
from avistamientos.nucleo.servicio import ServicioAvistamientos


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(Path(__file__).resolve().parent / "data" / "avistamientos.db"),
        MAX_CONTENT_LENGTH=64 * 1024,
        RELOJ=RelojSistema(),
    )
    if test_config:
        app.config.update(test_config)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    inicializar(app.config["DATABASE"])

    def servicio():
        # Una conexión por contexto; el núcleo no conoce g ni la configuración.
        if "db" not in g:
            g.db = conectar(app.config["DATABASE"])
        return ServicioAvistamientos(RepositorioSQLite(g.db), app.config["RELOJ"])

    @app.teardown_appcontext
    def cerrar_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    registrar_http(app, servicio)
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API REST de avistamientos de aves")
    parser.add_argument("--port", type=int, default=5000, help="Puerto local (por defecto: 5000)")
    args = parser.parse_args()
    create_app().run(host="127.0.0.1", port=args.port, debug=False)
