"""El puerto primario funciona con un fake, sin Flask ni SQLite."""
from collections import Counter
from datetime import date
import subprocess
import sys
from pathlib import Path

import pytest

from avistamientos.nucleo.servicio import AvistamientoNoEncontrado, ServicioAvistamientos
from avistamientos.nucleo.validacion import ErrorValidacion


class RepositorioMemoria:
    """Fake exclusivo de pruebas; conserva el contrato de datos del puerto."""
    def __init__(self):
        self.registros = {}
        self.siguiente = 1

    def listar(self):
        return [r.copy() for r in self.registros.values()]

    def obtener(self, identificador):
        registro = self.registros.get(identificador)
        return registro.copy() if registro is not None else None

    def crear(self, datos):
        identificador = self.siguiente
        self.siguiente += 1
        self.registros[identificador] = {"id": identificador, **datos}
        return self.obtener(identificador)

    def actualizar(self, identificador, datos):
        if identificador not in self.registros:
            return None
        self.registros[identificador] = {"id": identificador, **datos}
        return self.obtener(identificador)

    def eliminar(self, identificador):
        return self.registros.pop(identificador, None) is not None

    def resumen(self):
        conteo = Counter(r["especie"] for r in self.registros.values())
        return [{"especie": e, "cantidad": conteo[e]} for e in sorted(conteo)]


def test_crud_y_resumen_por_puerto_primario_con_repositorio_en_memoria(datos, reloj):
    # Arrange
    servicio = ServicioAvistamientos(RepositorioMemoria(), reloj)
    # Act: recorrido funcional sin adaptadores de producción.
    creado = servicio.crear(datos)
    consultado = servicio.obtener(creado["id"])
    actualizado = servicio.actualizar(creado["id"], {**datos, "especie": "copetón"})
    resumen = servicio.resumen()
    servicio.eliminar(creado["id"])
    # Assert
    assert consultado == {"id": 1, **datos}
    assert actualizado == {"id": 1, **datos, "especie": "copetón"}
    assert resumen == [{"especie": "copetón", "cantidad": 1}]
    assert servicio.listar() == []
    with pytest.raises(AvistamientoNoEncontrado):
        servicio.obtener(creado["id"])


def test_creacion_invalida_no_llega_al_repositorio(datos, reloj):
    # Arrange
    repositorio = RepositorioMemoria()
    servicio = ServicioAvistamientos(repositorio, reloj)
    # Act
    with pytest.raises(ErrorValidacion):
        servicio.crear({**datos, "especie": "ab"})
    # Assert
    assert repositorio.listar() == []
    assert repositorio.siguiente == 1


def test_nucleo_se_ejecuta_con_imports_externos_bloqueados():
    # Arrange: proceso limpio; conftest importa Flask en el proceso de pytest.
    programa = '''
import sys
import importlib.abc
from datetime import date
class Bloquear(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'flask', 'werkzeug', 'sqlite3', 'app', 'validacion'} or fullname.startswith('avistamientos.adaptadores'):
            raise ImportError('Dependencia externa en el núcleo: ' + fullname)
sys.meta_path.insert(0, Bloquear())
from avistamientos.nucleo.servicio import ServicioAvistamientos
class Reloj:
    def hoy(self): return date(2026, 10, 21)
class Repositorio:
    def crear(self, datos): return {'id': 1, **datos}
datos = {'especie': 'colibrí', 'lugar': 'Bogotá', 'fecha': '2026-10-21', 'observador': 'Nicolás'}
assert ServicioAvistamientos(Repositorio(), Reloj()).crear(datos) == {'id': 1, **datos}
'''
    # Act
    resultado = subprocess.run(
        [sys.executable, "-c", programa], cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True,
    )
    # Assert
    assert resultado.returncode == 0, resultado.stderr
