"""Operaciones de la aplicación: conocen reglas y puertos, no tecnologías."""
from .puertos import GestionAvistamientos, RepositorioAvistamientos, Reloj
from .validacion import validar_avistamiento


class AvistamientoNoEncontrado(Exception):
    """El registro solicitado no existe; el adaptador decide cómo comunicarlo."""

    def __init__(self):
        super().__init__("Avistamiento no encontrado.")


class ServicioAvistamientos(GestionAvistamientos):
    def __init__(self, repositorio: RepositorioAvistamientos, reloj: Reloj):
        self.repositorio = repositorio
        self.reloj = reloj

    def listar(self):
        return self.repositorio.listar()

    def obtener(self, identificador):
        registro = self.repositorio.obtener(identificador)
        if registro is None:
            raise AvistamientoNoEncontrado()
        return registro

    def crear(self, datos):
        limpios = validar_avistamiento(datos, self.reloj)
        return self.repositorio.crear(limpios)

    def actualizar(self, identificador, datos):
        self.obtener(identificador)
        limpios = validar_avistamiento(datos, self.reloj)
        registro = self.repositorio.actualizar(identificador, limpios)
        if registro is None:
            raise AvistamientoNoEncontrado()
        return registro

    def eliminar(self, identificador):
        if not self.repositorio.eliminar(identificador):
            raise AvistamientoNoEncontrado()

    def resumen(self):
        return self.repositorio.resumen()
