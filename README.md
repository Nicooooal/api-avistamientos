# API REST de avistamientos de aves

Trabajo individual de Ingeniería de Software 2, sesión 17. Implementado en Python con Flask y SQLite, a partir del enunciado y del material de integración y APIs de la sesión 16.

**Autor:** Nicolas Arias Lasprilla

La API registra, consulta, reemplaza y elimina avistamientos. Cada registro contiene `id`, `especie`, `lugar`, `fecha` y `observador`. SQLite conserva los datos en disco entre ejecuciones.

Si es tu primera vez con VS Code, empieza por [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md). 

## 1. Requisitos

- Python 3.10 o posterior, con `pip` y el módulo estándar `sqlite3` disponibles. Verificado en Python 3.12.14 sobre Linux.
- Acceso a internet para instalar Flask y sus dependencias la primera vez.
- Git para clonar o publicar el repositorio.
- `curl` para las peticiones manuales. En PowerShell de Windows usa `curl.exe`.
- VS Code es opcional para ejecutar, pero incluye una configuración de depuración y pruebas.

No se necesita instalar un servidor de base de datos: `sqlite3` viene con las distribuciones habituales de Python. La aplicación crea `data/avistamientos.db` y su tabla al arrancar. El archivo está excluido de Git para que cada persona trabaje con su propia base.

## 2. Obtener el proyecto

Descomprime el ZIP y abre la carpeta que contiene `app.py` y este README. Si lo recibes mediante GitHub, copia la URL real del repositorio y ejecuta:

```bash
git clone git clone https://github.com/Nicooooal/api-avistamientos.git
```
 Todos los comandos siguientes se ejecutan desde esta carpeta.

## 3. Instalar y ejecutar

### Windows: PowerShell o CMD

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Si `py` no existe, prueba `python --version` y usa `python -m venv .venv`. Los demás comandos son iguales. Se usa directamente el Python del entorno virtual: no necesitas activar scripts ni cambiar la política de PowerShell.

### macOS o Linux

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python app.py
```

En una distribución Linux que no tenga `venv` o `pip`, instala esos componentes con el administrador de paquetes de tu distribución antes de crear el entorno. En Debian/Ubuntu suelen estar en `python3-venv` y `python3-pip`.

### Confirmar el arranque

La terminal debe indicar `Running on http://127.0.0.1:5000`. Déjala abierta y usa una segunda terminal para enviar peticiones. Abre [http://127.0.0.1:5000/avistamientos](http://127.0.0.1:5000/avistamientos): al iniciar con una base nueva devuelve `[]`.

La ruta `/` no está definida y devuelve 404 en JSON. El servidor que inicia Flask es para desarrollo local. Su aviso de desarrollo no impide realizar el taller.

Para detenerlo, pulsa `Ctrl+C` en su terminal. Si el puerto está ocupado, añade `--port 5001` a `app.py` y cambia `5000` por `5001` en las peticiones.

## 4. Modelo y validaciones

| Campo | Tipo JSON | Regla |
| --- | --- | --- |
| `id` | Número entero | Lo genera SQLite. No se envía en POST ni en el cuerpo de PUT. |
| `especie` | Texto | Obligatorio y no vacío. |
| `lugar` | Texto | Obligatorio y no vacío. |
| `fecha` | Texto | Fecha real en formato `AAAA-MM-DD`. |
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

Ejecuta los ejemplos **en este orden**, con el servidor encendido y la terminal en la raíz del proyecto. En **PowerShell**, sustituye `curl` por **`curl.exe`** en todos los comandos. En macOS, Linux o Git Bash utiliza `curl`.

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

## 7. Pruebas automatizadas

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

Son **30 pruebas de integración**, con subcasos de validación. Usan el cliente de pruebas de Flask y una base SQLite temporal para cada prueba. No necesitan un servidor encendido y no modifican `data/avistamientos.db`. Al finalizar se espera `Ran 30 tests` y `OK`.

Cubren CRUD, códigos HTTP, JSON, fechas, datos faltantes, resumen, entradas con texto SQL, idempotencia de PUT y persistencia al crear una nueva instancia de la aplicación con la misma base. No se presenta este conjunto como una garantía de ausencia de errores.

Para comprobar la persistencia manualmente: crea un registro, anota su id, detén el servidor con `Ctrl+C`, vuelve a iniciarlo y consulta ese mismo id **antes de eliminarlo**. Debe seguir disponible.

## 8. Archivos del proyecto

| Archivo | Función |
| --- | --- |
| `app.py` | Conexión SQLite, creación de tabla, validaciones y endpoints. |
| `requirements.txt` | Versión de Flask usada. Pip resuelve sus dependencias. |
| `tests/test_api.py` | Pruebas de integración. |
| `ejemplos/*.json` | Cuerpos para las peticiones curl. |
| `openapi.yaml` | Contrato de los seis endpoints. |
| `GUIA_PASO_A_PASO.md` | VS Code, ejecución, pruebas, GitHub y entrega. |
| `EXPLICACION_Y_SESION_16.md` | Explicación del código y relación con las diapositivas. |
| `.vscode/` | Configuración de depuración y descubrimiento de pruebas. |
| `.gitignore` | Excluye entorno virtual, datos locales y archivos temporales. |

## 9. Contrato y decisiones de diseño

[openapi.yaml](openapi.yaml) documenta rutas, métodos, cuerpos y respuestas en OpenAPI 3.0.3. Es documentación complementaria: la validación ejecutable está en `app.py`; Flask no carga automáticamente el YAML. No se añade una interfaz Swagger ni una dependencia para ejecutar el contrato.

La comunicación de este ejercicio es sincrónica: el cliente envía la petición y recibe el resultado de la operación. Se conserva `/avistamientos` tal como lo pide el enunciado; versionado por URL y paginación quedan como posibles ampliaciones. La API actual devuelve todos los registros. Colas y API Gateway no son necesarios para una aplicación local de este alcance.

## 10. Uso de IA y fuentes

- **Herramienta utilizada:** ChatGPT, modo Codex, de OpenAI.
- **Modelo exacto:** GPT 6 Astra Alta 
- **Alcance del apoyo:** generación de la base de código de la API, pruebas, ejemplos, contrato OpenAPI y documentación; ajustes a partir de los dos documentos de clase.


Material del curso consultado: Jonathan Briceño, *Comunicación entre sistemas: Integración y APIs*, `SESION_16_v2.pdf`; y *Trabajo en clase: construir una API REST*, sesión 17, `Enunciado_Sesion17_Trabajo_API_REST.pdf`. Los PDF no se redistribuyen en este repositorio.

Documentación oficial consultada para utilizar las bibliotecas y herramientas (29 de septiembre de 2026):

- Flask: [inicio rápido](https://flask.palletsprojects.com/en/stable/quickstart/) y [pruebas](https://flask.palletsprojects.com/en/stable/testing/).
- Python: [sqlite3](https://docs.python.org/3/library/sqlite3.html) y [entornos virtuales](https://docs.python.org/3/library/venv.html).
- OpenAPI Initiative: [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3).
- IETF: [RFC 9110, semántica HTTP](https://www.rfc-editor.org/rfc/rfc9110.html).
- curl: [manual oficial](https://curl.se/docs/manpage.html).
- VS Code: [entornos Python](https://code.visualstudio.com/docs/python/environments).
- GitHub: [publicar código local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) y [autenticación con Git Credential Manager](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git).

