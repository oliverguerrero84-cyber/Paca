# Estado del proyecto

> **Corte: 25 de septiembre de 2026.** En qué va todo. Los demás documentos dicen qué
> se va a hacer y en qué orden; éste dice **qué está hecho y qué no**.
>
> Cuando algo se termine, se mueve de una tabla a otra aquí mismo. Si este documento
> contradice a `docs/11-cronograma.md` o a `docs/13-accesos.md`, ellos mandan en el
> plan y éste sólo en el avance.

---

## 1. Dónde estamos, en una línea

**El cliente aceptó y pagó el Completo, su subcuenta existe —Greentex Clothing LLC— y
ya tiene el esqueleto de GHL de pie**: pipeline, campos y custom values. Falta el
motor —n8n, workflows y el agente— y los datos que el cliente todavía no manda. **El 25
de sep cambió la pasarela: se cobra con el Stripe del cliente, no con Mercado Pago**, y
la primera pieza que hace falta es que él lo conecte en Greentex.

## 2. Hecho

| Qué | Quién | Cuándo |
|---|---|---|
| Alcance, arquitectura y las decisiones de diseño | 786 | 14 – 19 sep |
| **Propuesta cerrada, aceptada y cobrada** — Completo, USD 4,497 + 637 al mes | 786 | 18 – 22 sep |
| Paquete de traspaso para trabajar el repo desde otra cuenta | 786 | 19 sep |
| **Excel del catálogo mandado al cliente** para que capture precio, piezas y stock | 786 | 22 sep |
| Mensaje de arranque al cliente con todo lo que hay que pedirle | 786 | 22 sep |
| **Los 23 campos del formulario de alta**, en la carpeta «Alta de subcuenta» | 786 | 23 sep |
| Cronograma de las 4 semanas al go-live | Germán | 23 sep |
| **La cadena de altas y accesos**, ordenada por dependencias | Germán | 23 sep |
| Mapa de desarrollo en una página para el equipo | Germán | 23 sep |
| Condiciones de pago corregidas en la propuesta | 786 | 23 sep |
| **Subcuenta del cliente creada** — Greentex Clothing LLC, y es donde se trabaja de aquí en adelante | 786 | 24 sep |
| **Esqueleto de GHL levantado** en Greentex: pipeline `SP · Menudeo` de 8 etapas, **21** campos custom en 4 carpetas y los 8 custom values | 786 | 24 sep |
| **Los 3 usuarios del cliente**, dados de alta a mano | 786 | 24 sep |
| **Las 6 plantillas de mensaje redactadas** (`A5`), listas para mandar a Meta | 786 | 24 sep |
| **Los 5 flujos de n8n escritos** como JSON importable — **sin probar**, no hay instancia donde correrlos | 786 | 24 sep |
| Validación 1 con Mercado Pago **cerrada sin resultado**: la cuenta argentina de 786 tiene las llaves revocadas. Queda anotado en `docs/13-accesos.md` §4 por si vuelve | 786 | 24 – 25 sep |
| **Ensayo del asistente con Custom API de Conversation AI**: con un endpoint falso, el bot recogió los datos, llamó una vez y mandó la liga. Mecanismo probado sin n8n | 786 | 25 sep |
| **Ensayo de la factura por API en Korvance**: 201, queda enviada con Stripe, liga `{dominio}/invoice/{id}` confirmada. `N1` corregido con lo que la API exige | 786 | 25 sep |
| **Cambio de pasarela a Stripe**, por decisión del cliente. La liga la crea `N1` con la API de Invoices y se la devuelve al agente; `SP03` desaparece; la subcuenta va en MXN | Cliente / 786 | 25 sep |

> Los 23 campos del formulario de alta viven en **Korvance, la cuenta de trabajo de
> Germán**, y ahí se quedan: son el formulario con el que se le piden los datos al
> cliente, y ya cumplieron. **No se copian a Greentex.** El script sirve para el
> siguiente cliente.

## 3. Lo siguiente, y nada de esto espera a nadie

Son los tres eslabones raíz de `docs/13-accesos.md` §2. Todo lo demás cuelga de ellos.

