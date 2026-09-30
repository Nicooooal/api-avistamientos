"""Pruebas de integración: peticiones HTTP simuladas y SQLite real temporal."""

import sqlite3
import tempfile
import unittest
from pathlib import Path
from contextlib import closing

from app import create_app


class AvistamientosTestCase(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.database = str(Path(self.temporal.name) / "pruebas.db")
        self.app = create_app({"TESTING": True, "DATABASE": self.database})
        self.client = self.app.test_client()
        self.datos = {
            "especie": "colibrí",
            "lugar": "Jardín Botánico de Bogotá",
            "fecha": "2026-09-29",
            "observador": "Nicolás",
        }

    def crear(self, **cambios):
        return self.client.post("/avistamientos", json={**self.datos, **cambios})

    def assert_json(self, respuesta, codigo):
        self.assertEqual(respuesta.status_code, codigo)
        self.assertEqual(respuesta.mimetype, "application/json")

    def test_listar_base_vacia(self):
        respuesta = self.client.get("/avistamientos")
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json(), [])

    def test_crear_devuelve_id_y_location(self):
        respuesta = self.crear()
        self.assert_json(respuesta, 201)
        self.assertEqual(respuesta.get_json(), {"id": 1, **self.datos})
        self.assertEqual(respuesta.headers["Location"], "/avistamientos/1")
        self.assertEqual(self.client.get("/avistamientos").get_json(), [respuesta.get_json()])

    def test_ids_generados_son_distintos(self):
        a, b = self.crear().get_json(), self.crear().get_json()
        self.assertNotEqual(a["id"], b["id"])

    def test_obtener_existente(self):
        creado = self.crear().get_json()
        respuesta = self.client.get(f"/avistamientos/{creado['id']}")
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json(), creado)

    def test_obtener_inexistente(self):
        self.assert_json(self.client.get("/avistamientos/999"), 404)

    def test_post_rechaza_cada_campo_faltante(self):
        for campo in self.datos:
            with self.subTest(campo=campo):
                datos = {k: v for k, v in self.datos.items() if k != campo}
                self.assert_json(self.client.post("/avistamientos", json=datos), 400)
        self.assertEqual(self.client.get("/avistamientos").get_json(), [])

    def test_campos_deben_ser_texto_no_vacio(self):
        for campo in self.datos:
            for valor in ("", "   ", None, 25, True, [], {}):
                with self.subTest(campo=campo, valor=valor):
                    self.assert_json(self.crear(**{campo: valor}), 400)

    def test_fechas_invalidas(self):
        for fecha in ("29/09/2026", "2026-9-29", "2026-02-30", "2025-02-29", "0000-01-01"):
            with self.subTest(fecha=fecha):
                self.assert_json(self.crear(fecha=fecha), 400)

    def test_fecha_bisiesta_valida(self):
        self.assert_json(self.crear(fecha="2024-02-29"), 201)

    def test_rechaza_id_y_campos_desconocidos(self):
        self.assert_json(self.crear(id=123), 400)
        self.assert_json(self.crear(color="verde"), 400)

    def test_json_malformado(self):
        respuesta = self.client.post("/avistamientos", data='{"especie":', content_type="application/json")
        self.assert_json(respuesta, 400)

    def test_cuerpo_no_es_objeto_json(self):
        for cuerpo in ("[]", "null", '"texto"', "42"):
            with self.subTest(cuerpo=cuerpo):
                respuesta = self.client.post("/avistamientos", data=cuerpo, content_type="application/json")
                self.assert_json(respuesta, 400)

    def test_sin_content_type_json(self):
        respuesta = self.client.post("/avistamientos", data="especie=colibri")
        self.assert_json(respuesta, 400)

    def test_sin_cuerpo(self):
        self.assert_json(self.client.post("/avistamientos", content_type="application/json"), 400)

    def test_actualizar_conserva_id(self):
        creado = self.crear().get_json()
        nuevos = {**self.datos, "lugar": "Humedal Santa María del Lago"}
        respuesta = self.client.put(f"/avistamientos/{creado['id']}", json=nuevos)
        self.assert_json(respuesta, 200)
        esperado = {"id": creado["id"], **nuevos}
        self.assertEqual(respuesta.get_json(), esperado)
        self.assertEqual(self.client.get(f"/avistamientos/{creado['id']}").get_json(), esperado)

    def test_actualizar_inexistente(self):
        self.assert_json(self.client.put("/avistamientos/999", json=self.datos), 404)

    def test_put_repetido_es_idempotente(self):
        creado = self.crear().get_json()
        url = f"/avistamientos/{creado['id']}"
        nuevos = {**self.datos, "lugar": "Humedal"}
        primera = self.client.put(url, json=nuevos)
        segunda = self.client.put(url, json=nuevos)
        self.assert_json(primera, 200)
        self.assert_json(segunda, 200)
        self.assertEqual(primera.get_json(), segunda.get_json())
        self.assertEqual(self.client.get("/avistamientos").get_json(), [segunda.get_json()])

    def test_put_incompleto_no_modifica_datos(self):
        creado = self.crear().get_json()
        url = f"/avistamientos/{creado['id']}"
        self.assert_json(self.client.put(url, json={"lugar": "Otro"}), 400)
        self.assertEqual(self.client.get(url).get_json(), creado)

    def test_eliminar_y_consultar_despues(self):
        creado = self.crear().get_json()
        url = f"/avistamientos/{creado['id']}"
        respuesta = self.client.delete(url)
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json()["id"], creado["id"])
        self.assert_json(self.client.get(url), 404)
        self.assert_json(self.client.delete(url), 404)

    def test_eliminar_inexistente(self):
        self.assert_json(self.client.delete("/avistamientos/999"), 404)

    def test_resumen_vacio(self):
        respuesta = self.client.get("/avistamientos/resumen")
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json(), [])

    def test_resumen_agrupa_por_especie(self):
        self.crear()
        self.crear()
        self.crear(especie="copetón")
        respuesta = self.client.get("/avistamientos/resumen")
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json(), [
            {"especie": "colibrí", "cantidad": 2},
            {"especie": "copetón", "cantidad": 1},
        ])

    def test_resumen_refleja_actualizacion_y_borrado(self):
        a, b = self.crear().get_json(), self.crear().get_json()
        self.client.put(f"/avistamientos/{a['id']}", json={**self.datos, "especie": "copetón"})
        self.client.delete(f"/avistamientos/{b['id']}")
        self.assertEqual(self.client.get("/avistamientos/resumen").get_json(), [{"especie": "copetón", "cantidad": 1}])

    def test_persistencia_al_recrear_aplicacion(self):
        creado = self.crear().get_json()
        otra_app = create_app({"TESTING": True, "DATABASE": self.database})
        respuesta = otra_app.test_client().get(f"/avistamientos/{creado['id']}")
        self.assert_json(respuesta, 200)
        self.assertEqual(respuesta.get_json(), creado)
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM avistamientos").fetchone()[0], 1)

    def test_entradas_sql_se_guardan_como_texto(self):
        texto = "ave'); DROP TABLE avistamientos; --"
        self.assert_json(self.crear(especie=texto), 201)
        self.assertEqual(self.client.get("/avistamientos").get_json()[0]["especie"], texto)
        self.assert_json(self.crear(), 201)

    def test_recorta_espacios_exteriores(self):
        respuesta = self.crear(especie="  colibrí  ")
        self.assertEqual(respuesta.get_json()["especie"], "colibrí")

    def test_ruta_desconocida_responde_json(self):
        self.assert_json(self.client.get("/no-existe"), 404)

    def test_metodo_no_permitido_responde_json(self):
        respuesta = self.client.patch("/avistamientos/1", json=self.datos)
        self.assert_json(respuesta, 405)
        self.assertIn("PUT", respuesta.headers["Allow"])

    def test_ids_fuera_de_rango_no_producen_500(self):
        for identificador in ("0", "-1", "abc", "999999999999999999999999"):
            for metodo in ("get", "put", "delete"):
                with self.subTest(identificador=identificador, metodo=metodo):
                    respuesta = getattr(self.client, metodo)(f"/avistamientos/{identificador}")
                    self.assert_json(respuesta, 404)

    def test_cuerpo_excesivo(self):
        self.assert_json(self.crear(lugar="x" * 70000), 413)


if __name__ == "__main__":
    unittest.main()
