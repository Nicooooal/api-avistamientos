# Justificación de pruebas de la API de avistamientos

**Autor:** Nicolás Arias Lasprilla · **Curso:** Ingeniería de Software 2 · **Taller:** sesión 22, 21 de octubre de 2026.

## 1. Qué cambió en el código

La validación anterior dependía de `request` y de excepciones HTTP de Flask. Se extrajo a `validacion.py`: `validar_avistamiento(datos, reloj)` recibe un diccionario y una dependencia temporal, devuelve una copia normalizada o lanza `ErrorValidacion`. No abre conexiones ni conoce rutas HTTP. La función `leer_avistamiento()` de `app.py` se ocupa del transporte: lee JSON y convierte el error de negocio en 400.

La regla exige especie de 3 a 50 caracteres, fecha real AAAA-MM-DD no posterior a hoy, y lugar y observador con contenido. Se recortan espacios antes de validar. `Reloj` define la operación `hoy()`; `RelojSistema` usa la fecha local de la máquina y las pruebas inyectan un reloj fijo mediante la configuración `RELOJ`. Esta separación permite cambiar el tiempo de referencia sin cambiar el sistema operativo ni levantar la API.

Se conserva SQLite real en las integraciones. La suite se migró de unittest a pytest, con fixtures por caso, nombres de especificación y comentarios Arrange, Act y Assert (AAA). La API mantiene sus rutas y el id generado por SQLite. Un PUT sobre un id inexistente sigue respondiendo 404 antes de validar su cuerpo; la nueva regla de 400 se comprueba sobre recursos existentes.

## 2. Tabla de casos: particiones y valores límite

La tabla se preparó antes de programar la nueva suite y se conserva completa en [casos-validacion.md](casos-validacion.md). El reloj stub representa **2026-10-21**. Los demás campos de cada caso son válidos.

| Valor elegido | Tipo y partición | Resultado esperado y razón |
| --- | --- | --- |
| Especie `ab` (2) | Límite inválido, longitud menor que 3 | Error especie: vecino anterior al mínimo. |
| Especie `abc` (3) | Límite válido | Aceptar: mínimo incluido. |
| Especie `colibrí` (7) | Representativo válido | Aceptar: interior del intervalo. |
| Especie `a` × 50 | Límite válido | Aceptar: máximo incluido. |
| Especie `a` × 51 | Límite inválido, longitud mayor que 50 | Error especie: vecino posterior al máximo. |
| Especie `  abc  ` | Normalización | Aceptar y devolver `abc`; medir después del recorte. |
| Fecha 2026-10-20 | Límite válido, ayer | Aceptar: vecino inferior de hoy. |
| Fecha 2026-10-21 | Límite válido, hoy | Aceptar: extremo superior permitido. |
| Fecha 2026-10-22 | Límite inválido, mañana | Error fecha: primer día prohibido. |
| Fecha 2026-11-21 | Representativo futuro | Error fecha: interior de la partición rechazada. |
| Fecha 2024-02-29 | Representativo pasado válido | Aceptar un día bisiesto real. |
| 2025-02-29, 2026-02-30, 0000-01-01 | Calendario inválido | Error fecha aunque la estructura del texto sea correcta. |
| `21/10/2026`, `2026-1-21`, `texto` | Formato inválido | Error fecha: separadores, ancho o estructura incorrectos. |
| Campos vacíos o con espacios | Contenido inválido | Identificar el campo; incluye lugar y observador. |
| Campo ausente, null o tipo no textual | Contrato inválido | Identificar el campo faltante o de tipo incorrecto. |
| Lista/null/texto como cuerpo; campos extra | Estructura inválida | Error de objeto o de campo no permitido. |

Las particiones reducen entradas equivalentes; los límites detectan confusiones entre `<` y `<=`. No basta con una especie habitual: aceptarla no demuestra que 3 y 50 estén incluidos. La fecha se divide por formato, existencia en el calendario y relación con hoy. Los casos parametrizados comparten comportamiento y cambian la entrada; no se confunde su cantidad con su valor.

## 3. Por qué cada nivel

**Especie de 2/3/50/51 caracteres:** son pruebas unitarias porque cruzan solamente la frontera de la función de negocio. Reciben datos y un reloj stub, y verifican el resultado o el mensaje exacto. Detectan errores de límites sin introducir fallos de HTTP o SQL.

**Fecha de mañana:** también es unitaria. Compara contra una referencia temporal controlada; no necesita un servidor. Una prueba adicional cambia el retorno del reloj y demuestra que la misma fecha pasa de inválida a válida. Así se comprueba que la dependencia inyectada realmente controla la decisión.

