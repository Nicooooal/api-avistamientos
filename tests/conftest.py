from datetime import date

import pytest

from app import create_app


class RelojFijo:
    """Stub: siempre entrega la fecha configurada, sin consultar el sistema."""

    def __init__(self, fecha):
        self.fecha = fecha

    def hoy(self):
        return self.fecha


@pytest.fixture
def reloj():
    return RelojFijo(date(2026, 10, 21))


@pytest.fixture
def datos():
    return {
        "especie": "colibrí",
        "lugar": "Jardín Botánico de Bogotá",
        "fecha": "2026-10-21",
        "observador": "Nicolás",
    }


@pytest.fixture
def app(tmp_path, reloj):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "pruebas.db"), "RELOJ": reloj})


@pytest.fixture
def client(app):
    return app.test_client()
