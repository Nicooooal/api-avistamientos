# Taller 5. Parte 2: aplicación de arquitectura hexagonal

**Nicolás Arias Lasprilla**  
Ingeniería de Software 2 · Universidad El Bosque

**Repositorio:** https://github.com/Nicooooal/api-avistamientos  
**Rama:** main  
**Alcance:** únicamente la Parte 2. Este documento no incluye las respuestas de investigación de la Parte 1.

## 1. Arquitectura elegida y cambios

Para reorganizar la API elegí **arquitectura hexagonal**, usando los nombres núcleo, puertos y adaptadores. La idea que apliqué fue mantener las reglas dentro de la aplicación y conectar las tecnologías externas mediante adaptadores, como propone Cockburn (2005).

Apliqué el cambio a **todos los endpoints**: listar, consultar por id, crear, actualizar, eliminar y obtener el resumen por especie. Conservé Flask, SQLite, las rutas, los mensajes y el archivo de datos. Cambió la organización interna, no las operaciones que ofrece la API.

| Ubicación | Responsabilidad |
| --- | --- |
| `app.py` | Crear Flask, configurar la base, conectar los objetos y cerrar cada conexión. También conserva el arranque por consola. |
| `avistamientos/nucleo/puertos.py` | Definir `GestionAvistamientos` como puerto de entrada y `RepositorioAvistamientos` y `Reloj` como puertos de salida. |
| `avistamientos/nucleo/servicio.py` | Implementar las operaciones y coordinar la validación con el repositorio recibido. |
| `avistamientos/nucleo/validacion.py` | Conservar las reglas de especie, fecha y campos obligatorios. |
| `avistamientos/adaptadores/http.py` | Traducir peticiones a llamadas al núcleo y resultados o errores a respuestas HTTP. |
| `avistamientos/adaptadores/sqlite.py` | Implementar persistencia, consultas SQL y conversión de filas a diccionarios. |
| `avistamientos/adaptadores/reloj.py` | Implementar el reloj del sistema. |
| `validacion.py` | Reexportar los nombres anteriores para mantener compatibles las pruebas existentes; no duplica reglas. |
| `tests/` | Conservar las 109 pruebas anteriores y añadir tres comprobaciones del núcleo. |
| `docs/` | Mantener la justificación del taller anterior y este documento de la Parte 2. |

Dentro de `avistamientos/`, las carpetas `nucleo/` y `adaptadores/` son paquetes de Python y tienen su `__init__.py`. También se mantienen los archivos de dependencias, `pytest.ini`, `.gitignore` y los ejemplos JSON del README.

<!-- pagebreak -->

## 2. Dirección de las dependencias

Las flechas del diagrama muestran **dependencias del código**, no el orden de una petición. El núcleo no importa Flask, Werkzeug, sqlite3 ni los adaptadores. `app.py` está fuera del núcleo y conoce las implementaciones para conectarlas.

```mermaid
flowchart TB
    H["Adaptador HTTP / Flask"] --> S
    Q["Adaptador SQLite"] --> P
    T["Adaptador reloj del sistema"] --> P
    Q --> V
    subgraph N["Núcleo de avistamientos"]
        S["ServicioAvistamientos"] --> P["Puertos: gestión, repositorio y reloj"]
        S --> V["Validación y campos"]
        V --> P
    end
```

El adaptador HTTP utiliza el puerto `GestionAvistamientos`; también conoce los errores del núcleo para traducirlos a 400 o 404. SQLite implementa `RepositorioAvistamientos` y usa la lista de campos del núcleo. El reloj del sistema implementa `Reloj`. Ninguna dependencia vuelve desde el núcleo hacia esos adaptadores.

Por ejemplo, al crear un registro, HTTP lee el JSON y llama a `crear`. El servicio valida y pide guardar al repositorio que recibió. En ejecución ese objeto es `RepositorioSQLite`, pero el servicio no importa esa clase. La respuesta cruza el límite como un diccionario normal, sin objetos de Flask ni `sqlite3.Row`.

### Evolución en el mismo repositorio

Los cambios se dividieron en pasos comprobados, sin crear otro repositorio:

