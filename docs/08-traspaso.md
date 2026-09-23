# Traspaso a Germán — estado del proyecto y qué sigue

> **Esto es tu tarea.** Para el contexto completo del proyecto —el negocio, la
> arquitectura, las decisiones y cómo trabajarlo desde tu computadora— lee primero
> `docs/10-contexto-completo.md`.
>
> Aquí va dónde quedó todo y qué falta. El detalle está en los demás documentos de `docs/`, y cada sección apunta al
> que corresponde. El registro de cómo se llegó a cada decisión está en
> `docs/09-conversacion.md`, que **no es fuente de verdad**: si contradice a un
> documento, gana el documento.

---

## 1. Dónde quedó

**El estado vive en `docs/14-estado.md`**, que se actualiza conforme avanza el
proyecto. Este documento ya no lo lleva: quedó congelado en el día del traspaso y
citarlo como estado fue justo lo que llevó a afirmar que no se había tocado la cuenta
de GoHighLevel cuando ya había 23 campos creados.

Lo que no cambia: el cliente es Pamela, Miguel y Mauricio Hernández — McAllen TX,
almacén en Nuevo Laredo — y contrató el **Completo, $4,497 de implementación y $637
al mes**.

---

## 2. Tu tarea — la liga de pago

Hay que **generar la liga con la que el cliente paga e incrustarla en la propuesta**.
### Las condiciones de pago — ya corregidas

Se corrigieron el 23 de sep (revisión 8). La página ya dice lo que de verdad se cobra:
**la implementación completa al arrancar, y la mensualidad un mes después de
entregado.** No hay que volver a tocar esas líneas; se dejan aquí por si hay que
ubicarlas:

| Línea | Qué dice ahora |
|---|---|
| `propuesta-paca.html:1079` · `.split-box` | El primer mes de operación va sin costo — tarjeta del Esencial |
| `propuesta-paca.html:1092` · `.split-box` | Lo mismo — tarjeta del Completo |
| `propuesta-paca.html:1171` · `.pending-note` | «Cómo se formaliza»: se cubre la implementación y la mensualidad arranca un mes después de la entrega |

**Ojo con el checklist del `CLAUDE.md` si agregas un botón de pago**: los colores salen
de `:root`, no se usan emojis, y el responsivo se mide en Chromium, no se supone.

### Cómo generar la liga

Mercado Pago **ya es pasarela nativa de HighLevel** (desde el 27 de abril de 2026,
con México entre los países soportados), así que la liga puede salir de GHL por
Payment Links o Invoices y cobrar con tarjeta, OXXO o SPEI sin desarrollo extra.
Detalle en `docs/07-decision-checkout.md` §3.

Dos ligas distintas: una de **cobro único** por el monto de implementación, y otra
**recurrente** para la mensualidad, con el primer cargo un mes después de entregado.

> El mismo mecanismo de Payment Links es el que sostiene el cobro del cliente final
> en el diseño del Completo. Si lo pruebas ahora, de paso resuelves la validación 1
> de §4 — es el supuesto que sostiene toda la arquitectura.

---

## 3. Decisiones cerradas — no las reabras sin razón nueva

Cada una costó investigación y una o más correcciones. Están en `CLAUDE.md` en
corto; aquí va el porqué.

**La venta vive en la conversación; el cobro sale por liga, no por la tienda.**
Oliver preguntó lo correcto: si la gente está hablando por WhatsApp, ¿qué tiene que
ver una tienda? Mandarlos a un carrito es fricción para un público que —según
Mauricio— *"no sabe escribir bien, no sabe usar muy bien el teléfono"*. Además el
carrito abandonado nativo manda **una sola** notificación y exige que el cliente haya
escrito su correo, así que no sirve para la cadencia del apartado.
→ `docs/07-decision-checkout.md`

**Un solo asistente, en Agent Studio de GHL.** Su nodo `API Call` le permite
preguntarle a n8n *dentro del mismo turno*: el cliente pregunta si hay existencia y
le contestan al momento. Conversation AI clásico no tiene ese nodo e iría por webhook
asíncrono. Y dos bots en el mismo WhatsApp se pelean el primer turno.
→ `docs/01-mapa-ghl.md`

**n8n hace tres cosas y ninguna es conversacional:** valida y aparta stock, busca
sucursal por código postal contra Envia, y genera guías y rastrea. **Nunca habla con
el cliente y nunca toca Mercado Pago.**
→ `docs/02-arquitectura-inventario.md`

