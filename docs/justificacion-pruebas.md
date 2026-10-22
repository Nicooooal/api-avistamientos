# Justificación de las pruebas de la API de avistamientos

**Nicolás Arias Lasprilla · Ingeniería de Software 2**  
Taller de pruebas unitarias y de integración sobre la API de avistamientos.

## 1. Qué cambié en el código y por qué

Para este taller trabajé sobre la API de avistamientos que ya tenía en Python, Flask y SQLite, con el apoyo de IA que declaro en el README. El cambio principal fue separar la validación en `validacion.py`. Así puedo probar las reglas de los datos sin tener que iniciar Flask ni conectarme a la base de datos.

La función `validar_avistamiento(datos, reloj)` revisa que la especie tenga entre 3 y 50 caracteres, que la fecha exista y tenga el formato AAAA-MM-DD, y que no sea posterior a hoy. También comprueba que lugar y observador tengan texto. Antes de medir la longitud, recorta los espacios exteriores. Si encuentra un problema, devuelve un `ErrorValidacion`; si los datos son válidos, devuelve una copia con los textos recortados.

Dejé en el controlador la lectura del JSON y la respuesta HTTP: un error de validación produce 400 e identifica el campo. Para un PUT con un id inexistente se mantiene el 404. También separé el reloj: la aplicación usa `RelojSistema` y las pruebas reciben uno con una fecha fija.

Relaciono estos cambios con la **controlabilidad** y la **observabilidad** vistas en clase. Puedo controlar los datos y la fecha de cada prueba, y observar el resultado, el mensaje de error y lo que quedó guardado.

## 2. Cómo elegí los casos de prueba

La tabla inicial se preparó antes de implementar las pruebas. Después, al revisar las diapositivas, añadí las longitudes 4 y 49 para comprobar también los valores que están justo dentro del rango. En las pruebas tomé **2026-10-21** como hoy. Para comprobar una entrada inválida, mantuve válidos los demás campos.

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


Para aplicar **particiones de equivalencia**, dividí la longitud de especie en tres grupos: menos de 3, de 3 a 50 y más de 50. Luego elegí **valores límite** para revisar dónde cambia la respuesta. Por ejemplo, probar 3 y 50 permite detectar si una comparación rechaza por error los extremos permitidos. En las fechas revisé por separado el formato, si el día existe y si está en el futuro.

El resultado de pytest muestra **109 casos: 58 unitarios y 51 de integración**. Estos salen de 33 funciones de prueba, varias parametrizadas. Por ejemplo, una función combina cuatro campos con siete valores inválidos y genera 28 casos. Con vacío y espacios reviso el contenido; con null, números, booleanos, listas y objetos reviso el tipo de dato. Varias combinaciones pasan por la misma rama, pero permiten comprobar que la regla se aplique a cada campo. Tener 109 casos no significa por sí solo que las pruebas sean mejores: lo que debo justificar es qué comprueba cada grupo.

## 3. Por qué utilicé pruebas unitarias y de integración

Para los **límites de especie** usé pruebas unitarias porque puedo llamar directamente al validador y comprobar si acepta el texto o devuelve el error esperado. Si fallan, puedo revisar esa regla sin mezclarla con HTTP o SQLite.

También probé **hoy y mañana** de forma unitaria. Con el reloj fijo sé cuál debe ser el resultado cada vez. Incluí dos casos que cambian la fecha del reloj para comprobar que el validador realmente use la fecha que recibe.

Para **crear con POST y consultar con GET** usé integración. Aquí necesito comprobar que Flask, la validación y SQLite funcionen juntos. Reviso el código 201, Content-Type, Location, el id y todos los campos. Esto permite encontrar problemas que la prueba del validador no detectaría, como devolver los datos sin guardarlos o guardar un campo en la columna equivocada. En PUT inválido verifico que los datos anteriores se conserven; en DELETE, que desaparezca el registro indicado y permanezca otro.

Usé `test_client()` de Flask, permitido por el taller. Las peticiones se procesan dentro de la aplicación, sin abrir un puerto. Cada caso tiene un archivo SQLite temporal nuevo para evitar que una prueba dependa de los datos de otra. Para GET de una colección vacía espero 200 y una lista vacía, porque ese resultado es válido.

