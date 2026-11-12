"""Adaptador secundario para consultar el reloj del equipo."""
from datetime import date
from avistamientos.nucleo.puertos import Reloj


class RelojSistema(Reloj):
    def hoy(self) -> date:
        return date.today()
