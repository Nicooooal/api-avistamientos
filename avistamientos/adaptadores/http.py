"""Adaptador primario: convierte HTTP a llamadas al puerto primario del núcleo."""
from typing import Callable

from flask import jsonify, request, url_for
from werkzeug.exceptions import BadRequest, HTTPException

from avistamientos.nucleo.puertos import GestionAvistamientos
from avistamientos.nucleo.servicio import AvistamientoNoEncontrado
from avistamientos.nucleo.validacion import ErrorValidacion


def leer_json():
    if not request.is_json:
        raise BadRequest("Envía el cuerpo con Content-Type: application/json.")
    return request.get_json()


def registrar_http(app, servicio: Callable[[], GestionAvistamientos]):
    @app.errorhandler(HTTPException)
    def error_http(error):
        respuesta = error.get_response()
        respuesta.data = app.json.dumps({"error": error.description})
        respuesta.content_type = "application/json"
        return respuesta

    @app.errorhandler(ErrorValidacion)
    def error_validacion(error):
        return error_http(BadRequest(str(error)))

    @app.errorhandler(AvistamientoNoEncontrado)
    def no_encontrado(error):
        return jsonify(error=str(error)), 404

    @app.errorhandler(500)
    def error_interno(_error):
        return jsonify(error="Error interno del servidor."), 500

    @app.get("/avistamientos")
    def listar_avistamientos():
        return jsonify(servicio().listar()), 200

    @app.get("/avistamientos/resumen")
    def resumen_avistamientos():
        return jsonify(servicio().resumen()), 200

    @app.get("/avistamientos/<int:avistamiento_id>")
    def obtener_avistamiento(avistamiento_id):
        return jsonify(servicio().obtener(avistamiento_id)), 200

    @app.post("/avistamientos")
    def crear_avistamiento():
        datos = leer_json()
        creado = servicio().crear(datos)
        respuesta = jsonify(creado)
        respuesta.status_code = 201
        respuesta.headers["Location"] = url_for(
            "obtener_avistamiento", avistamiento_id=creado["id"]
        )
        return respuesta

    @app.put("/avistamientos/<int:avistamiento_id>")
    def actualizar_avistamiento(avistamiento_id):
        operaciones = servicio()
        # Mantiene la precedencia original: id inexistente devuelve 404,
        # incluso si su cuerpo HTTP está mal formado o es excesivo.
        operaciones.obtener(avistamiento_id)
        datos = leer_json()
        return jsonify(operaciones.actualizar(avistamiento_id, datos)), 200

    @app.delete("/avistamientos/<int:avistamiento_id>")
    def eliminar_avistamiento(avistamiento_id):
        servicio().eliminar(avistamiento_id)
        return jsonify(mensaje="Avistamiento eliminado.", id=avistamiento_id), 200
