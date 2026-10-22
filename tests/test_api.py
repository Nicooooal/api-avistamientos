"""Integración del contrato HTTP, validación y SQLite real."""
import pytest
from app import create_app


def comprobar(respuesta, codigo, cuerpo):
    assert respuesta.status_code == codigo
    assert respuesta.mimetype == "application/json"
    assert respuesta.get_json() == cuerpo


def crear(client, datos):
    respuesta = client.post("/avistamientos", json=datos)
    assert respuesta.status_code == 201
    return respuesta.get_json()


def test_get_coleccion_vacia_responde_200_y_array_vacio(client):
    # Arrange: base exclusiva y vacía proporcionada por la fixture.
    ruta = "/avistamientos"
    # Act
    respuesta = client.get(ruta)
    # Assert
    comprobar(respuesta, 200, [])


def test_get_coleccion_devuelve_registros_ordenados_sin_modificarlos(client, datos):
    # Arrange
    a = crear(client, datos)
    b = crear(client, {**datos, "especie": "copetón"})
    # Act
    respuesta = client.get("/avistamientos")
    # Assert
    comprobar(respuesta, 200, [a, b])
    comprobar(client.get("/avistamientos"), 200, [a, b])


def test_post_valido_devuelve_201_location_y_registro_consultable(client, datos):
    # Arrange
    entrada = datos.copy()
    # Act
    respuesta = client.post("/avistamientos", json=entrada)
    # Assert
    creado = respuesta.get_json()
    assert type(creado["id"]) is int and creado["id"] > 0
    comprobar(respuesta, 201, {"id": creado["id"], **entrada})
    assert respuesta.headers["Location"] == f"/avistamientos/{creado['id']}"
    comprobar(client.get(respuesta.headers["Location"]), 200, creado)
    comprobar(client.get("/avistamientos"), 200, [creado])


def test_get_id_existente_devuelve_todos_los_campos(client, datos):
    # Arrange
    creado = crear(client, datos)
    # Act
    respuesta = client.get(f"/avistamientos/{creado['id']}")
    # Assert
    comprobar(respuesta, 200, creado)


@pytest.mark.parametrize("metodo", ["get", "put", "delete"])
@pytest.mark.parametrize("identificador", ["999", "0", "999999999999999999999999"])
def test_id_inexistente_o_fuera_de_rango_devuelve_404_sin_alterar_datos(client, datos, metodo, identificador):
    # Arrange
    ruta = f"/avistamientos/{identificador}"
    # Act
    respuesta = getattr(client, metodo)(ruta, json=datos)
    # Assert
    comprobar(respuesta, 404, {"error": "Avistamiento no encontrado."})
    comprobar(client.get("/avistamientos"), 200, [])


def test_put_reemplaza_campos_y_conserva_id(client, datos):
    # Arrange
    creado = crear(client, datos)
    ruta = f"/avistamientos/{creado['id']}"
    nuevos = {"especie": "copetón", "lugar": "Humedal", "fecha": "2026-10-20", "observador": "Ana"}
    esperado = {"id": creado["id"], **nuevos}
    # Act
    primera = client.put(ruta, json=nuevos)
    # Assert
    comprobar(primera, 200, esperado)
    comprobar(client.get(ruta), 200, esperado)
    comprobar(client.get("/avistamientos"), 200, [esperado])


def test_repetir_put_no_crea_otro_registro_ni_cambia_el_resultado(client, datos):
    # Arrange: el recurso ya recibió una actualización correcta.
    creado = crear(client, datos)
    ruta = f"/avistamientos/{creado['id']}"
    nuevos = {**datos, "lugar": "Humedal"}
    esperado = {"id": creado["id"], **nuevos}
    comprobar(client.put(ruta, json=nuevos), 200, esperado)
    # Act
    respuesta = client.put(ruta, json=nuevos)
    # Assert
    comprobar(respuesta, 200, esperado)
    comprobar(client.get("/avistamientos"), 200, [esperado])


