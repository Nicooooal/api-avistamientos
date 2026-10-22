"""Regla de negocio independiente de Flask y de la base de datos."""

import re
from datetime import date
from typing import Protocol

CAMPOS = ("especie", "lugar", "fecha", "observador")


class Reloj(Protocol):
    def hoy(self) -> date:
        """Entrega la fecha de referencia para validar un avistamiento."""


class RelojSistema:
    def hoy(self) -> date:
        return date.today()


class ErrorValidacion(ValueError):
    """Datos que no cumplen el contrato o la regla de negocio."""


def validar_avistamiento(datos, reloj: Reloj):
    """Devuelve una copia normalizada o informa qué campo es inválido."""
    if not isinstance(datos, dict):
        raise ErrorValidacion("El cuerpo debe ser un objeto JSON.")

    faltantes = [campo for campo in CAMPOS if campo not in datos]
    if faltantes:
        raise ErrorValidacion("Faltan campos obligatorios: " + ", ".join(faltantes) + ".")

    adicionales = sorted(set(datos) - set(CAMPOS))
    if adicionales:
        raise ErrorValidacion(
            "Campos no permitidos: " + ", ".join(adicionales) + ". El id lo asigna el sistema."
        )

    limpios = {}
    for campo in CAMPOS:
        valor = datos[campo]
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion(f"El campo '{campo}' debe ser texto no vacío.")
        limpios[campo] = valor.strip()

    if not 3 <= len(limpios["especie"]) <= 50:
        raise ErrorValidacion("El campo 'especie' debe tener entre 3 y 50 caracteres.")

    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", limpios["fecha"]):
        raise ErrorValidacion("El campo 'fecha' debe tener el formato AAAA-MM-DD.")
    try:
        fecha = date.fromisoformat(limpios["fecha"])
    except ValueError as error:
        raise ErrorValidacion("El campo 'fecha' debe ser una fecha real del calendario.") from error
    if fecha > reloj.hoy():
        raise ErrorValidacion("El campo 'fecha' no puede ser posterior a hoy.")

    return limpios
