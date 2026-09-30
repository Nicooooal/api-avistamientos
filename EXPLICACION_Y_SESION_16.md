# Cómo funciona el proyecto y cómo se relaciona con la sesión 16

## 1. Qué construimos

El recurso es un **avistamiento de ave**. La API define cómo otros programas pueden registrarlo y consultarlo. En las pruebas manuales, `curl` actúa como cliente y Flask recibe las peticiones. SQLite guarda los registros en un archivo.

El cliente necesita conocer la URL, el método HTTP y el formato del JSON. No necesita abrir la base de datos ni importar el código del servidor. Esa separación aplica la idea de contrato de la sesión 16.

## 2. Recorrido de un POST

1. `curl` lee `ejemplos/crear.json` y envía una petición POST a `/avistamientos`.
2. Flask encuentra `crear_avistamiento()`, asociada con esa ruta y ese método.
3. `validar_avistamiento()` revisa el formato y los cuatro campos obligatorios.
4. Si algo falla, se responde 400 en JSON y no se ejecuta el INSERT.
5. Si los datos son válidos, se ejecuta un INSERT con parámetros `?`.
6. SQLite genera el id y el bloque `with db:` confirma la transacción.
7. La API consulta el registro creado y responde 201 con su representación JSON.
8. La cabecera `Location` indica dónde consultar ese nuevo recurso.

Esta secuencia es sincrónica: el cliente recibe el resultado después de ejecutar la operación. No se envía un trabajo pendiente a una cola.

## 3. Qué hace cada parte de app.py

| Elemento | Explicación |
| --- | --- |
| `CAMPOS` | Define los cuatro campos editables permitidos. |
| `get_db()` | Abre o reutiliza la conexión SQLite correspondiente al contexto de la petición. |
| `g` | Almacena esa conexión durante el contexto; no es la base de datos ni una lista global de registros. |
| `sqlite3.Row` | Permite acceder a las columnas por nombre y convertir cada fila en un diccionario. |
| `validar_avistamiento()` | Comprueba JSON, campos, tipos, textos no vacíos y fechas reales. |
| `buscar_avistamiento(id)` | Consulta por identificador y devuelve una fila o `None`. |
| `create_app()` | Construye y configura la aplicación; permite elegir una base temporal en las pruebas. |
| `CREATE TABLE IF NOT EXISTS` | Crea la tabla al arrancar y conserva los registros si ya existía. |
| `@app.get`, `@app.post`, etc. | Asocian cada método y URL con una función de Python. |
| `jsonify()` | Construye una respuesta JSON con el tipo de contenido adecuado. |
| `with db:` | Confirma las escrituras al terminar correctamente; ante una excepción revierte la transacción. No cierra por sí solo la conexión. |
| `cerrar_db()` | Cierra la conexión cuando termina el contexto de la aplicación. |
| `error_http()` | Da formato JSON a los errores HTTP conservando código y cabeceras. |
| Bloque `if __name__ == "__main__"` | Inicia el servidor cuando ejecutas `app.py`; no lo inicia al importarlo en las pruebas. |

## 4. La tabla SQLite

```sql
CREATE TABLE IF NOT EXISTS avistamientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    especie TEXT NOT NULL,
    lugar TEXT NOT NULL,
    fecha TEXT NOT NULL,
    observador TEXT NOT NULL
);
```

`id` identifica un registro; `AUTOINCREMENT` permite generarlo desde la base. `NOT NULL` impide guardar un valor nulo en esos campos. La API añade las validaciones de texto no vacío y de fecha. La fecha se almacena como texto ISO `AAAA-MM-DD`, tal como lo solicita el taller.

El archivo de datos aparece en `data/avistamientos.db`. Cuando se detiene Python, los registros permanecen allí. Al descargar el repositorio en otro computador se crea otra base vacía. `.gitignore` evita subir los datos locales y el entorno virtual.

Las consultas utilizan `?` y una tupla de valores. Así un texto recibido se trata como dato y no como una instrucción SQL. Por ejemplo, no se construye un `WHERE` concatenando lo que escribió el cliente.

## 5. Método, URL y código HTTP