| # | Qué | Quién |
|---|---|---|
| `0.1` | **Rotar el PIT de Korvance.** Se compartió en texto plano por chat | 786 |
| `0.3` | **Levantar la instancia de n8n**, importar los 5 flujos de `n8n/` y dejar sus URLs en los custom values. Ojo: `N1` va con **concurrencia 1** | 786 |
| — | **Conseguir las credenciales de Envia** y hacer una guía de prueba. Destraba tres de los seis supuestos de `n8n/README.md` | 786 |
| `A3` | Confirmar que **+1 (956) 820-2011 recibe SMS o llamada**. Si es VoIP, el alta en Meta puede fallar y hay que conseguir otro número | 786 |
| — | **Agendar la sesión de mapeo** con el cliente | 786 |
| — | El **logo de 786**: la propuesta todavía lleva el wordmark provisional en CSS | 786 |

## 4. Bloqueado, y por quién

### Espera al cliente

| Qué | Bloquea |
|---|---|
| **Precios de venta por SKU** | Sin esto el bot no cotiza ni genera liga. Es lo que más falta |
| **Fotos y videos** de los 30 artículos | El catálogo que el agente manda por WhatsApp |
| **Descripciones** — faltan 6 de 30 | El agente no puede describir lo que no sabe |
| **Piezas por paca** | De lo que más preguntan los compradores |
| **Stock inicial** al menudeo | La carga de `availableQuantity` |
| **Verificar el Meta Business Manager** y agregar a 786 como socio | `A1` y `A2`, el primer eslabón del carril más largo |
| **Conectar su Stripe en Greentex** (`B1`), y activar OXXO y transferencia MX en su dashboard (`B2`) | Las validaciones 1, 2 y 4. Es lo único que hoy detiene el carril del cobro |
| **Cuenta de Envia.com con saldo** | Las guías |

Los primeros cinco se piden con el Excel que ya se les mandó.

### Espera a que exista algo nuestro

| Qué | Espera a |
|---|---|
| **7 de los 8 custom values están en `PENDIENTE`** — las 5 URLs de n8n, el WhatsApp del almacén y el correo de los dueños | Las URLs, a que n8n exista (`0.3`); las otras dos, a que las mande el cliente |
| **Validación 3** — que el nodo `API Call` responda a tiempo | Que `N1` exista, o sea la semana 2 |
| Mandar las 4 plantillas a Meta (`A6`) — **ya redactadas** en `docs/15-plantillas.md` | La WhatsApp Business Account (`A4`) |
| **Validaciones 1, 2 y 4** | Que el cliente conecte Stripe (`B1`). La 4 además pregunta si el checkout de GHL muestra OXXO y SPEI; si no, el plan es tarjeta más transferencia manual con `AP03` |
| **La liga de pago del cliente** e incrustarla en la propuesta | Nada: es tarea viva de Germán |

## 5. Sin dueño todavía

De los cinco huecos de `docs/13-accesos.md` §8, **dos ya se cerraron**: Korvance es la
cuenta de trabajo de Germán, y n8n corre en la instancia de Germán, prestada. Quedan
tres:

| # | Hueco | Bloquea |
|---|---|---|
| 1 | Cómo se obtienen las credenciales de API de Envia, y si hay ambiente de pruebas | `C3`, y con él los flujos `N3`, `N4` y `N5` |
| 4 | Roles y permisos de Pamela, Miguel y Mauricio dentro de la subcuenta | La capacitación de la última semana |
| 5 | Quién activa OXXO y transferencia MX en el Stripe del cliente: él, o 786 con acceso | `B2`, y con él la validación 4 |

## 6. Riesgos vivos

- **La aprobación de las plantillas por Meta es el único plazo que no controlamos.**
  Tarda de 24 a 48 horas y puede rechazar. Si se atrasa, se lleva el go-live con ella.
- **Si la validación 1 falla**, entra el plan B: cobrar por el checkout de la tienda y
  renunciar al apartado de 24 h. Conviene saberlo antes de prometérselo al cliente.
- **La propuesta prometió tarjeta, OXXO y SPEI en una liga.** Con Stripe en GHL sólo
  tarjeta está confirmado; los otros dos dependen de la validación 4. Si no salen, hay
  que avisarle al cliente esa misma semana.
- **El PIT sigue sin rotar.** Es lo primero de la lista de arriba.