**El inventario vive en los productos de GHL, con n8n como dueño único del
contador.** Como el cobro no pasa por el checkout de la tienda, GHL nunca descuenta
por su cuenta. Eso eliminó dos errores de diseño: el doble descuento, y uno peor —
que quien apartaba la última paca no podía pagarla, porque la tienda ya se la
mostraba agotada.

**El buscador de sucursal es una consulta a tabla, nunca IA.** Envia
`validate-zip-code` + `carrier-branches`, y se le devuelven 2 o 3 opciones para que
elija. Un modelo inventando sucursales es una guía perdida.
→ `docs/06-logistica-envia.md`

> **Dos afirmaciones de revisiones viejas eran falsas** y están corregidas: que
> Mercado Pago no era pasarela nativa de GHL, y que GHL no podía llevar inventario.
> Las dos son incorrectas. Si te topas con ellas repetidas en algún lado, es un
> resto que se escapó.

---

## 4. Lo que sigue sin validarse en cuenta

De `docs/07-decision-checkout.md` §6. Ninguna está probada todavía, y están marcadas
como supuestos en todos los documentos. **No las presentes al cliente como hechos.**

| # | Qué probar | Por qué importa |
|---|---|---|
| 1 | Que la API de Invoices / Payment Links **cobre con Mercado Pago** | Sostiene todo el diseño. El changelog los nombra como soportados, pero hay que verlo cobrar |
| 2 | Que **pagar una liga no descuente stock solo** | Si lo descontara, vuelve el doble descuento |
| 3 | Que el nodo **`API Call` responda a tiempo** | Si tarda, la conversación se siente trabada |

**Plan B si falla la 1:** cobrar por el checkout de la tienda y renunciar al apartado
de 24 h, porque ahí sí chocan. Conviene saberlo antes de prometer el apartado.

Hay un conflicto conocido que no es un supuesto, es un hecho: **OXXO acredita en
hasta 72 horas hábiles** y el apartado dura 24. La solución adoptada es que el
apartado se extiende hasta el vencimiento de la referencia de Mercado Pago cuando el
cliente elige efectivo.

---

## 5. Lo que falta de afuera

**De nosotros:** el **logo de 786 Marketing**. El encabezado de la propuesta lleva un
wordmark provisional hecho en CSS. La clase `.logo-img` ya está lista y el comentario
del HTML explica cómo cambiarlo. Ahora que el documento es el definitivo, conviene
cerrarlo antes de enviarlo.

**Del cliente** — nada de esto mueve el precio, pero sí la fecha de arranque:

| Falta | Bloquea |
|---|---|
| **Precios de venta por SKU** | Sin esto el bot no puede cotizar ni generar liga, en ninguno de los dos paquetes |
| **Fotos y videos** de los 30 artículos | El catálogo del bot y la landing |
| **Descripciones** — 6 de 30 no tienen | El bot no puede describir lo que no sabe |
| **Piezas por paca** | Es de lo que más preguntan los clientes |
| **Stock inicial** al menudeo | Necesario para el Completo. Ya se les mandó `entregables/catalogo-menudeo-para-llenar.xlsx` para capturarlo |
| **Tarifa por volumen** de la paquetería | 500 a 800 envíos al mes. No bloquea el arranque |

Ya se cerraron dos: el **envío va incluido en el precio** y la paquetería es
**Paquete Express a ocurre**. Lista completa en `docs/05-preguntas-cliente.md`.

---

## 6. Cómo arrancar tu sesión

1. Pide a Oliver acceso al repo `oliverguerrero84-cyber/Paca`.
2. Abre una sesión de Claude Code sobre ese repo, en la rama
   **`claude/cool-dirac-4sht9y`**.
3. Pega esto como primer mensaje:

```
Voy a retomar el proyecto Paca. Lee CLAUDE.md y docs/08-traspaso.md completos
antes de proponer nada, y después dime en qué estado está la propuesta y qué
hay que corregir de las condiciones de pago.

Mi tarea es generar la liga de pago con la que el cliente paga la
implementación, más una segunda para la mensualidad con un mes de gracia
después de entregado, e incrustarlas en propuesta/propuesta-paca.html.
```

Claude Code lee `CLAUDE.md` solo al abrir el repo, así que arranca sabiendo las
reglas: la rama, los precios, qué cifras no pueden salir al documento del cliente y
el checklist del HTML.

**Trabaja sobre el mismo repo**, no sobre una copia: así los cambios le regresan a
Oliver sin que nadie tenga que reconciliar nada.
