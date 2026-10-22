# Justificación de las pruebas de la API de avistamientos

**Nicolás Arias Lasprilla · Ingeniería de Software 2**  
Taller de pruebas unitarias y de integración sobre la API de avistamientos.

## 1. Qué cambió en el código

La validación se extrajo de la petición de Flask a `validacion.py`. La función `validar_avistamiento(datos, reloj)` recibe datos y devuelve una copia normalizada o un `ErrorValidacion`. Comprueba especie de 3 a 50 caracteres, fecha real en formato AAAA-MM-DD no posterior a hoy, y lugar y observador no vacíos. La longitud se evalúa después de recortar espacios.

El controlador lee el JSON y convierte el error de validación en HTTP 400, indicando el campo. Se conserva el 404 cuando PUT recibe un identificador inexistente. El reloj también se separó: `RelojSistema` obtiene la fecha local y las pruebas inyectan un reloj fijo.

Esto mejora la **controlabilidad** porque se pueden fijar entradas y fecha; mejora la **observabilidad** porque se comprueban resultados, errores y datos persistidos. La regla se prueba sin crear una aplicación Flask ni acceder a SQLite.

## 2. Casos elegidos: particiones y valores límite

La tabla inicial se preparó antes de implementar la suite; los vecinos 4 y 49 se añadieron al revisar las diapositivas. Se fija hoy en **2026-10-21**. En cada caso, los demás campos son válidos.

| Entrada | Tipo de caso | Resultado y motivo |
| --- | --- | --- |
| Especie `ab` (2) | Límite inválido | Error especie: justo debajo del mínimo. |
| Especie `abc` (3) | Límite válido | Aceptar: mínimo incluido. |
| Especie de 4 caracteres | Vecino interior | Aceptar: inmediatamente después del mínimo. |
| Especie `colibrí` (7) | Representativo válido | Aceptar: interior de la partición permitida. |
| Especie de 49 caracteres | Vecino interior | Aceptar: inmediatamente antes del máximo. |
| Especie de 50 caracteres | Límite válido | Aceptar: máximo incluido. |
| Especie de 51 caracteres | Límite inválido | Error especie: justo encima del máximo. |
| Especie `  abc  ` | Normalización | Devolver `abc`; medir el texto recortado. |
| Fecha 2026-10-20 | Límite válido: ayer | Aceptar: vecino anterior a hoy. |
| Fecha 2026-10-21 | Límite válido: hoy | Aceptar: último día permitido. |
| Fecha 2026-10-22 | Límite inválido: mañana | Error fecha: primer día prohibido. |
| Fecha 2026-11-21 | Representativo futuro | Error fecha: interior de la partición futura. |
| Fecha 2024-02-29 | Representativo válido | Aceptar: día bisiesto real y pasado. |
| 2025-02-29, 2026-02-30, 0000-01-01 | Calendario inválido | Error fecha: el formato no garantiza que exista. |
| `21/10/2026`, `2026-1-21`, `texto` | Formato inválido | Error fecha: separador, ancho o estructura incorrectos. |
| Campos vacíos o con espacios | Contenido inválido | Identificar el campo, especialmente lugar y observador. |
| Campo ausente o no textual | Contrato inválido | Identificar el campo faltante o con tipo incorrecto. |
| Cuerpo no objeto o campos adicionales | Estructura inválida | Rechazar entradas fuera del contrato. |

La **partición de equivalencia** divide especie en menos de 3, entre 3 y 50, y más de 50 caracteres. Los **valores límite** detectan errores como excluir 3 o 50 mediante una comparación incorrecta. En fecha se distinguen formato, existencia y relación con hoy: son causas distintas de rechazo.

La suite tiene **33 funciones que generan 109 casos parametrizados**: 58 unitarios y 51 de integración. Por ejemplo, una función combina cuatro campos con siete valores inválidos y produce 28 casos. Vacío y espacios comprueban normalización; null, número, booleano, lista y objeto comprueban tipos JSON. Las combinaciones detectan diferencias accidentales entre campos, aunque varias recorren la misma rama. No se consideran 28 comportamientos independientes ni evidencia de mayor calidad.

## 3. Por qué cada nivel

**Límites de especie:** son unitarias porque llaman directamente al validador. Comprueban aceptación o error exacto, aislando la regla de posibles fallos de HTTP y SQL.

**Hoy y mañana:** también son unitarias. El stub fija la referencia temporal; dos casos adicionales cambian esa referencia para comprobar que el validador utiliza el reloj recibido.

