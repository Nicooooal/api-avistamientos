# Relación del taller con las sesiones 20 y 21

Material revisado: Jonathan Briceño, *Pruebas unitarias y dobles de prueba* (sesión 20), *Pruebas II: Integración y cobertura* (sesión 21) y el enunciado del taller de pruebas sobre la API. La numeración impresa tiene saltos; se indican también los títulos para localizar los conceptos.

## Sesión 20

| Concepto de clase | Aplicación concreta |
| --- | --- |
| Niveles, diap. 20 | Unitarias para la regla en `validacion.py`; integración para colaboración Flask–validación–SQLite. No se presenta la suite como aceptación de usuarios ni como E2E de interfaz gráfica. |
| Testabilidad, diap. 22 | Controlabilidad: datos, reloj y base por caso. Observabilidad: resultado/error, código HTTP, JSON y estado consultado después de escribir. |
| FIRST, diap. 25 | Fast: unitarias sin red/base. Independent: fixtures nuevas. Repeatable: reloj stub. Self-validating: asserts. Timely: pruebas junto con la ampliación; no se afirma que toda la API original naciera de pruebas. |
| AAA, diap. 26 | Cada caso tiene Arrange, Act y Assert visibles. Se dividieron las pruebas que agrupaban distintas acciones; preparar un registro en Arrange y consultarlo en Assert no añade otra operación principal bajo prueba. |
| Partición, diap. 27–28 | Longitud menor de 3 / de 3 a 50 / mayor de 50; fecha mal formada / imposible / pasada o presente / futura. |
| Valores límite, diap. 27–28 | Especie 2, 3, 4 y 49, 50, 51; fecha ayer, hoy y mañana. Los 4 y 49 completan los vecinos interiores al revisar las diapositivas. |
| Dobles, diap. 30–31 | `RelojFijo` devuelve una fecha preparada: es un stub. `Mock(spec=Reloj)` también se usa como stub, sin expectativas de llamadas. |
| Inversión de dependencias, diap. 32 | El validador depende del protocolo `Reloj` y recibe la implementación desde fuera. La API inyecta el reloj del sistema; las pruebas, uno fijo. |

Los cinco dobles son alternativas según el comportamiento que se quiere verificar. No hay que añadir un dummy, spy, mock y fake solo para completar una lista. El taller exige al menos uno; el stub resuelve la dependencia temporal real de esta API. No existe una interacción de pago o correo que justifique un mock de llamadas.

Los siete principios se aplican como criterios: no se deduce ausencia de defectos por tener pruebas verdes; no se enumeran todas las fechas; la tabla anticipa la selección; se prioriza la validación por su riesgo, sin afirmar que se haya medido una concentración de defectos; se amplía la suite al cambiar la regla; se usa SQLite porque es la tecnología del proyecto; verificar el contrato no sustituye validar necesidades con usuarios.

## Sesión 21

| Concepto de clase | Aplicación concreta |
| --- | --- |
| Herramientas, diap. 6 | pytest, unittest.mock y coverage mediante pytest-cov: las opciones Python de la tabla del profesor. No hace falta migrar a Java/JUnit. |
| Stub frente a mock, diap. 8 | Se comprueba el resultado de validar con un reloj prefijado; no cuántas veces se consultó el reloj. |
| TDD y sus tres reglas | La clase exige observar rojo antes de verde para llamar TDD al proceso. La ampliación se implementó con tabla previa y pruebas posteriores al código; no se presenta como TDD ni se inventa ese historial. El enunciado no exige demostrar TDD. |
| Defectos en la frontera, diap. 14–15 | POST seguido de GET detecta errores de mapeo, SQL, persistencia y serialización que una unitaria del validador no detecta. |
| Pirámide, panal y trofeo | Se elige el nivel por riesgo y frontera. La proporción 58/51 de casos no es una meta ni una prueba de calidad. |
| Anatomía de integración, diap. 19–20 | Se verifican estado, Content-Type, Location en creación, cuerpo y efectos. `test_client()` es la herramienta Flask expresamente autorizada en el taller: ejercita la interfaz HTTP dentro del proceso, sin abrir un puerto TCP. |
| Misma tecnología de base, diap. 21 | SQLite real en archivos temporales, igual que la API; no se sustituye por un fake ni por PostgreSQL. |
| Servicios externos, diap. 22 | No hay servicios externos. Un servidor HTTP simulado sería necesario si se añadieran; actualmente no aporta una frontera que probar. |
| Contratos entre equipos, diap. 23 | Se comprueban campos y valores de nuestro contrato. No hay otro equipo/proveedor que justifique pruebas de contrato entre servicios. |
| Criterios de cobertura | Se distinguen sentencias (94,93%), ramas (92,11%) y porcentaje combinado de la herramienta (94% redondeado). No se afirma cobertura de condiciones, caminos o MC/DC. |
| Cobertura y bordes, diap. 32 | Un porcentaje alto puede ocultar un error `>`/`>=`; por eso se conservan explícitamente 3, 50 y hoy. |
| Cobertura como meta y mutación, diap. 34 y preguntas finales | No se añaden pruebas sin assert para llegar a 100%. Se documentan ramas pendientes. La mutación sería complementaria; el taller no pide ejecutarla y no se reporta un resultado de mutación inexistente. |

## Qué cambió tras revisar las diapositivas

- Separación de reemplazo por PUT e idempotencia del segundo PUT.
- Prueba independiente para repetir DELETE.
- Cuatro casos de resumen: vacío, agrupación, actualización previa y eliminación previa.
- Reloj configurable probado con una llamada por caso parametrizado.
- El segundo registro de la prueba de texto SQL pasó a Arrange: Assert solo observa resultados.
- Casos de especie de 4 y 49 caracteres, junto con los límites obligatorios.
- Justificación con FIRST, controlabilidad/observabilidad, referencias de clase y porcentajes por criterio.

No cambió el comportamiento de producción: la regla, el reloj inyectable y SQLite ya correspondían al taller. Resultado después de los ajustes: **109 casos aprobados**, 58 unitarios y 51 de integración; cobertura combinada **94%**. Más casos aquí resultan de separar comportamientos y completar límites, no de perseguir una cantidad.

## Diferencia de fechas en las fuentes

El enunciado adjunto identifica el taller con el 21 de octubre, sesión 22. Las diapositivas anuncian el taller para el martes 27 de octubre. Se conserva la identificación del enunciado en la justificación; la fecha efectiva de entrega debe verificarse en el Aula Virtual o con el profesor. El reloj fijo de las pruebas (2026-10-21) es un dato de prueba, no una afirmación sobre la fecha de entrega.
