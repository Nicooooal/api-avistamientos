# Guía para ejecutar, probar y entregar la API

Esta guía está pensada principalmente para **Windows con PowerShell dentro de Visual Studio Code**. El README también contiene la instalación para macOS y Linux. Ejecuta los comandos uno por uno y confirma el resultado antes de continuar.

## Paso 1. Instalar lo necesario

1. Instala Python desde [python.org/downloads](https://www.python.org/downloads/). El proyecto requiere Python 3.10 o posterior. Si el instalador ofrece añadir Python al PATH, habilítalo.
2. Instala [Visual Studio Code](https://code.visualstudio.com/).
3. Instala Git desde [git-scm.com/downloads](https://git-scm.com/downloads). En Windows, conserva Git Credential Manager si el instalador lo incluye: facilita iniciar sesión en GitHub al subir el proyecto.
4. Si todavía no tienes cuenta, créala en [GitHub](https://github.com/).
5. Cierra y vuelve a abrir VS Code si estaba abierto durante la instalación.

En VS Code abre **Terminal > Nueva terminal**. Comprueba:

```powershell
py --version
git --version
curl.exe --version
```

Debes ver una versión para cada herramienta. Si solo falla `py`, prueba `python --version`. Si ambos fallan, revisa la instalación de Python y vuelve a abrir la terminal.

## Paso 2. Extraer y abrir la carpeta correcta

1. Descarga `API_Avistamientos_VSCode.zip`.
2. En el Explorador de archivos, haz clic derecho y selecciona **Extraer todo**. No trabajes dentro del ZIP.
3. En VS Code selecciona **Archivo > Abrir carpeta**.
4. Abre la carpeta `api-avistamientos` que contiene `app.py`, `requirements.txt` y `README.md` directamente.
5. En el panel izquierdo debes ver esos archivos, además de `tests`, `ejemplos` y `.vscode`.
6. Abre `GUIA_PASO_A_PASO.md`. Con **Ctrl+Shift+V** puedes visualizarla con formato.
7. Abre una terminal nueva y selecciona **PowerShell** en el menú de perfiles si aparece otro tipo de terminal.

Comprueba dónde estás:

```powershell
Get-Location
Get-ChildItem
```

Si no aparece `app.py` en esa lista, todavía no estás en la raíz del proyecto. Abre la carpeta correcta antes de instalar nada.

## Paso 3. Crear el entorno e instalar Flask

Ejecuta:

```powershell
py -m venv .venv
```

Si tu sistema utiliza `python` en lugar de `py`, ejecuta `python -m venv .venv`.

La carpeta `.venv` contendrá el intérprete y las dependencias del proyecto. A continuación:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Cuando termine sin errores, comprueba Flask:

```powershell
.\.venv\Scripts\python.exe -m pip show Flask
```

Debe mostrar `Version: 3.1.3`. No necesitas instalar SQLite aparte ni ejecutar `Activate.ps1`: esta guía llama al intérprete del entorno directamente.

## Paso 4. Configurar VS Code

1. Abre **Extensiones** con `Ctrl+Shift+X`.
2. Instala **Python**, publicada por Microsoft. Para ejecutar con F5, instala también **Python Debugger**, de Microsoft, si no quedó instalada.
3. Pulsa `Ctrl+Shift+P`, busca **Python: Select Interpreter** y selecciona el intérprete dentro de `.venv`.
4. Si no aparece, selecciona la opción para introducir la ruta y elige `.venv\Scripts\python.exe` dentro del proyecto.

Esto hace que el editor, el depurador y el explorador de pruebas utilicen el mismo entorno. Los comandos de esta guía funcionan incluso sin estas extensiones.

## Paso 5. Iniciar la API

En la terminal ejecuta:

```powershell
.\.venv\Scripts\python.exe app.py
```

Debes ver una línea como:

```text
Running on http://127.0.0.1:5000
```

La terminal queda ocupada porque está atendiendo peticiones. **No la cierres.** El mensaje que indica que es un servidor de desarrollo es normal para este taller.

Abre en el navegador [http://127.0.0.1:5000/avistamientos](http://127.0.0.1:5000/avistamientos). En una base nueva verás `[]`: la API funciona y todavía no tiene registros. No hay una página con formularios; el entregable solicitado es una API que intercambia JSON.

Para volver a arrancar otro día basta con abrir la carpeta y ejecutar el mismo comando; no debes recrear el entorno ni reinstalar Flask cada vez.

Si prefieres depurar, detén antes el servidor con `Ctrl+C` y pulsa **F5**, seleccionando **Ejecutar API de avistamientos**. No uses F5 y el comando de arranque simultáneamente sobre el mismo puerto.

## Paso 6. Probar todas las operaciones desde PowerShell

Abre una **segunda terminal** con el botón `+`. Conserva la primera ejecutando la API. Los comandos siguientes se ejecutan desde la carpeta donde está `app.py`.

### 6.1. Listar: 200

```powershell
curl.exe -i --max-time 10 http://127.0.0.1:5000/avistamientos
```

Busca `200 OK` al comienzo y la lista JSON al final. `-i` muestra cabeceras; `--max-time 10` limita a diez segundos la espera del cliente.

### 6.2. Crear: 201

```powershell
curl.exe -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/crear.json"
```

Debes recibir `201 CREATED` y un objeto con los cuatro datos enviados y un `id` generado. Abre `ejemplos/crear.json` para ver qué información acabas de enviar. Los ejemplos son datos ficticios.

Anota el id. Si fue `1`, ejecuta:

```powershell
$id = 1
```

**Si recibiste otro número, sustituye 1 por ese número.** `$id` es una variable de PowerShell que usaremos en las siguientes peticiones de esta terminal. No supongas que siempre será 1: SQLite no reutiliza necesariamente los ids eliminados.

### 6.3. Consultar uno: 200

```powershell
curl.exe -i --max-time 10 "http://127.0.0.1:5000/avistamientos/$id"
```

Debes recibir `200 OK` y los datos del registro que creaste.

### 6.4. Reemplazar: 200

```powershell
curl.exe -i --max-time 10 -X PUT "http://127.0.0.1:5000/avistamientos/$id" -H "Content-Type: application/json" --data-binary "@ejemplos/actualizar.json"
```

Debes recibir `200 OK`, el mismo id, el lugar `Humedal Santa María del Lago` y la fecha `2026-09-30`. El JSON contiene los cuatro campos editables porque PUT reemplaza el conjunto completo. Ejecuta de nuevo el mismo comando: no debe crear otro registro. Esa es una demostración de idempotencia.

### 6.5. Revisar el resumen: 200

```powershell
curl.exe -i --max-time 10 http://127.0.0.1:5000/avistamientos/resumen
```

Si solo existe el registro creado en esta secuencia, verás:

```json
[{"especie": "colibrí", "cantidad": 1}]
```

El resumen cuenta registros por especie. No cuenta individuos observados, porque el modelo no incluye un campo con el número de aves.

### 6.6. Comprobar datos incompletos: 400

```powershell
curl.exe -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/incompleto.json"
```

Debe devolver `400 BAD REQUEST` e indicar que faltan `lugar`, `fecha` y `observador`. El registro inválido no se guarda.

También prueba una fecha que no existe:

```powershell
curl.exe -i --max-time 10 -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@ejemplos/fecha_invalida.json"
```

Debe responder 400 porque el 30 de febrero no es una fecha válida.

### 6.7. Comprobar persistencia antes de eliminar

1. Ve a la primera terminal, la del servidor.
2. Pulsa `Ctrl+C` para detenerlo.
3. Inícialo otra vez con `.\.venv\Scripts\python.exe app.py`.
4. En la segunda terminal repite la consulta:

```powershell
curl.exe -i --max-time 10 "http://127.0.0.1:5000/avistamientos/$id"
```

Debe responder 200 y conservar los datos actualizados. Esto comprueba que estaban almacenados en `data/avistamientos.db`, no solamente en la memoria del proceso.

### 6.8. Eliminar: 200

```powershell
curl.exe -i --max-time 10 -X DELETE "http://127.0.0.1:5000/avistamientos/$id"
```

Debe responder 200 con un mensaje de eliminación y el id.

### 6.9. Comprobar inexistencia: 404

Ejecuta las tres peticiones siguientes sobre el id eliminado:

```powershell
curl.exe -i --max-time 10 "http://127.0.0.1:5000/avistamientos/$id"
curl.exe -i --max-time 10 -X PUT "http://127.0.0.1:5000/avistamientos/$id" -H "Content-Type: application/json" --data-binary "@ejemplos/actualizar.json"
curl.exe -i --max-time 10 -X DELETE "http://127.0.0.1:5000/avistamientos/$id"
```

Las tres deben responder `404 NOT FOUND`. Así verificas los casos de inexistencia exigidos para consulta, actualización y eliminación.

## Paso 7. Ejecutar las pruebas automatizadas

En la segunda terminal:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La parte final debe mostrar:

```text
Ran 30 tests in ...s

OK
```

El tiempo varía. Las pruebas emplean bases temporales y no alteran los datos manuales. No necesitas detener ni iniciar el servidor para ejecutarlas.

Para comprenderlas, abre `tests/test_api.py`. Cada función cuyo nombre empieza por `test_` comprueba un comportamiento. `assertEqual` compara el resultado obtenido con el esperado. Si aparece `FAILED`, lee el nombre de la prueba y el error antes de entregar.


## Paso 8. Crear el repositorio público en GitHub

1. Inicia sesión en [GitHub](https://github.com/).
2. Selecciona **New repository** desde el menú para crear repositorios.
3. Escribe `api-avistamientos` como nombre.
4. Puedes usar esta descripción: `API REST de avistamientos de aves con Flask y SQLite. Taller ISW-2.`
5. Selecciona **Public**. El enunciado exige un repositorio público.
6. Déjalo vacío: no añadas README, `.gitignore` ni licencia desde GitHub, porque el proyecto ya trae los archivos iniciales que necesita.
7. Selecciona **Create repository**.
8. Copia la URL HTTPS que muestra GitHub. Tendrá una forma parecida a `https://github.com/TU_USUARIO/api-avistamientos.git`.

La API seguirá ejecutándose en tu computador. GitHub almacena el código; no la pone a funcionar como un servicio público. El taller pide el enlace al repositorio, no un despliegue ni GitHub Pages.

## Paso 9. Subir el proyecto con Git desde VS Code

En la terminal del proyecto ejecuta:

```powershell
git init
```

Configura la identidad **para este repositorio**. Sustituye los textos antes de ejecutar:

```powershell
git config user.name "TU NOMBRE"
git config user.email "TU CORREO DE GITHUB O TU CORREO NOREPLY"
```

Si prefieres no publicar tu correo habitual en los commits, copia tu dirección `noreply` desde la configuración de correo de GitHub; no inventes su formato.

Comprueba los archivos y prepara el primer commit:

```powershell
git status
git add .
git status
```

En la lista de archivos preparados deben aparecer `app.py`, README, pruebas, ejemplos, documentación, `requirements.txt`, `.vscode` y `.gitignore`. **No deben aparecer `.venv` ni `data/avistamientos.db`**, porque `.gitignore` los excluye.

Registra los cambios:

```powershell
git commit -m "Implementa API de avistamientos con SQLite y pruebas"
git branch -M main
```

Conecta la carpeta al repositorio remoto usando **la URL real que copiaste**:

```powershell
git remote add origin https://github.com/TU_USUARIO/api-avistamientos.git
git remote -v
git push -u origin main
```

No ejecutes la URL de ejemplo sin cambiar `TU_USUARIO`. Si Git Credential Manager abre el navegador, inicia sesión en tu cuenta y completa la autorización. No pongas contraseñas ni tokens dentro de los archivos del proyecto. Si te solicita una contraseña de Git por HTTPS, la contraseña normal de GitHub no sustituye el mecanismo de autenticación por token o Credential Manager; consulta el enlace oficial de autenticación del README.

Cuando termine, recarga la página del repositorio. Debes ver los archivos extraídos, con el README visible debajo. No subas solamente el ZIP.

### Qué hizo cada comando

| Comando | Efecto |
| --- | --- |
| `git init` | Crea el repositorio local. |
| `git status` | Muestra archivos nuevos, modificados y preparados. |
| `git add .` | Pasa los cambios al área de preparación. |
| `git commit` | Guarda esos cambios en la historia local. |
| `git remote add origin ...` | Registra la dirección del repositorio remoto. |
| `git push -u origin main` | Sube los commits y vincula la rama local con la remota. |
| `git log --oneline` | Muestra los commits ya registrados. |

**Guardar el archivo, hacer commit y hacer push son acciones diferentes.** El commit no sube por sí solo los cambios a GitHub.

## Paso 10. Verificar que quedó bien subido a github

1. Abre la URL del repositorio en una ventana privada del navegador, sin iniciar sesión. Comprueba que puedes ver los archivos: eso verifica el acceso público.
2. Detén el servidor de la carpeta original para liberar el puerto.
3. En una terminal de PowerShell entra a una carpeta distinta donde quieras verificar la descarga. Por ejemplo, desde la raíz del proyecto original puedes usar `cd ..` para ir a su carpeta padre.
4. Clona una copia con otro nombre:

```powershell
git clone https://github.com/TU_USUARIO/api-avistamientos.git api-avistamientos-verificacion
cd api-avistamientos-verificacion
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe app.py
```

Si tu comando era `python`, úsalo en lugar de `py`. Cuando las pruebas indiquen `OK` y el servidor arranque, abre `/avistamientos`. La copia nueva comienza con `[]`, porque la base de datos local no viaja por Git. Repite el POST de ejemplo para comprobar que puede crear registros.
