"""Contratos del núcleo, sin dependencias de Flask o SQLite."""
from datetime import date
from typing import Protocol


class Reloj(Protocol):
    def hoy(self) -> date:
        """Fecha de referencia de la aplicación."""
