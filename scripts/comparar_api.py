"""Ejecuta una secuencia fija de peticiones contra una versión de la API.

Uso:  python comparar_api.py RUTA_DEL_PROYECTO > salida.txt
Sirve para comparar dos revisiones (antes y después del refactor) con diff.
Usa el cliente de pruebas de Flask, un reloj fijo y una base temporal nueva.
"""
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

proyecto = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(proyecto))
from app import create_app  # noqa: E402


class RelojFijo:
    def hoy(self):
        return date(2026, 10, 21)


VALIDO = {"especie": "colibrí", "lugar": "Bogotá", "fecha": "2026-10-21", "observador": "Nicolás"}
JSON = {"Content-Type": "application/json"}


def peticiones():
    """(descripción, método, ruta, kwargs de la petición)"""
    return [
        ("GET lista vacía", "GET", "/avistamientos", {}),
        ("POST datos válidos", "POST", "/avistamientos", {"json": VALIDO}),
        ("GET por id", "GET", "/avistamientos/1", {}),
        ("PUT reemplazo válido", "PUT", "/avistamientos/1", {"json": {**VALIDO, "lugar": "Humedal Santa María del Lago"}}),
        ("GET resumen", "GET", "/avistamientos/resumen", {}),
        ("PUT especie corta (400)", "PUT", "/avistamientos/1", {"json": {**VALIDO, "especie": "ab"}}),
        ("PUT id inexistente + JSON roto (404)", "PUT", "/avistamientos/99", {"data": "{roto", "headers": JSON}),
        ("PUT id existente + JSON roto (400)", "PUT", "/avistamientos/1", {"data": "{roto", "headers": JSON}),
        ("POST sin Content-Type JSON (400)", "POST", "/avistamientos", {"data": "x"}),
        ("POST campos faltantes (400)", "POST", "/avistamientos", {"json": {"especie": "colibrí"}}),
        ("POST campo extra (400)", "POST", "/avistamientos", {"json": {**VALIDO, "id": 7}}),
        ("POST fecha imposible (400)", "POST", "/avistamientos", {"json": {**VALIDO, "fecha": "2026-02-30"}}),
        ("POST fecha futura (400)", "POST", "/avistamientos", {"json": {**VALIDO, "fecha": "2026-10-22"}}),
        ("POST tipo incorrecto (400)", "POST", "/avistamientos", {"json": {**VALIDO, "lugar": 5}}),
        ("POST cuerpo no objeto (400)", "POST", "/avistamientos", {"json": [1, 2]}),
        ("POST cuerpo excesivo (413)", "POST", "/avistamientos", {"data": "x" * (65 * 1024), "headers": JSON}),
        ("GET lista con un registro", "GET", "/avistamientos", {}),
        ("PATCH no implementado (405)", "PATCH", "/avistamientos/1", {"json": VALIDO}),
        ("DELETE colección (405)", "DELETE", "/avistamientos", {}),
        ("GET ruta inexistente (404)", "GET", "/nada", {}),
        ("GET id no numérico (404)", "GET", "/avistamientos/abc", {}),
        ("DELETE existente", "DELETE", "/avistamientos/1", {}),
        ("GET tras borrar (404)", "GET", "/avistamientos/1", {}),
        ("DELETE repetido (404)", "DELETE", "/avistamientos/1", {}),
        ("PUT tras borrar (404)", "PUT", "/avistamientos/1", {"json": VALIDO}),
        ("GET resumen vacío", "GET", "/avistamientos/resumen", {}),
    ]


with tempfile.TemporaryDirectory() as tmp:
    app = create_app({"TESTING": True, "DATABASE": str(Path(tmp) / "t.db"), "RELOJ": RelojFijo()})
    cliente = app.test_client()
    for descripcion, metodo, ruta, kw in peticiones():
        r = cliente.open(ruta, method=metodo, **kw)
        permitido = r.headers.get("Allow")
        print(json.dumps({
            "peticion": f"{metodo} {ruta} :: {descripcion}",
            "estado": r.status_code,
            "content_type": r.headers.get("Content-Type"),
            "location": r.headers.get("Location"),
            "allow": sorted(permitido.replace(" ", "").split(",")) if permitido else None,
            "cuerpo": r.get_data(as_text=True).strip(),
        }, ensure_ascii=False))