1. [ccfd4af](https://github.com/Nicooooal/api-avistamientos/commit/ccfd4af290584f8344c3b1276615dbc02b4dcdf8): mover validación y reloj; las 109 pruebas siguen pasando.
2. [84ca66b](https://github.com/Nicooooal/api-avistamientos/commit/84ca66bb717aba31a56fd7a3da30ded6f7c1c27a): incorporar puertos, servicio, adaptador SQLite y tres pruebas nuevas. En este paso todavía se conserva la conexión HTTP anterior.
3. [3290c11](https://github.com/Nicooooal/api-avistamientos/commit/3290c11aa38f21f1b218b91805ba3c1ef937602c): conectar todos los endpoints al servicio y dejar `app.py` como composición y arranque.
4. Un commit posterior incorpora este informe y actualiza los comandos del README.

### Comprobaciones añadidas

Añadí un recorrido de creación, consulta, actualización, resumen y borrado con un repositorio en memoria; una comprobación de que los datos inválidos no se guardan; y una ejecución en un proceso limpio que bloquea las importaciones externas. Esta última permite comprobar que el núcleo realmente funciona sin Flask ni SQLite. El repositorio en memoria es un **fake de pruebas**, no una nueva opción de almacenamiento para el usuario.

<!-- pagebreak -->

## 3. Evidencia antes del refactor

Tomé como punto de partida el commit [e1c4a37](https://github.com/Nicooooal/api-avistamientos/commit/e1c4a37802ca52fee0be60714ae0886645cc0293). Las pruebas pasaron antes de reorganizar el código; no fue necesario corregir un fallo previo.

Las mediciones de este informe se ejecutaron en el entorno Linux de apoyo, con Python 3.12.14, pytest 9.1.1 y pytest-cov 7.1.0. No las presento como nuevas capturas de mi equipo Windows. El apoyo de ChatGPT/Codex está declarado en el README.

Comando de medición, usando el Python del entorno virtual:

```bash
python -m pytest --cov=app --cov=validacion --cov-branch --cov-report=term-missing
```

Salida de la ejecución (se omiten únicamente la ruta local de trabajo y la línea de exportación auxiliar JSON):

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.1.1, pluggy-1.7.0
configfile: pytest.ini
testpaths: tests
plugins: cov-7.1.0
collected 109 items

tests/test_api.py ...................................................    [ 46%]
tests/test_validacion.py ............................................... [ 89%]
...........                                                              [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.14-final-0 _______________

Name            Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------
app.py            102      6     22      3    93%   53->55, 89, 145, 165-168
validacion.py      36      1     16      0    98%   17
-----------------------------------------------------------
TOTAL             138      7     38      3    94%
============================= 109 passed in 0.51s ==============================
```

El resultado fue **109 pruebas aprobadas y 94 % de cobertura combinada de sentencias y ramas**. En esta versión todo el código de producción medido estaba en `app.py` y `validacion.py`.

Para reproducir el antes sin perder la versión actual, se puede crear una carpeta de trabajo separada desde un clon del mismo repositorio:

```bash
git worktree add --detach ../avistamientos-antes e1c4a37802ca52fee0be60714ae0886645cc0293
```

Después se abre esa carpeta, se crea su entorno virtual y se instalan las dependencias siguiendo el README. Este comando no crea un repositorio de entrega distinto: permite ejecutar una revisión histórica del mismo proyecto.

<!-- pagebreak -->

## 4. Evidencia después del refactor

Primero ejecuté **las mismas 109 pruebas**, conservando sin modificaciones `tests/test_api.py`, `tests/test_validacion.py` y `tests/conftest.py`. Añadí `--cov=avistamientos` para que la medición incluya los módulos que ahora contienen la implementación. Medir solo los dos archivos anteriores habría dejado fuera gran parte del código.

```bash
python -m pytest tests/test_api.py tests/test_validacion.py --cov=app --cov=validacion --cov=avistamientos --cov-branch --cov-report=term-missing
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.1.1, pluggy-1.7.0
configfile: pytest.ini
plugins: cov-7.1.0
collected 109 items

tests/test_api.py ...................................................    [ 46%]
tests/test_validacion.py ............................................... [ 89%]
...........                                                              [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.14-final-0 _______________

Name                                    Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------
app.py                                     31      4      8      3    82%   20->22, 28->30, 43-46
avistamientos/__init__.py                   0      0      0      0   100%
avistamientos/adaptadores/__init__.py       0      0      0      0   100%
avistamientos/adaptadores/http.py          53      1      2      0    98%   36
avistamientos/adaptadores/reloj.py          5      1      0      0    80%   8
avistamientos/adaptadores/sqlite.py        46      1      6      1    96%   69
avistamientos/nucleo/__init__.py            0      0      0      0   100%
avistamientos/nucleo/puertos.py             6      0      0      0   100%
avistamientos/nucleo/servicio.py           31      1      6      1    95%   36
avistamientos/nucleo/validacion.py         31      0     16      0   100%
validacion.py                               4      0      0      0   100%
-----------------------------------------------------------------------------------
TOTAL                                     207      8     38      5    95%
============================= 109 passed in 0.54s ==============================
```

Después ejecuté la suite completa, incluyendo las tres comprobaciones nuevas:

```text
collected 112 items
tests/test_api.py ...................................................    [ 45%]
tests/test_nucleo.py ...                                                 [ 48%]
tests/test_validacion.py ............................................... [ 90%]
============================= 112 passed in 0.64s ==============================
```

La suite completa produce el mismo total de cobertura: **207 sentencias, 8 sin ejecutar, 38 ramas, 5 parcialmente cubiertas y 95 % combinado**. Que aumente de 94 % a 95 % no demuestra por sí solo una mejora: también cambió el número de sentencias al separar responsabilidades.

Quedan sin cubrir el manejo genérico del error 500, el reloj real, parte del arranque y configuración y el caso en que el registro desaparece antes de terminar una actualización. Las líneas exactas figuran en `Missing`. El núcleo de validación alcanza el 100 %, pero eso tampoco garantiza ausencia de defectos.

<!-- pagebreak -->

## 5. Muestra de que la API responde igual

Comparé 43 respuestas de ambas versiones con la misma fecha fija y bases temporales nuevas. Coincidieron código HTTP, JSON, texto del cuerpo, Content-Type, Location y los métodos de Allow. La comparación incluyó CRUD, resumen, datos inválidos, cuerpos mal formados o excesivos y errores 404 y 405. No implica haber probado todas las peticiones posibles.

Esta es una muestra del recorrido ejecutado en las dos versiones:

| Petición | Antes | Después |
| --- | --- | --- |
| GET `/avistamientos` al iniciar | 200 y `[]` | 200 y `[]` |
| POST `/avistamientos` con datos válidos | 201, id 1 y Location `/avistamientos/1` | Igual |
| GET `/avistamientos/1` | 200 y registro completo | Igual |
| PUT `/avistamientos/1`, lugar Humedal | 200, mismo id y lugar actualizado | Igual |
| GET `/avistamientos/resumen` | 200, colibrí: 1 | Igual |
| PUT `/avistamientos/1`, especie ab | 400 y mensaje del límite | Igual |
| DELETE `/avistamientos/1` | 200 y confirmación | Igual |
| GET `/avistamientos/1` después de borrar | 404 y Avistamiento no encontrado. | Igual |

En el POST se enviaron especie `colibrí`, lugar `Bogotá`, fecha `2026-10-21` y observador `Nicolás`. El cuerpo exacto obtenido en ambas versiones fue:

```json
{"id":1,"especie":"colibrí","lugar":"Bogotá","fecha":"2026-10-21","observador":"Nicolás"}
```

También se comprobó el arranque real con `python app.py --port 40269` y una consulta HTTP por red local: GET `/avistamientos` respondió 200, `application/json` y `[]`. El puerto fue temporal; el uso normal sigue siendo el 5000.

## 6. Qué fue lo más difícil de separar

Lo más delicado fue conservar el comportamiento de PUT mientras separaba HTTP, validación y persistencia. Antes se consultaba si existía el id **antes de leer el cuerpo**. Si movía toda la lectura al principio, un id inexistente con JSON mal formado habría pasado de responder 404 a responder 400.

Por eso el adaptador HTTP consulta primero mediante el servicio y después lee el JSON. El servicio vuelve a comprobar la existencia al actualizar para que la operación también sea válida cuando se invoque desde otro adaptador. Esa consulta adicional es un costo concreto de esta solución sencilla; no garantiza por sí sola protección contra todas las carreras concurrentes.

También separé el manejo de conexiones de las reglas. SQLite conserva el SQL y sus límites numéricos; `app.py` se encarga de la conexión por contexto y de cerrarla. Así el núcleo puede trabajar con un repositorio en memoria, mientras las pruebas de integración siguen usando SQLite real. El costo es tener más archivos y contratos para una API pequeña.

<!-- pagebreak -->

## 7. Cómo ejecutar y verificar la entrega

En VS Code, abre la carpeta del proyecto y selecciona **Terminal > Nueva terminal**. Si trabajas desde el clon existente, actualízalo con `git pull --ff-only`. Si descargaste ZIP, descarga y extrae la versión nueva; esa carpeta no admite `git pull`.

En Windows, crea el entorno solo si todavía no existe:

```powershell
py -m venv .venv
```

Instala las dependencias y ejecuta las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
```

El resultado esperado es **112 passed**: las 109 anteriores más las tres nuevas. Para generar cobertura, ejecuta esta línea completa:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov=validacion --cov=avistamientos --cov-branch --cov-report=term-missing --cov-report=html
```

Abre `htmlcov/index.html` desde el explorador de archivos. Para iniciar la API:

```powershell
.\.venv\Scripts\python.exe app.py
```

Deja esa terminal abierta. En otra terminal del proyecto, consulta:

```powershell
curl.exe -i http://127.0.0.1:5000/avistamientos
```

Si la base está vacía verás `[]`; si ya tenías registros, verás esos datos. El refactor no borra la base existente. Los ejemplos de POST, PUT y DELETE siguen en el README.

En macOS o Linux crea el entorno con `python3 -m venv .venv`, sustituye `.\.venv\Scripts\python.exe` por `./.venv/bin/python` en los comandos y usa `curl` en lugar de `curl.exe`.

### Referencia de la arquitectura aplicada

Cockburn, A. (2005). *Hexagonal architecture*. https://alistair.cockburn.us/hexagonal-architecture/

La organización y las decisiones descritas corresponden a esta implementación. Esta referencia sustenta el enfoque de puertos y adaptadores; las respuestas de investigación de la Parte 1 quedan fuera del alcance solicitado.
