"""Compatibilidad con los imports del taller de pruebas anterior.

La implementación está en el núcleo; este módulo no contiene reglas duplicadas.
"""
from avistamientos.nucleo.validacion import CAMPOS, ErrorValidacion, validar_avistamiento
from avistamientos.nucleo.puertos import Reloj
from avistamientos.adaptadores.reloj import RelojSistema

__all__ = ["CAMPOS", "ErrorValidacion", "validar_avistamiento", "Reloj", "RelojSistema"]