Organicé las pruebas con **AAA**: primero preparo los datos, después ejecuto la acción principal y al final verifico el resultado. Cuando hago un GET después de POST o DELETE, lo uso para comprobar el efecto. También apliqué **FIRST**: las unitarias son rápidas y no acceden a archivos; los casos son independientes, el reloj permite repetirlos y los asserts indican si pasan. Las pruebas se incorporaron durante esta ampliación de la API. Como la API base ya existía, no presento este trabajo como un desarrollo completo con TDD.

## 4. Qué doble utilicé y para qué

Utilicé `RelojFijo` como **stub**, porque entrega una fecha preparada para la prueba. El validador depende del protocolo `Reloj` y recibe la implementación desde fuera. Así aplico inversión de dependencias y puedo cambiar el reloj sin cambiar la validación. En otros casos usé `unittest.mock.Mock(spec=Reloj)` también como stub configurable: compruebo el resultado, no cuántas veces fue llamado.

Elegí este doble porque una fecha que hoy es futura dejará de serlo con el paso de los días. Si las pruebas dependieran del reloj del equipo, podrían cambiar de resultado sin haber modificado el código.

No necesité un spy ni comprobar interacciones con un mock, porque lo que me interesa es si la fecha se acepta o se rechaza. En integración mantuve SQLite real para revisar también las consultas SQL. La API no consume servicios externos, así que no tuve que simular respuestas de otra API.

## 5. Qué pruebas decidí no incluir

1. **Todas las longitudes y fechas posibles.** No es viable probar cada valor. Elegí representantes y límites de las particiones para revisar las reglas sin enumerar todas las entradas.
2. **El número exacto de llamadas al reloj.** Me interesa que la validación use la fecha recibida. Exigir una cantidad de llamadas haría que la prueba dependiera de un detalle interno que podría cambiar sin afectar el resultado.
3. **Carga y escrituras simultáneas.** En este taller me concentré en el comportamiento funcional. Comprobar peticiones concurrentes requiere otro diseño de pruebas y queda como una limitación del trabajo.

Conservé pruebas de idempotencia, persistencia y entradas con texto SQL para revisar comportamientos de la API anterior. No añadí casos únicamente para aumentar el conteo o llegar al 100 %.

## 6. Qué resultados obtuve y cómo interpreto la cobertura

Ejecuté las pruebas desde la terminal de VS Code en **Windows, con Python 3.14.6, pytest 9.1.1 y pytest-cov 7.1.0**. El resultado fue **109 passed**. En el README dejé los comandos para repetir la ejecución y abrir el reporte HTML.

```text
Name            Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------
app.py            102      6     22      3    93%   53->55, 89, 145, 165-168
validacion.py      36      1     16      0    98%   17
-----------------------------------------------------------
TOTAL             138      7     38      3    94%
```


El reporte muestra **94 % de cobertura combinada**. Se ejecutaron 131 de 138 sentencias (**94,93 %**) y 35 de 38 ramas (**92,11 %**). Distingo estos **criterios de cobertura** porque recorrer una línea no siempre significa haber probado todas sus decisiones. La medición incluye `app.py` y `validacion.py`, sin contar las pruebas ni las bibliotecas.

Al revisar lo que falta, encontré estos puntos:

- **Línea 89 de app.py:** no probé la respuesta genérica 500. Sería útil provocar un fallo controlado de base de datos para verificar que la respuesta siga siendo JSON y no exponga detalles internos. La dejo identificada como una prueba pendiente.
- **Línea 145 de app.py:** contempla que un registro desaparezca entre la consulta y el UPDATE. No cubrí esa situación de concurrencia.
- **Líneas 165–168 y rama 53→55 de app.py:** corresponden al arranque por consola y a la configuración por defecto. Las pruebas crean la aplicación con una configuración temporal.
- **Línea 17 de validacion.py:** obtiene la fecha del sistema. En las pruebas la sustituyo por el reloj fijo.

El porcentaje me sirve para localizar partes que no ejecuté, pero no demuestra que la API esté libre de errores. Una comparación incorrecta, como usar `>` en lugar de `>=`, puede pasar desapercibida si no pruebo el valor exacto del límite. Por eso considero necesario revisar tanto la cobertura como los datos y resultados que comprueba cada caso.

**Fuentes:** enunciado del taller; Jonathan Briceño, sesiones 20 (*Pruebas unitarias y dobles de prueba*) y 21 (*Pruebas II: Integración y cobertura*); [Flask: testing](https://flask.palletsprojects.com/en/stable/testing/) y [pytest-cov: configuración](https://pytest-cov.readthedocs.io/en/latest/config.html). El apoyo de IA está declarado en el README.