| Petición | Operación SQL principal | Motivo del código |
| --- | --- | --- |
| GET `/avistamientos` | SELECT | 200: consulta realizada, incluso con lista vacía. |
| GET `/avistamientos/1` | SELECT con WHERE | 200 si hay fila; 404 si no existe. |
| POST `/avistamientos` | INSERT | 201: se creó un recurso. Datos inválidos: 400. |
| PUT `/avistamientos/1` | UPDATE con WHERE | 200: reemplazó los datos del recurso. Inexistente: 404. |
| DELETE `/avistamientos/1` | DELETE con WHERE | 200: borró la fila y envía confirmación. Inexistente: 404. |
| GET `/avistamientos/resumen` | GROUP BY y COUNT | 200: consulta agregada por especie. |

Una petición como `POST /crearAvistamiento` pondría la acción también en la URL. Aquí el recurso se expresa en plural y el método indica la operación, siguiendo el diseño del enunciado.

POST no recibe id porque lo genera SQLite. PUT toma el id de la URL y reemplaza los cuatro datos editables sin cambiar ese id. PATCH permitiría actualizar solo algunos campos, pero no forma parte de esta API.

## 6. Idempotencia con ejemplos del proyecto

Idempotencia significa que repetir una operación tiene el mismo efecto previsto sobre el estado que realizarla una vez. No exige que todas las respuestas sean idénticas.

- **GET:** consultar varias veces no cambia los registros.
- **PUT:** enviar repetidamente los mismos cuatro campos al mismo id conserva un único registro con esos datos.
- **DELETE:** la primera petición elimina y responde 200; la segunda responde 404. El estado final sigue siendo que ese recurso no existe.
- **POST:** enviar dos veces `crear.json` crea dos ids. No incorpora una clave de idempotencia ni una regla para detectar duplicados.

Por eso no se configuraron reintentos automáticos de POST. Si el cliente deja de esperar, puede que el servidor sí haya guardado el registro; repetir la petición a ciegas podría duplicarlo. El timeout de diez segundos de los ejemplos limita la espera de curl, pero no deshace una operación ya ejecutada por la API.

## 7. Relación con los temas de las diapositivas

Los números siguientes corresponden a la numeración impresa de las diapositivas. El PDF tiene saltos y un número repetido.

| Tema de la sesión 16 | Aplicación o alcance en este taller |
| --- | --- |
| Integración y contratos, 2 a 4 | Un cliente utiliza la API mediante HTTP y JSON sin acceder a su implementación interna. |
| Sincrónica y asincrónica, 5 a 9 | Este CRUD usa petición y respuesta sincrónicas. La elección permite conocer de inmediato el resultado de una escritura. |
| API, 10 | El contrato define qué puede pedir el cliente y qué recibirá. |
| REST y recursos, 11 y 15 | El dominio se representa mediante `/avistamientos` y `/avistamientos/{id}`. |
| Métodos HTTP, 12 | GET consulta, POST crea, PUT reemplaza y DELETE elimina. PATCH queda explicado, pero no implementado. |
| Códigos, 13 | 200 y 201 expresan éxito; 400 datos inválidos; 404 inexistencia. También se manejan 405 y 413. |
| JSON, 14 | Peticiones y respuestas emplean objetos o listas JSON. Es una exigencia del taller, no de todos los sistemas REST. |
| Buenas prácticas, 16 | Nombres consistentes en plural y códigos adecuados. Se conservan las URL exactas del enunciado. |
| OpenAPI, 17 | `openapi.yaml` documenta los seis endpoints y sus estructuras de datos. |
| API Gateway, 18 | No se implementa: hay un único servicio local. Tendría sentido evaluar uno si hubiera varios servicios y consumidores. |
| Robustez, 19 | Validación, transacciones y errores JSON; curl usa timeout. PUT y DELETE permiten analizar idempotencia. |
| Alternativas y FAQ, 20 | SOAP, GraphQL y gRPC son alternativas comentadas en clase; este ejercicio pide REST. |
| Resumen, 22 | Se relacionan contrato, recursos, métodos, respuestas y manejo de errores. |
| Git y plataformas, 23 a 25 | Git registra versiones localmente; GitHub aloja el repositorio que se entrega. |
| Comandos, áreas y flujo, 26 a 28 | La guía aplica `init`, `add`, `commit`, `push`, `clone`, `status` y `log`; explica `pull` para cambios remotos. |
| Recursos de práctica, 29 | Son material complementario para aprender Git, no dependencias del programa. |
| Indicaciones de entrega, 30 | El resultado entregable es el enlace al repositorio público con README. |
| Anuncios, 31 a 34 | Las exposiciones de patrones y la entrega de arquitectura de BioHub son actividades separadas. No se convierten en requisitos de esta API. |
| Bibliografía, 36 | Se usa el material de clase y documentación técnica oficial; no se atribuyen lecturas no realizadas de los libros mencionados. |

