# Casos de validación: diseño previo a las pruebas

Fecha de referencia del stub: 2026-10-21. Los campos no mencionados contienen datos válidos. La longitud se calcula después de recortar espacios exteriores. Las particiones de especie son menos de 3, entre 3 y 50 inclusive, y más de 50 caracteres. Para fecha se distinguen formato incorrecto, día imposible, fecha pasada/presente y fecha futura.

| Campo y valor | Tipo de caso | Resultado esperado | Motivo de selección |
| --- | --- | --- | --- |
| especie: `ab` (2) | Límite inválido | Error especie | Justo antes del mínimo. |
| especie: `abc` (3) | Límite válido | Aceptar | Mínimo incluido. |
| especie: `colibrí` (7) | Representativo válido | Aceptar | Interior de la partición aceptada. |
| especie: `a` repetida 50 veces | Límite válido | Aceptar | Máximo incluido. |
| especie: `a` repetida 51 veces | Límite inválido | Error especie | Justo después del máximo. |
| especie: espacios o cadena vacía | Inválido | Error especie | Ausencia de contenido tras normalizar. |
| especie: `  abc  ` | Representativo válido | Devolver `abc` | La longitud se evalúa sobre el texto recortado. |
| fecha: `2026-10-20` | Límite válido | Aceptar | Ayer: vecino inferior de hoy. |
| fecha: `2026-10-21` | Límite válido | Aceptar | Hoy: extremo superior permitido. |
| fecha: `2026-10-22` | Límite inválido | Error fecha | Mañana: vecino superior prohibido. |
| fecha: `2026-11-21` | Representativo inválido | Error fecha | Interior de la partición futura. |
| fecha: `2024-02-29` | Representativo válido | Aceptar | Día real de un año bisiesto, anterior al reloj. |
| fecha: `2025-02-29`, `2026-02-30`, `0000-01-01` | Inválido | Error fecha | Forma correcta, pero no representan fechas reales. |
| fecha: `21/10/2026`, `2026-1-21`, `texto` | Inválido | Error fecha | Partición de formato incorrecto. |
| lugar u observador: vacío o espacios | Inválido | Error del campo | Campos obligatorios sin contenido. |
| Cada campo: null, número, booleano, lista u objeto | Inválido | Error del campo | El contrato requiere texto. |
| Cada campo obligatorio ausente | Inválido | Identificar el campo ausente | El objeto está incompleto. |
| Cuerpo: lista, null o texto | Inválido | Error de objeto JSON | Frontera estructural de entrada. |
| Campo adicional `id` o `color` | Inválido | Error de campo no permitido | El identificador lo genera el sistema. |

Esta tabla se preparó antes de implementar la nueva suite. En las pruebas HTTP se reutilizan los límites de la regla para comprobar que el controlador traduce el error a 400 y no modifica la base.
