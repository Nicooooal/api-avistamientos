"""Nivel unitario: sin contexto Flask, solicitudes HTTP ni conexión SQLite."""

from datetime import date
from unittest.mock import Mock

import pytest

from validacion import ErrorValidacion, Reloj, validar_avistamiento


@pytest.mark.parametrize("especie", ["abc", "colibrí", "a" * 50], ids=["minimo_3", "interior_7", "maximo_50"])
def test_acepta_especie_dentro_de_3_a_50_caracteres(datos, reloj, especie):
    # Arrange
    entrada = {**datos, "especie": especie}
    # Act
    resultado = validar_avistamiento(entrada, reloj)
    # Assert
    assert resultado == entrada


@pytest.mark.parametrize("especie", ["ab", "a" * 51], ids=["inferior_2", "superior_51"])
def test_rechaza_especie_fuera_de_limites_e_identifica_el_campo(datos, reloj, especie):
    # Arrange
    entrada = {**datos, "especie": especie}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == "El campo 'especie' debe tener entre 3 y 50 caracteres."


@pytest.mark.parametrize("fecha", ["2026-10-20", "2026-10-21", "2024-02-29"], ids=["ayer", "hoy", "bisiesto_pasado"])
def test_acepta_fecha_real_no_posterior_al_reloj(datos, reloj, fecha):
    # Arrange
    entrada = {**datos, "fecha": fecha}
    # Act
    resultado = validar_avistamiento(entrada, reloj)
    # Assert
    assert resultado == entrada


@pytest.mark.parametrize("fecha", ["2026-10-22", "2026-11-21"], ids=["manana", "futuro_representativo"])
def test_rechaza_fecha_posterior_al_reloj_fijo(datos, reloj, fecha):
    # Arrange
    entrada = {**datos, "fecha": fecha}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == "El campo 'fecha' no puede ser posterior a hoy."


@pytest.mark.parametrize("fecha", ["21/10/2026", "2026-1-21", "texto"])
def test_rechaza_fecha_con_formato_incorrecto(datos, reloj, fecha):
    # Arrange
    entrada = {**datos, "fecha": fecha}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == "El campo 'fecha' debe tener el formato AAAA-MM-DD."


@pytest.mark.parametrize("fecha", ["2025-02-29", "2026-02-30", "0000-01-01"])
def test_rechaza_fecha_imposible_aunque_tenga_formato_correcto(datos, reloj, fecha):
    # Arrange
    entrada = {**datos, "fecha": fecha}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == "El campo 'fecha' debe ser una fecha real del calendario."


@pytest.mark.parametrize("campo", ["especie", "lugar", "fecha", "observador"])
@pytest.mark.parametrize("valor", ["", "   ", None, 25, True, [], {}])
def test_rechaza_campos_sin_texto_no_vacio(datos, reloj, campo, valor):
    # Arrange
    entrada = {**datos, campo: valor}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == f"El campo '{campo}' debe ser texto no vacío."


@pytest.mark.parametrize("campo", ["especie", "lugar", "fecha", "observador"])
def test_rechaza_objeto_si_falta_un_campo_obligatorio(datos, reloj, campo):
    # Arrange
    entrada = {k: v for k, v in datos.items() if k != campo}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == f"Faltan campos obligatorios: {campo}."


@pytest.mark.parametrize("entrada", [[], None, "texto"])
def test_rechaza_cuerpo_que_no_es_objeto(reloj, entrada):
    # Arrange
    cuerpo = entrada
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(cuerpo, reloj)
    # Assert
    assert str(error.value) == "El cuerpo debe ser un objeto JSON."


@pytest.mark.parametrize("campo", ["id", "color"])
def test_rechaza_campos_adicionales(datos, reloj, campo):
    # Arrange
    entrada = {**datos, campo: "extra"}
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(entrada, reloj)
    # Assert
    assert str(error.value) == f"Campos no permitidos: {campo}. El id lo asigna el sistema."


def test_recorta_espacios_antes_de_validar_sin_modificar_la_entrada(datos, reloj):
    # Arrange
    entrada = {**datos, "especie": "  abc  ", "lugar": "  Bogotá  "}
    original = entrada.copy()
    # Act
    resultado = validar_avistamiento(entrada, reloj)
    # Assert
    assert resultado == {**datos, "especie": "abc", "lugar": "Bogotá"}
    assert entrada == original


def test_la_misma_fecha_cambia_de_validez_segun_el_reloj_inyectado(datos):
    # Arrange: Mock usado como stub, sin verificar interacciones.
    reloj = Mock(spec=Reloj)
    reloj.hoy.return_value = date(2026, 10, 20)
    # Act
    with pytest.raises(ErrorValidacion) as error:
        validar_avistamiento(datos, reloj)
    reloj.hoy.return_value = date(2026, 10, 21)
    resultado = validar_avistamiento(datos, reloj)
    # Assert
    assert "posterior a hoy" in str(error.value)
    assert resultado == datos