**POST válido seguido de GET:** es integración porque atraviesa enrutamiento, lectura JSON, validación, INSERT y SELECT en SQLite, y serialización. Verifica 201, Content-Type, todos los campos, id y Location, y después consulta el registro. La unitaria no detectaría una columna mal enlazada, una escritura omitida ni un código HTTP incorrecto. PUT inválido verifica 400 y que el registro anterior siga intacto; DELETE comprueba que el id eliminado responda 404 y que otro registro permanezca.

Se utiliza `test_client()` de Flask, permitido expresamente por el taller. Recorre la frontera HTTP de la aplicación dentro del proceso, sin abrir un puerto TCP. Cada caso recibe un `tmp_path` distinto y crea su propia base, incluso al parametrizar. Las pruebas no dependen del orden ni de registros manuales. GET de colección no tiene parámetros obligatorios ni un recurso individual que pueda faltar: la colección vacía responde 200, por lo que no se inventa un 400 para esa operación.

## 4. Los dobles

`RelojFijo` es un **stub**: entrega una fecha prefijada. No almacena avistamientos, no simula un repositorio funcional y no verifica llamadas; por eso no se clasifica como fake, mock de interacciones ni spy. También se usa `unittest.mock.Mock(spec=Reloj)` como stub configurable en un caso: la clasificación depende del uso, no del nombre de la biblioteca.

Sin el doble, una fecha escrita como “mañana” podría dejar de ser futura al ejecutar la suite otro día. Calcularla a partir del sistema evitaría parte de ese problema, pero mantendría una dependencia de reloj y un posible cambio de día durante la ejecución. El stub elimina esa variación. SQLite permanece real en integración: sustituirlo ocultaría errores de SQL y persistencia. La aplicación no consume servicios externos, por lo que no necesita un servidor externo simulado.

## 5. Lo que no se probó

1. **Cada longitud entre 3 y 50.** Se eligieron extremos y un representante interior. Enumerar todo el intervalo aportaría poco para esta única condición de rango; los límites tienen mayor capacidad de detectar errores de comparación.
2. **El funcionamiento interno de Flask, SQLite y `date.fromisoformat`.** Se comprueba nuestro uso mediante contratos y fechas representativas, sin replicar las suites de esas bibliotecas ni enumerar todo el calendario.
3. **Autenticación y servicios de notificación.** No existen en esta API. Inventar pruebas para ellos no cubriría comportamiento del producto. Tampoco se incluye carga concurrente; queda como limitación de esta suite funcional local.

## 6. Lectura de cobertura

Ejecución en Linux con Python 3.12.14, pytest 9.1.1, pytest-cov 7.1.0 y coverage 7.16.2: **101 casos aprobados** (55 unitarios y 46 de integración). El comando y el HTML reproducible están explicados en el [README](../README.md). Resumen guardado en [cobertura.txt](cobertura.txt):

```text
Name            Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------
app.py            102      6     22      3    93%   53->55, 89, 145, 165-168
validacion.py      36      1     16      0    98%   17
-----------------------------------------------------------
TOTAL             138      7     38      3    94%
```

El criterio mide sentencias y ramas de los dos módulos propios; excluye pruebas y dependencias al seleccionar `--cov=app --cov=validacion`. Se recorrieron 131/138 sentencias y 35/38 salidas de ramas. El 94% mostrado combina ambas medidas y está redondeado. No demuestra ausencia de defectos: una línea ejecutada no implica que sus resultados estén bien comprobados.

La línea 89, respuesta genérica 500, no está cubierta. Merece una futura integración con un fallo de base controlado y propagación de excepciones desactivada, para verificar JSON y que no se expongan detalles internos. La línea 145 contempla un registro eliminado entre la consulta y el UPDATE; una prueba secuencial normal no recorre esa carrera. Se deja fuera del alcance concurrente declarado, sin presentarla como cubierta.

Las líneas 165–168 corresponden al arranque por consola; 53→55 omite configuración de pruebas. La suite usa la fábrica con configuración temporal. La línea 17 de `validacion.py` lee el reloj real: se sustituye deliberadamente para obtener determinismo. No se agregan asserts triviales solo para elevar esos porcentajes. Una medición inicial de cinco casos de especie obtuvo 71% en validación y mostró pendientes las ramas de estructura, tipos y fechas; la suite completa las recorre.

**Fuentes:** enunciado del taller de la sesión 22; [pruebas con Flask](https://flask.palletsprojects.com/en/stable/testing/); [configuración de pytest-cov](https://pytest-cov.readthedocs.io/en/latest/config.html). Se emplean los conceptos solicitados por el enunciado; no se atribuyen ejemplos a diapositivas de pruebas que no se han adjuntado. El apoyo de IA está declarado en el README. Los resultados indicados corresponden a ejecuciones realizadas durante la preparación del proyecto, no a una ejecución personal del estudiante en su equipo.
