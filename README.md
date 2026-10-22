# API REST de avistamientos de aves

Proyecto individual de Ingeniería de Software 2: API de la sesión 17 y taller de pruebas de la sesión 22.

La parte D del taller está en [docs/justificacion-pruebas.md](docs/justificacion-pruebas.md), con la tabla de casos, las decisiones y el reporte de cobertura.

**Autor:** Nicolas Arias Lasprilla

Esta API permite registrar, consultar, actualizar y eliminar avistamientos de aves. Está desarrollada con Python, Flask y SQLite. Los datos se guardan en un archivo local y se conservan al reiniciar la aplicación.

Sigue estos pasos para ejecutarla en **Windows, macOS o Linux**. Los comandos se escriben en la terminal; los archivos se abren desde el explorador de VS Code.

## 1. Preparar las herramientas

Necesitas Python 3.10 o posterior con pip y sqlite3, y conexión a internet para descargar las dependencias. Para seguir los pasos con el editor, instala [Visual Studio Code](https://code.visualstudio.com/). También puedes ejecutar los mismos comandos desde la terminal del sistema.

- **Windows:** instala Python desde [python.org](https://www.python.org/downloads/). Si el instalador ofrece añadir Python al PATH, marca esa opción. Abre PowerShell y ejecuta `py --version`. Si no reconoce el comando, prueba `python --version`.
- **macOS:** instala Python 3 desde [python.org](https://www.python.org/downloads/macos/). Abre Terminal y ejecuta `python3 --version`.
- **Linux:** ejecuta `python3 --version` en la terminal. Si falta Python, pip o venv, instálalos con el administrador de paquetes de tu distribución. En Ubuntu o Debian puedes usar:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip curl git
```

Comprueba que la versión de Python sea 3.10 o posterior. Cierra y vuelve a abrir VS Code si instalaste las herramientas mientras estaba abierto.

Para las pruebas manuales, comprueba curl con `curl.exe --version` en Windows o `curl --version` en macOS/Linux. Si falta, instálalo desde [curl](https://curl.se/download.html) o con el administrador de paquetes del sistema.

SQLite no necesita un servidor separado. Al iniciar la API se crean automáticamente el archivo `data/avistamientos.db` y su tabla.

## 2. Descargar y abrir el proyecto

Elige una de estas dos opciones.

### Opción A: descargar desde GitHub sin usar Git

1. Abre [el repositorio](https://github.com/Nicooooal/api-avistamientos).
2. Haz clic en **Code** y luego en **Download ZIP**.
3. Extrae el ZIP. En Windows, haz clic derecho sobre el archivo y selecciona **Extraer todo**; en macOS, haz doble clic; en Linux, utiliza la opción de extraer de tu gestor de archivos.
4. Abre VS Code y selecciona **Archivo > Abrir carpeta** (**File > Open Folder**).
5. Selecciona la carpeta extraída que contiene directamente `app.py`, `requirements.txt` y `README.md`. Si descargaste el ZIP desde GitHub, normalmente se llama `api-avistamientos-main`.

### Opción B: clonar con Git

Instala [Git](https://git-scm.com/downloads) si todavía no está disponible. Abre una terminal en la carpeta donde quieras guardar el proyecto y ejecuta una línea a la vez:

```bash
git clone https://github.com/Nicooooal/api-avistamientos.git
cd api-avistamientos
```

Después, en VS Code, selecciona **Archivo > Abrir carpeta** y abre esa carpeta `api-avistamientos`.

### Abrir la terminal del proyecto

1. En VS Code, haz clic en **Terminal > Nueva terminal** (**Terminal > New Terminal**).
2. En Windows, selecciona **PowerShell** en el menú de perfiles junto al botón `+`. En macOS/Linux utiliza bash o zsh.
3. Comprueba que estás en la carpeta correcta: ejecuta `dir` en Windows o `ls` en macOS/Linux. Deben aparecer `app.py` y `requirements.txt`.

Ejecuta todos los comandos siguientes desde esa carpeta. Si ya tienes el proyecto abierto, continúa con el paso 3.

## 3. Instalar y ejecutar la API

Usa únicamente el bloque correspondiente a tu sistema operativo. Ejecuta cada comando y espera a que termine antes de escribir el siguiente.

### Windows: PowerShell

Primero, crea el entorno virtual:

```powershell
py -m venv .venv
```

Si el comando disponible en tu equipo es `python`, usa `python -m venv .venv` en ese primer paso.

Luego, instala las dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Por último, inicia la API:

```powershell
.\.venv\Scripts\python.exe app.py
```

Estos comandos también funcionan en CMD. No es necesario ejecutar un script de activación del entorno.

### macOS y Linux: bash o zsh

Primero, crea el entorno virtual:

```bash
python3 -m venv .venv
```

Luego, instala las dependencias:

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

Por último, inicia la API:

```bash
./.venv/bin/python app.py
```

### Comprobar que está funcionando

1. Busca en la terminal el mensaje `Running on http://127.0.0.1:5000`.
2. Deja esa terminal abierta: allí está funcionando el servidor.
3. Abre el navegador y entra a [http://127.0.0.1:5000/avistamientos](http://127.0.0.1:5000/avistamientos).
4. Si la base es nueva, verás `[]`. Significa que la consulta funcionó y todavía no hay registros.
5. Para crear, actualizar y eliminar registros, sigue los ejemplos del paso 6.

El aviso de servidor de desarrollo de Flask es normal en esta ejecución local. La dirección raíz `http://127.0.0.1:5000/` devuelve 404 porque no tiene una ruta definida.

Para detener la API, vuelve a su terminal y pulsa **Ctrl+C**. Para arrancarla otro día, abre la misma carpeta y ejecuta únicamente el comando de inicio de tu sistema; no necesitas instalar todo de nuevo.

### Seleccionar el intérprete en VS Code (opcional)

1. Haz clic en **Extensiones**, busca **Python** y selecciona **Instalar** en la extensión de Microsoft.
2. Abre **Ver > Paleta de comandos** (**View > Command Palette**).
3. Busca **Python: Select Interpreter** y selecciona el intérprete de `.venv`.
4. Si no aparece, elige la opción para introducir una ruta y selecciona `.venv\Scripts\python.exe` en Windows o `.venv/bin/python` en macOS/Linux.

## 4. Modelo y validaciones

| Campo | Tipo JSON | Regla |
| --- | --- | --- |
| `id` | Número entero | Lo genera SQLite. No se envía en POST ni en el cuerpo de PUT. |
| `especie` | Texto | Entre 3 y 50 caracteres después de recortar espacios exteriores. |
| `lugar` | Texto | Obligatorio y no vacío. |
| `fecha` | Texto | Fecha real en formato `AAAA-MM-DD`, no posterior a hoy según la fecha local del servidor. |
| `observador` | Texto | Obligatorio y no vacío. |

POST y PUT reciben un objeto JSON con los cuatro campos editables y `Content-Type: application/json`. Se recortan los espacios exteriores. Los campos adicionales, valores nulos, tipos incorrectos, fechas imposibles y cuerpos mal formados producen 400. El máximo de cuerpo es 64 KiB; al superarlo se responde 413.

PUT reemplaza **todos los campos editables** de un registro existente y conserva su `id`. No es una actualización parcial ni crea registros. Si el identificador no existe devuelve 404. PATCH no se implementa porque el taller no lo pide; devuelve 405.

## 5. Endpoints

URL base: `http://127.0.0.1:5000`.

| Método | Ruta | Respuesta |
| --- | --- | --- |
| GET | `/avistamientos` | 200 y lista JSON, incluso si está vacía. |
| GET | `/avistamientos/{id}` | 200 y objeto; 404 si no existe. |
| POST | `/avistamientos` | 201 y objeto creado; 400 si los datos son inválidos. |
| PUT | `/avistamientos/{id}` | 200 y objeto actualizado; 404 si no existe; 400 si los datos son inválidos. |
| DELETE | `/avistamientos/{id}` | 200 y confirmación JSON; 404 si no existe. |
| GET | `/avistamientos/resumen` | 200 y cantidad de registros por especie. Bonus. |

Se eligió 200 para DELETE para incluir una confirmación JSON. También habría sido válido 204 sin cuerpo, según el enunciado. Los errores tienen la forma `{"error": "Descripción del problema."}`. Las rutas se usan sin barra final.

El resumen agrupa por el nombre exacto después de recortar espacios exteriores. `colibrí`, `Colibrí` y `colibri` son textos distintos. No se realiza una clasificación biológica ni una corrección de nombres.

## 6. Ejemplos completos con curl

1. Deja abierta la terminal que ejecuta la API.
2. Haz clic en **Terminal > Nueva terminal**, o en el botón `+` del panel de terminales.
3. Comprueba con `dir` (Windows) o `ls` (macOS/Linux) que esta segunda terminal también está en la carpeta donde se encuentra `app.py`.
4. Ejecuta los ejemplos siguientes en orden, uno por uno.

**En Windows, cambia la primera palabra `curl` por `curl.exe` en cada comando. En macOS/Linux, copia los comandos tal como aparecen.** Por ejemplo, la primera consulta en Windows es:

```powershell
curl.exe -i --max-time 10 http://127.0.0.1:5000/avistamientos
```

Los archivos JSON ya vienen incluidos en `ejemplos/`. `--data-binary "@archivo"` lee el contenido del archivo; `-i` permite ver el código HTTP y las cabeceras. Se incluye un límite de espera de 10 segundos.

### 6.1. Listar

```bash
curl -i --max-time 10 http://127.0.0.1:5000/avistamientos
```

Esperado en una base nueva: **200 OK** y `[]`.

### 6.2. Crear

```bash
curl -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/crear.json"
```

Esperado: **201 CREATED**, cabecera `Location: /avistamientos/1` y un objeto como este:

```json
{
  "id": 1,
  "especie": "colibrí",
  "lugar": "Jardín Botánico de Bogotá",
  "fecha": "2026-09-29",
  "observador": "Nicolás"
}
```

**El id 1 es solo el ejemplo de una base nueva.** Usa el `id` real que devuelva POST en todas las peticiones siguientes. Los datos son ficticios para probar el ejercicio; no representan avistamientos verificados.

### 6.3. Consultar uno

```bash
curl -i --max-time 10 http://127.0.0.1:5000/avistamientos/1
```

Esperado: **200 OK** y el objeto creado.

### 6.4. Reemplazar sus datos

```bash
curl -i --max-time 10 -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" --data-binary "@ejemplos/actualizar.json"
```

Esperado: **200 OK**, el mismo `id`, lugar `Humedal Santa María del Lago` y fecha `2026-09-30`. El archivo contiene los cuatro campos editables, aunque solo cambien dos. Repetir este mismo PUT conserva el mismo estado.

### 6.5. Resumen por especie

```bash
curl -i --max-time 10 http://127.0.0.1:5000/avistamientos/resumen
```

Esperado si solamente creaste el registro anterior:

```json
[{"especie": "colibrí", "cantidad": 1}]
```

Para observar un conteo de 2, ejecuta de nuevo el POST. Cada POST crea un registro nuevo. Un PUT no aumenta el total.

### 6.6. Datos incompletos: 400

```bash
curl -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/incompleto.json"
```

Esperado: **400 BAD REQUEST** y un error que identifica los campos faltantes.

Para comprobar una fecha imposible:

```bash
curl -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/fecha_invalida.json"
```

Esperado: **400 BAD REQUEST**. Estos errores no deben guardar registros.

### 6.7. Eliminar

```bash
curl -i --max-time 10 -X DELETE http://127.0.0.1:5000/avistamientos/1
```

Esperado: **200 OK** y `{"mensaje": "Avistamiento eliminado.", "id": 1}`.

### 6.8. Verificar 404 después de eliminar

```bash
curl -i --max-time 10 http://127.0.0.1:5000/avistamientos/1
curl -i --max-time 10 -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" --data-binary "@ejemplos/actualizar.json"
curl -i --max-time 10 -X DELETE http://127.0.0.1:5000/avistamientos/1
```

Esperado: **404 NOT FOUND** en los tres casos. El segundo DELETE no cambia el estado: el recurso sigue ausente.

## 7. Ejecutar pruebas y generar cobertura

Abre **Terminal > Nueva terminal** en VS Code, dentro de la carpeta del proyecto. Instala las herramientas de pruebas una vez; este archivo incluye también Flask.

Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
```

macOS/Linux:

```bash
./.venv/bin/python -m pip install -r requirements-dev.txt
./.venv/bin/python -m pytest -v
```

Se esperan **109 casos aprobados**: 58 casos unitarios y 51 de integración, incluyendo las combinaciones parametrizadas. Cada función de prueba contiene comentarios Arrange, Act y Assert. La cantidad no es el criterio de calidad; la selección se explica en el documento de justificación.

Para ejecutar un solo nivel, añade `tests/test_validacion.py` (unitarias) o `tests/test_api.py` (integración) después de `pytest`.

Las pruebas no necesitan un servidor encendido. Las de integración usan `test_client()` de Flask y una base SQLite temporal nueva por caso. El reloj fijo devuelve 2026-10-21; la ejecución normal de la API utiliza la fecha local del sistema. Las pruebas no modifican `data/avistamientos.db`.

Genera cobertura de líneas y ramas en Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov=validacion --cov-branch --cov-report=term-missing --cov-report=html
```

En macOS/Linux:

```bash
./.venv/bin/python -m pytest --cov=app --cov=validacion --cov-branch --cov-report=term-missing --cov-report=html
```

Al terminar, revisa el resumen de la terminal. Para abrir el detalle, entra a la carpeta `htmlcov` desde el explorador de archivos del sistema y abre `index.html` con el navegador. La columna Missing señala líneas y ramas no recorridas. El resumen de referencia y su interpretación están en la sección 6 de [la justificación](docs/justificacion-pruebas.md). El reporte HTML se genera localmente y no se sube a Git.

Para comprobar la persistencia manualmente: crea un registro, anota su id, detén el servidor con Ctrl+C, vuelve a iniciarlo y consulta ese id antes de eliminarlo.

## 8. Resolver problemas de ejecución

| Mensaje o situación | Qué hacer |
| --- | --- |
| No se encuentra `app.py` o `requirements.txt` | Abre en VS Code la carpeta que contiene esos archivos y crea una terminal nueva. |
| `py` no se reconoce en Windows | Prueba `python --version`. Si funciona, usa `python -m venv .venv`. Si tampoco funciona, revisa la instalación de Python y vuelve a abrir la terminal. |
| `No module named venv` o error con ensurepip en Linux | Instala el paquete de venv correspondiente a tu Python. En Ubuntu/Debian, usa los paquetes del paso 1 y vuelve a crear el entorno. |
| `No module named flask` | Ejecuta otra vez el comando de instalación del paso 3 y arranca con el Python de `.venv`. |
| curl no puede conectarse | Revisa que la terminal del servidor siga abierta y que la URL use el puerto mostrado al arrancar. |
| curl no encuentra el archivo JSON | Ejecuta la petición desde la carpeta que contiene `ejemplos/`. |
| Respuesta 404 al consultar un registro | Usa el id que devolvió POST. Un registro eliminado ya no se puede consultar. |
| El puerto 5000 está ocupado | Detén la otra instancia o inicia la API en el puerto 5001 como se muestra a continuación. |

Para usar otro puerto en Windows:

```powershell
.\.venv\Scripts\python.exe app.py --port 5001
```

En macOS/Linux:

```bash
./.venv/bin/python app.py --port 5001
```

Después cambia `5000` por `5001` en la dirección del navegador y en todos los comandos curl.

## 9. Archivos del proyecto

| Archivo | Función |
| --- | --- |
| `app.py` | Adaptación HTTP, conexión SQLite, creación de tabla y endpoints. |
| `validacion.py` | Regla de negocio, error de validación e interfaz del reloj. |
| `requirements-dev.txt` | Herramientas de pruebas y cobertura. |
| `tests/test_validacion.py` | Pruebas unitarias de particiones y límites. |
| `tests/conftest.py` | Reloj fijo y fixtures con base temporal por caso. |
| `docs/justificacion-pruebas.md` | Decisiones de pruebas y lectura de cobertura de la sesión 22. |
| `requirements.txt` | Versión de Flask usada. Pip resuelve sus dependencias. |
| `tests/test_api.py` | Pruebas de integración. |
| `ejemplos/*.json` | Cuerpos para las peticiones curl. |
| `.gitignore` | Excluye entorno virtual, datos locales y archivos temporales. |

## 10. Uso de IA y fuentes

- **Herramienta utilizada:** ChatGPT, modo Codex, de OpenAI.
- **Modelo exacto:** GPT 6 Astra Alta 
- **Alcance del apoyo:** generación de la base de código de la API, pruebas, ejemplos, contrato OpenAPI y documentación; ajustes a partir de los documentos de clase. Para la sesión 22 se utilizó también ChatGPT/Codex (GPT-6) como apoyo para refactorizar la validación, preparar las pruebas y redactar su justificación.


Material del curso consultado: Jonathan Briceño, *Comunicación entre sistemas: Integración y APIs*, `SESION_16_v2.pdf`; y *Trabajo en clase: construir una API REST*, sesión 17, `Enunciado_Sesion17_Trabajo_API_REST.pdf`. Para el taller de pruebas se consultaron el enunciado y las sesiones 20 y 21 de Jonathan Briceño. Los PDF no se redistribuyen en este repositorio.

Documentación oficial consultada para utilizar las bibliotecas y herramientas (29 de septiembre de 2026):

- Flask: [inicio rápido](https://flask.palletsprojects.com/en/stable/quickstart/) y [pruebas](https://flask.palletsprojects.com/en/stable/testing/).
- Python: [sqlite3](https://docs.python.org/3/library/sqlite3.html) y [entornos virtuales](https://docs.python.org/3/library/venv.html).
- IETF: [RFC 9110, semántica HTTP](https://www.rfc-editor.org/rfc/rfc9110.html).
- curl: [manual oficial](https://curl.se/docs/manpage.html).
- VS Code: [entornos Python](https://code.visualstudio.com/docs/python/environments).
- GitHub: [publicar código local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) y [autenticación con Git Credential Manager](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git).