### Colas, ack, reintentos y Dead Letter Queue

La sesión presenta un productor que publica en una cola y un consumidor que procesa el mensaje. La confirmación de recepción por la cola no equivale a que el consumidor ya terminó el trabajo. En el flujo descrito, el consumidor confirma el procesamiento mediante un **ack**; sin confirmación puede producirse una nueva entrega. Tras fallos reiterados, una **Dead Letter Queue** permite separar mensajes problemáticos.

Las garantías concretas dependen del sistema y de su configuración. Con entrega al menos una vez, el consumidor debe soportar mensajes repetidos sin duplicar el efecto de negocio. En el caso de aves, enviar notificaciones después de registrar un avistamiento podría justificar ese mecanismo en una ampliación. **Esta implementación no tiene cola ni notificaciones.**

### Versionado, paginación y API Gateway

Una futura versión incompatible podría exponerse en `/v1/avistamientos` o seguir otra estrategia documentada. Aquí se mantienen las rutas solicitadas. La paginación sería útil con muchos registros, pero cambiaría el comportamiento de listar todos y necesita un contrato adicional. El Gateway serviría como entrada común y podría centralizar políticas si aparecieran varios servicios; no sustituye a SQLite ni a la lógica del CRUD.

### Formato y resultado

REST puede utilizar representaciones distintas de JSON. En este taller JSON sí es obligatorio. Ver un código 200 aislado no basta para probar el programa: también hay que revisar el cuerpo y comprobar el estado posterior con otra consulta. Las pruebas verifican ambas cosas.

### OpenAPI y contract-first

OpenAPI permite describir el contrato sin obligar al consumidor a leer Python. Se entrega un YAML con las rutas, campos y respuestas. La sesión recomienda acordar ese contrato antes de implementar; aquí se añadió al proyecto y se contrastó con el comportamiento construido. No se afirma que este trabajo se haya desarrollado originalmente mediante contract-first.

## 8. Cómo explicar las pruebas

Son pruebas de integración porque recorren el enrutamiento HTTP de Flask, las validaciones y una base SQLite real temporal. El cliente de Flask simula las peticiones dentro del proceso; las pruebas no abren un puerto de red. Las pruebas manuales con curl sí recorren el servidor HTTP local.

Cada `setUp()` crea una aplicación y una base vacía, por lo que una prueba no depende de los datos de la anterior. Las aserciones revisan código, contenido y cambios guardados. La prueba de persistencia vuelve a construir la aplicación con el mismo archivo y comprueba que el registro sigue allí.

## 9. Preguntas para comprobar que lo entiendes

1. **¿Por qué usaste SQLite?** Porque el enunciado exige una base real o embebida; SQLite guarda datos en disco y no requiere un servidor separado.
2. **¿Por qué POST responde 201?** Porque creó un recurso nuevo. GET y PUT exitosos responden 200 en este contrato.
3. **¿Qué pasa si falta `observador`?** Se responde 400 en JSON antes de insertar.
4. **¿Por qué PUT necesita todos los campos?** Porque reemplaza la representación editable completa; una modificación parcial sería otra operación.
5. **¿Qué pasa al pedir un id que no existe?** GET, PUT y DELETE responden 404.
6. **¿Qué ocurre al cerrar el programa?** Los datos ya confirmados permanecen en el archivo SQLite.
7. **¿Por qué DELETE es idempotente si la segunda respuesta cambia?** Porque el estado final sigue siendo la ausencia del recurso.
8. **¿Por qué POST no se reintenta automáticamente?** Porque cada ejecución crea otro registro y podría duplicar uno cuyo resultado se perdió en la red.
9. **¿Dónde está el contrato?** En el README para lectura humana y en `openapi.yaml` como descripción estructurada; el comportamiento se implementa en `app.py`.
10. **¿Qué diferencia hay entre Git y GitHub?** Git guarda versiones; GitHub aloja una copia remota y facilita compartirla.
11. **¿Qué diferencia hay entre add, commit y push?** Preparar cambios, registrarlos localmente y subir los commits al remoto.
12. **¿Qué aportó la IA?** La base de implementación, pruebas y documentación. Declara la herramienta y el modelo verificable, y explica qué comprobaste personalmente sin atribuirte revisiones que no hiciste.

Fuentes: los dos documentos de clase suministrados y las referencias oficiales enlazadas en el README. La precisión sobre idempotencia se apoya en RFC 9110, sección 9.2.2.