@pytest.mark.parametrize("metodo", ["post", "put"])
@pytest.mark.parametrize("campo,valor,mensaje", [
    ("especie", "ab", "El campo 'especie' debe tener entre 3 y 50 caracteres."),
    ("especie", "a" * 51, "El campo 'especie' debe tener entre 3 y 50 caracteres."),
    ("fecha", "2026-10-22", "El campo 'fecha' no puede ser posterior a hoy."),
    ("fecha", "21/10/2026", "El campo 'fecha' debe tener el formato AAAA-MM-DD."),
    ("lugar", "  ", "El campo 'lugar' debe ser texto no vacío."),
    ("observador", "", "El campo 'observador' debe ser texto no vacío."),
])
def test_post_y_put_invalidos_responden_400_con_campo_y_conservan_la_base(client, datos, metodo, campo, valor, mensaje):
    # Arrange
    existente = crear(client, datos)
    ruta = "/avistamientos" if metodo == "post" else f"/avistamientos/{existente['id']}"
    entrada = {**datos, campo: valor}
    # Act
    respuesta = getattr(client, metodo)(ruta, json=entrada)
    # Assert
    comprobar(respuesta, 400, {"error": mensaje})
    comprobar(client.get("/avistamientos"), 200, [existente])


@pytest.mark.parametrize("metodo", ["post", "put"])
@pytest.mark.parametrize("especie", ["abc", "a" * 50])
def test_post_y_put_aceptan_limites_de_especie_y_fecha_de_hoy(client, datos, metodo, especie):
    # Arrange
    anterior = crear(client, datos) if metodo == "put" else None
    ruta = f"/avistamientos/{anterior['id']}" if anterior else "/avistamientos"
    entrada = {**datos, "especie": especie}
    # Act
    respuesta = getattr(client, metodo)(ruta, json=entrada)
    # Assert
    identificador = anterior["id"] if anterior else respuesta.get_json()["id"]
    esperado = {"id": identificador, **entrada}
    comprobar(respuesta, 200 if anterior else 201, esperado)
    comprobar(client.get(f"/avistamientos/{identificador}"), 200, esperado)


@pytest.mark.parametrize("metodo", ["post", "put"])
def test_post_y_put_incompletos_identifican_faltantes_sin_cambiar_datos(client, datos, metodo):
    # Arrange
    existente = crear(client, datos)
    ruta = "/avistamientos" if metodo == "post" else f"/avistamientos/{existente['id']}"
    # Act
    respuesta = getattr(client, metodo)(ruta, json={"especie": "colibrí"})
    # Assert
    comprobar(respuesta, 400, {"error": "Faltan campos obligatorios: lugar, fecha, observador."})
    comprobar(client.get("/avistamientos"), 200, [existente])


def test_delete_elimina_solo_el_id_indicado_y_consulta_posterior_responde_404(client, datos):
    # Arrange
    a = crear(client, datos)
    b = crear(client, {**datos, "especie": "copetón"})
    ruta = f"/avistamientos/{a['id']}"
    # Act
    respuesta = client.delete(ruta)
    # Assert
    comprobar(respuesta, 200, {"mensaje": "Avistamiento eliminado.", "id": a["id"]})
    comprobar(client.get(ruta), 404, {"error": "Avistamiento no encontrado."})
    comprobar(client.get("/avistamientos"), 200, [b])


def test_repetir_delete_responde_404_y_conserva_la_ausencia(client, datos):
    # Arrange
    creado = crear(client, datos)
    ruta = f"/avistamientos/{creado['id']}"
    comprobar(client.delete(ruta), 200, {"mensaje": "Avistamiento eliminado.", "id": creado["id"]})
    # Act
    respuesta = client.delete(ruta)
    # Assert
    comprobar(respuesta, 404, {"error": "Avistamiento no encontrado."})
    comprobar(client.get("/avistamientos"), 200, [])


def test_resumen_sin_registros_devuelve_array_vacio(client):
    # Arrange
    ruta = "/avistamientos/resumen"
    # Act
    respuesta = client.get(ruta)
    # Assert
    comprobar(respuesta, 200, [])


def test_resumen_agrupa_registros_por_especie(client, datos):
    # Arrange
    crear(client, datos)
    crear(client, datos)
    crear(client, {**datos, "especie": "copetón"})
    # Act
    respuesta = client.get("/avistamientos/resumen")
    # Assert
    comprobar(respuesta, 200, [{"especie": "colibrí", "cantidad": 2}, {"especie": "copetón", "cantidad": 1}])