**POST seguido de GET:** es integración porque recorre Flask, validación, escritura y lectura en SQLite. Comprueba 201, Content-Type, Location, id y todos los valores. Detectaría un campo guardado en otra columna, una escritura omitida o una respuesta HTTP incorrecta, defectos que la unitaria no puede observar. PUT inválido comprueba que los datos anteriores permanezcan; DELETE verifica que el recurso desaparezca y otro registro se conserve.

Se usa `test_client()`, autorizado por el taller: ejercita la interfaz HTTP dentro del proceso, sin abrir un puerto TCP. SQLite es el mismo motor de la aplicación, con un archivo temporal nuevo por caso. GET de colección vacía devuelve 200; no se inventa un error 400 donde no aplica.

Las pruebas tienen nombres de comportamiento y **AAA** visible: preparar, realizar una acción principal y verificar. Los GET posteriores observan el efecto de esa acción. **FIRST** orienta su diseño: unitarias rápidas sin I/O, datos independientes, reloj repetible y asserts autoverificables; se escribieron junto con esta ampliación, aunque la API base ya existía. No se afirma haber seguido TDD.

## 4. Qué doble se utilizó y por qué

`RelojFijo` es un **stub**: devuelve una fecha preparada. El validador depende del protocolo `Reloj` y recibe su implementación desde fuera, aplicando inversión de dependencias. También se utiliza `unittest.mock.Mock(spec=Reloj)` como stub configurable: no se verifican llamadas, sino resultados.

Sin este doble, una fecha escrita como mañana dejaría de ser futura al ejecutar la prueba otro día. No se necesita un spy o mock de interacciones porque consultar el reloj no es el comportamiento de negocio que se quiere observar. No se reemplaza SQLite por un fake en integración: se perdería la comprobación del SQL real. La API no consume servicios externos.

## 5. Qué pruebas se decidió no escribir

1. **Todas las longitudes y fechas posibles.** Las pruebas exhaustivas no son viables. Los representantes y límites cubren las particiones relevantes sin enumerar el dominio.
2. **El número exacto de consultas al reloj.** Se verifica la decisión según la fecha recibida; exigir una llamada concreta acoplaría la prueba a una implementación que puede cambiar sin alterar el resultado.
3. **Carga y escrituras concurrentes.** La suite comprueba comportamiento funcional local. Las carreras entre peticiones requieren otro diseño de pruebas y quedan como limitación explícita.

Se conservan regresiones de idempotencia, persistencia y entrada SQL porque protegen comportamientos existentes. No se añaden casos solo para aumentar la cantidad o alcanzar 100% de cobertura.

## 6. Reporte y lectura de cobertura

La ejecución local en **Windows, Python 3.14.6, pytest 9.1.1 y pytest-cov 7.1.0** terminó con **109 passed**. Coincide con el resultado obtenido en Linux. El README contiene el comando reproducible y la forma de abrir el reporte HTML.

```text
Name            Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------
app.py            102      6     22      3    93%   53->55, 89, 145, 165-168
validacion.py      36      1     16      0    98%   17
-----------------------------------------------------------
TOTAL             138      7     38      3    94%
```

El **criterio de cobertura** determina qué se cuenta: se ejecutaron 131/138 sentencias (**94,93%**) y 35/38 ramas (**92,11%**). El **94%** de la herramienta combina ambos criterios y redondea. Solo se miden `app.py` y `validacion.py`, no las pruebas ni las bibliotecas.

La línea 89, respuesta genérica 500, queda pendiente. Sí aportaría una integración con un fallo de base controlado para comprobar JSON y ausencia de detalles internos. La línea 145 contempla una eliminación entre consulta y UPDATE; requiere estudiar concurrencia y queda fuera del alcance declarado. El arranque por consola (165–168), la configuración por defecto (53→55) y el reloj real (validacion.py:17) tampoco se recorren en esta suite: se usan fábrica, configuración temporal y stub.

La cobertura identifica huecos, pero no demuestra que se hayan elegido buenas entradas. Un error `>` en lugar de `>=` puede sobrevivir con cobertura alta; por eso se comprueban los límites. Las decisiones pendientes se explican, sin presentar las pruebas verdes como garantía de ausencia de defectos.

**Fuentes:** enunciado del taller; Jonathan Briceño, sesiones 20 (*Pruebas unitarias y dobles de prueba*) y 21 (*Pruebas II: Integración y cobertura*); [Flask: testing](https://flask.palletsprojects.com/en/stable/testing/) y [pytest-cov: configuración](https://pytest-cov.readthedocs.io/en/latest/config.html). El apoyo de IA está declarado en el README.