def test_resumen_refleja_el_cambio_de_especie(client, datos):
    # Arrange
    a = crear(client, datos)
    crear(client, datos)
    nuevos = {**datos, "especie": "copetón"}
    comprobar(client.put(f"/avistamientos/{a['id']}", json=nuevos), 200, {"id": a["id"], **nuevos})
    # Act
    respuesta = client.get("/avistamientos/resumen")
    # Assert
    comprobar(respuesta, 200, [{"especie": "colibrí", "cantidad": 1}, {"especie": "copetón", "cantidad": 1}])


def test_resumen_deja_de_contar_un_registro_eliminado(client, datos):
    # Arrange
    a = crear(client, datos)
    crear(client, datos)
    comprobar(client.delete(f"/avistamientos/{a['id']}"), 200, {"mensaje": "Avistamiento eliminado.", "id": a["id"]})
    # Act
    respuesta = client.get("/avistamientos/resumen")
    # Assert
    comprobar(respuesta, 200, [{"especie": "colibrí", "cantidad": 1}])


def test_registro_persiste_al_recrear_aplicacion_con_el_mismo_archivo(client, app, datos, reloj):
    # Arrange
    creado = crear(client, datos)
    otra_app = create_app({"TESTING": True, "DATABASE": app.config["DATABASE"], "RELOJ": reloj})
    # Act
    respuesta = otra_app.test_client().get(f"/avistamientos/{creado['id']}")
    # Assert
    comprobar(respuesta, 200, creado)


def test_texto_sql_se_guarda_como_dato_y_la_tabla_permanece(client, datos):
    # Arrange
    entrada = {**datos, "especie": "ave'); DROP TABLE avistamientos; --"}
    otro = crear(client, datos)
    # Act
    respuesta = client.post("/avistamientos", json=entrada)
    # Assert
    creado = respuesta.get_json()
    comprobar(respuesta, 201, {"id": creado["id"], **entrada})
    assert otro["id"] != creado["id"]
    comprobar(client.get("/avistamientos"), 200, [otro, creado])


@pytest.mark.parametrize("cuerpo", ["[]", "null", '"texto"', "42"])
def test_post_json_no_objeto_devuelve_400_y_no_inserta(client, cuerpo):
    # Arrange
    ruta = "/avistamientos"
    # Act
    respuesta = client.post(ruta, data=cuerpo, content_type="application/json")
    # Assert
    comprobar(respuesta, 400, {"error": "El cuerpo debe ser un objeto JSON."})
    comprobar(client.get(ruta), 200, [])


@pytest.mark.parametrize("cuerpo,tipo,codigo", [('{"especie":', "application/json", 400), ("", "application/json", 400), ("especie=ave", "text/plain", 400), ('{"lugar":"' + 'x' * 70000 + '"}', "application/json", 413)])
def test_cuerpo_http_invalido_devuelve_error_json_sin_insertar(client, cuerpo, tipo, codigo):
    # Arrange
    ruta = "/avistamientos"
    # Act
    respuesta = client.post(ruta, data=cuerpo, content_type=tipo)
    # Assert: el mensaje de sintaxis/tamaño lo genera Flask, se exige esquema y texto útil.
    assert respuesta.status_code == codigo
    assert respuesta.mimetype == "application/json"
    error = respuesta.get_json()
    assert set(error) == {"error"} and isinstance(error["error"], str) and error["error"].strip()
    comprobar(client.get(ruta), 200, [])


@pytest.mark.parametrize("ruta,metodo,codigo", [("/no-existe", "get", 404), ("/avistamientos/1", "patch", 405)])
def test_errores_de_enrutamiento_conservan_codigo_json_y_cabeceras(client, ruta, metodo, codigo):
    # Arrange
    peticion = getattr(client, metodo)
    # Act
    respuesta = peticion(ruta)
    # Assert
    assert respuesta.status_code == codigo
    assert respuesta.mimetype == "application/json"
    cuerpo = respuesta.get_json()
    assert set(cuerpo) == {"error"} and isinstance(cuerpo["error"], str) and cuerpo["error"]
    if codigo == 405:
        assert "PUT" in respuesta.headers["Allow"]
