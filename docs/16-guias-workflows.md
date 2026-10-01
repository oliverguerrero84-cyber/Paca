# Guías de construcción de los workflows

> **Para armar en la interfaz de GHL, nodo por nodo.** Germán arma; nosotros
> verificamos por la API. Una guía por workflow, en el orden de construcción de
> `docs/01-mapa-ghl.md` §2.
>
> La descripción de qué hace cada workflow vive en `docs/01-mapa-ghl.md`. **Aquí van los
> valores exactos**: nombres de campo para copiar y pegar, duraciones, condiciones.

**Por qué esta guía termina en una verificación y no en «quedó armado».** Regla dura de
`CLAUDE.md`: *GHL guarda y muestra nodos malformados que después no ejecutan, sin
avisar.* Un workflow que se ve bien en el canvas puede estar muerto. La única prueba es
leerlo por la API y correrlo.

| Workflow | Guía | Estado |
|---|---|---|
| `AP01` · Rastreo | — | Esperando la URL del Inbound Webhook de Germán |
| **`SP02`** · Apartado 24 h | **§2 de este documento** | **Lista para armar** |
| **`AP02`** · Escalamiento a humano | **§3 de este documento** | **Lista para armar** — es la más corta, y la elegida para probar si la API interna sirve |
| `SP04` · Pago confirmado | — | Se escribe con lo que salga de `SP02` |
| `AP03`, `SP05`, `LS01` | — | Después |

---

## 1. Antes de tocar nada

### 1.1 Lo que ya existe en Greentex, verificado el 29 sep

| | |
|---|---|
| Pipeline | `SP · Menudeo` — `80QTHEK406nT2KJhQ6TZ` |
| Etapa del trigger de `SP02` | **«Liga de Pago Enviada»** — `4f1e4ebd-9514-4f7d-98ef-0bcb4c145744` |
| Campos de oportunidad | 14, los del pedido |
| Campos de contacto | 25 |
| Workflows | 4, **todos en borrador y todos de prueba**. `SP02` no existe: se arranca de cero |
| Tags | `prueba-n1`, `prueba-n3`, `prueba-paca`. **`apartado-vencido` no existe todavía** |

Las 8 etapas, en orden: `Lead Nuevo` · `En Conversación (Bot)` · `Pedido Apartado (24 h)`
· **`Liga de Pago Enviada`** · `Pago Confirmado` · `Orden en Almacén` ·
`Enviado — Guía Generada` · `Entregado / Cerrado`.

### 1.2 ⚠️ La trampa de los campos duplicados

**Cada campo del pedido existe dos veces**: en la oportunidad, que es donde vive desde el
28 de septiembre, y en el contacto, que es donde vivía antes y **nunca se borró**.

| El bueno | El viejo, que sigue ahí |
|---|---|
| `opportunity.articulo_apartado` | `contact.articulo_apartado` |
| `opportunity.estado_apartado` | `contact.estado_apartado` |
| `opportunity.expira_en` | `contact.expira_en` |
| `opportunity.liga_pago` | `contact.liga_pago` |
| `opportunity.monto_apartado` | `contact.monto_apartado` |
| `opportunity.cantidad_apartada` | `contact.cantidad_apartada` |
| `opportunity.orden_id` | `contact.orden_id` |
| `opportunity.sku_apartado` | `contact.sku_apartado` |
| `opportunity.invoice_id` | `contact.invoice_id` |
| `opportunity.fecha_pago` | `contact.fecha_pago` |
| `opportunity.numero_guia` | `contact.numero_guia` |
| `opportunity.etiqueta_pdf` | `contact.etiqueta_pdf` |
| `opportunity.track_url` | `contact.track_url` |
| `opportunity.fecha_envio` | `contact.fecha_envio` |

**Nadie escribe en los del contacto.** Están vacíos y van a seguir vacíos.

En el selector de la interfaz los dos se llaman igual —«Artículo apartado», «Estado del
apartado»—. Si se escoge el del contacto:

- en un **mensaje**, la variable sale **vacía**: el cliente recibe *"tu apartado de
  vence hoy a las"*;
- en un **If**, la condición **nunca se cumple**, así que el flujo se va siempre por la
  rama del `else`;
- y **GHL no da ningún error**, ni al guardar ni al correr.

Por eso en esta guía cada campo va escrito completo. **Después de armar cada nodo que lea
un campo, ábrelo otra vez y confirma que dice `opportunity.`**, no `contact.`.

> Lo que hay que hacer con los 14 viejos es borrarlos, para que no se puedan escoger por
> error. No es parte de `SP02`; queda anotado en `docs/14-estado.md` §3.

### 1.3 🔴 Lo que bloquea dos de los tres mensajes

**Las plantillas 1 y 4 no existen todavía en Meta.** `A6` —mandarlas a aprobación—
espera a la WhatsApp Business Account (`A4`), que espera a que el cliente verifique su
Meta Business Manager.

Y esto no es un detalle de calendario: **los recordatorios de `SP02` caen fuera de la
ventana de 24 horas de WhatsApp**, que es exactamente para lo que sirven las plantillas.
El primero sale 12 horas después del último mensaje del cliente.

Conclusión práctica: **`SP02` se arma completa hoy, pero sus tres mensajes no pueden
salir hasta que Meta apruebe.** Los nodos se dejan puestos y sin configurar el contenido,
marcados. La copia de prueba (§2.7) sí corre hoy, porque con esperas de minutos la
ventana sigue abierta y el texto libre funciona.

### 1.4 🔴 `expira_en` no se le puede enseñar al cliente

`N1` guarda en la oportunidad `expira_en` **en ISO 8601 con offset** —
`2026-09-29T22:30:00.000Z`— porque es un contrato con `N2`, que lo compara. Eso no se
toca.

Pero la **plantilla 1** quiere la hora en palabras: *"vence hoy a las 6:30 p.m."*. Si se
mapea `{{3}}` a `opportunity.expira_en`, al cliente le llega:

```
Hola Laura, tu apartado de MUJER VERANO BOUTIQUE vence hoy a las 2026-09-29T22:30:00.000Z.
```

No da error. Sólo sale mal, y sale mal en un mensaje al cliente.

**`N1` ya calcula el texto bueno** y no lo guarda: en el nodo «Arrancar reloj de 24 h»
arma `expira_texto` con `toLocaleString('es-MX', …)` en `America/Chicago`, y sólo se lo
devuelve al bot.

**El arreglo son dos cambios chicos**, y hay que hacerlos antes de conectar la plantilla 1:

1. Crear el campo de oportunidad **`expira_texto`** (`TEXT`, «Expira en · texto»), en la
   carpeta *Apartado*, con `scripts/crear-esqueleto-menudeo.py`, que es idempotente.
2. En `N1`, nodo «GHL · apartado en la oportunidad», sumar `expira_texto: a.expira_texto`
   al objeto de `customFields`, y subirlo con `scripts/subir-n8n.py`.

Mientras no estén, la plantilla 1 no se conecta. No bloquea armar `SP02` ni probarla.

---

## 2. `SP02` · Apartado 24 h

**Es el corazón del sistema y lo que el cliente compró**: apartar una paca 24 horas sin
cobrar nada por adelantado, con recordatorios, y soltarla sola si no pagan.

### 2.1 Qué pasa antes de que arranque

```
el bot llama a N1  →  N1 aparta el stock, crea la factura y la liga
                   →  N1 escribe el pedido en la oportunidad
                   →  N1 la mueve a «Liga de Pago Enviada»
                   →  ESO dispara SP02
```

`N1` **no llama a ningún workflow**. `SP02` arranca por el cambio de etapa. Cuando
arranca, la oportunidad ya trae `sku_apartado`, `articulo_apartado`, `cantidad_apartada`,
`monto_apartado`, `estado_apartado = apartado`, `expira_en`, `invoice_id` y `liga_pago`.

### 2.2 El trigger

| | |
|---|---|
| Tipo | **Pipeline Stage Changed** |
| Pipeline | `SP · Menudeo` |
| Stage | **`Liga de Pago Enviada`** |

Nada más. Sin filtros extra.

> **Ojo con el reingreso.** En *Settings* del workflow, **«Allow Re-entry» apagado**. Un
> contacto puede volver a apartar semanas después; si se permite el reingreso y la
> oportunidad vuelve a pasar por esa etapa con el flujo todavía corriendo, quedan dos
> relojes sobre el mismo pedido.

### 2.3 Los nodos, en orden

| # | Nodo | Qué se configura |
|---|---|---|
| 1 | **Send Message** · WhatsApp | El mensaje de términos y condiciones de §2.4. **Texto libre**: el cliente acaba de escribirle al bot, la ventana de 24 h está abierta |
| 2 | **Wait** | **12 horas** |
| 3 | **If/Else** | `{{opportunity.estado_apartado}}` **is equal to** `pagado` → rama *sí*: **fin del flujo**. Rama *no*: sigue al 4 |
| 4 | **Send Message** · WhatsApp | **Plantilla 1**, mapeo en §2.5. Bloqueado hasta §1.3 y §1.4 |
| 5 | **Wait** | **10 horas** |
| 6 | **If/Else** | El mismo del 3 → rama *sí*: fin. Rama *no*: sigue al 7 |
| 7 | **Send Message** · WhatsApp | **Plantilla 1** otra vez, como recordatorio final |
| 8 | **Wait** | **2 horas 20 minutos** |
| 9 | **If/Else** | **Opportunity status** *is equal to* `abandoned` → rama *sí*: sigue al 10. Rama *no*: fin |
| 10 | **Add Contact Tag** | `apartado-vencido` — hay que crearlo, no existe |
| 11 | **Send Message** · WhatsApp | **Plantilla 4** |

**Por qué 12 + 10 + 2 h 20 min.** Suman **24 horas y 20 minutos**. Las 24 son el apartado.
Los 20 minutos de más son margen para el cron de `N2`, que corre cada 15 y es quien
marca la oportunidad como `abandoned`. Si `SP02` preguntara a las 24 en punto, `N2`
todavía no habría pasado y el flujo se iría por el `else` sin avisarle a nadie.

**Los waits son fijos, no calculados.** `expira_en` es texto, y GHL no puede esperar
«hasta» un texto.

**Por qué el If del paso 9 mira el status y no el campo.** Quien libera el apartado es
`N2`, y `N2` deja la oportunidad en `abandoned`. Es la señal más confiable de que el
reloj llegó a cero de verdad.

### 2.4 El mensaje 1 — términos y condiciones

Texto libre. Va con los campos de la **oportunidad**:

```
Listo, tu paca quedó apartada.

{{opportunity.articulo_apartado}}
Cantidad: {{opportunity.cantidad_apartada}}
Total: ${{opportunity.monto_apartado}} MXN

Tienes 24 horas para pagarla. Aquí está tu liga:
{{opportunity.liga_pago}}

Si no alcanzas a pagar, no pasa nada: la paca se libera sola y no hay ningún cargo.
```

> **«No hay ningún cargo» va a propósito**, igual que en la plantilla 1. Es lo que quita
> el miedo a apartar, que es lo que frena a un comprador primerizo.

### 2.5 Las plantillas y su mapeo

**Plantilla 1 — recordatorio** (nodos 4 y 7):

| Variable | Qué va |
|---|---|
| `{{1}}` | nombre del contacto |
| `{{2}}` | `{{opportunity.articulo_apartado}}` |
| `{{3}}` | `{{opportunity.expira_texto}}` — **el campo de §1.4, no `expira_en`** |
| `{{4}}` | `{{opportunity.liga_pago}}` |

**Plantilla 4 — apartado vencido** (nodo 11):

| Variable | Qué va |
|---|---|
| `{{1}}` | nombre del contacto |
| `{{2}}` | `{{opportunity.articulo_apartado}}` |

El texto de las dos está en `docs/15-plantillas.md`.

### 2.6 El Goal

`Payment Received`, para que el flujo se corte en cuanto entre el pago en vez de esperar
a la siguiente condición.

> **(verificar) que exista como goal.** Nadie lo ha comprobado en esta cuenta. **Si no
> existe, no pasa nada grave**: los If de los pasos 3 y 6 ya cortan el flujo cuando
> `SP04` pone `estado_apartado = pagado`. El Goal sólo lo corta antes, sin esperar al
> wait. Constrúyela sin el Goal si no aparece, y anótalo.

### 2.7 La copia de prueba

Antes de dejar corriendo un flujo de 24 horas, se prueba uno de 5 minutos.

**`SP02 · PRUEBA`**, idéntica salvo:

| | Real | Prueba |
|---|---|---|
| Wait del paso 2 | 12 h | **2 minutos** |
| Wait del paso 5 | 10 h | **2 minutos** |
| Wait del paso 8 | 2 h 20 min | **1 minuto** |
| Mensajes 4, 7 y 11 | plantillas 1, 1 y 4 | **texto libre** con las mismas variables |

Los mensajes de la copia pueden ir en texto libre porque en 5 minutos la ventana de 24 h
sigue abierta. Es justo lo que **no** se puede hacer en la versión real.

**Con qué se prueba:** el contacto **«Prueba Paca»**, que ya tiene la oportunidad
`ZMTFf0hvLxNkwQJn6tRw`. Hoy está en «Liga de Pago Enviada» con status `abandoned` y
`estado_apartado = vencido`.

**Cómo se corre:**

1. Poner la oportunidad en otra etapa —«Pedido Apartado (24 h)»— y `estado_apartado` en
   `apartado`, para que el cambio a «Liga de Pago Enviada» dispare el trigger.
2. Moverla a **«Liga de Pago Enviada»**. Ahí arranca.
3. **Camino del que paga:** antes de los 2 minutos, poner `estado_apartado = pagado` a
   mano. El flujo debe **parar** en el primer If y no mandar nada más.
4. **Camino del que no paga:** dejarla correr. Deben salir los dos recordatorios; después
   poner el status en `abandoned` a mano —simulando a `N2`— y comprobar que entra el tag
   `apartado-vencido` y sale el último mensaje.

**Las dos corridas hay que hacerlas.** La del que paga es la que más se usa y la que
nadie prueba.

> Al terminar, la copia de prueba **se borra**, y la oportunidad de «Prueba Paca» se deja
> como estaba. Está en la limpieza de `docs/14-estado.md`.

### 2.8 Qué se verifica por la API

Cuando Germán la dé por armada, antes de activarla:

| Qué | Cómo se sabe que está bien |
|---|---|
| El trigger | Apunta al pipeline `80QTHEK406nT2KJhQ6TZ` y a la etapa `4f1e4ebd-9514-4f7d-98ef-0bcb4c145744` |
| Los tres waits | 12 h, 10 h y 2 h 20 min — que sumen 24 h 20 min |
| Los tres If | **Leen `opportunity.…`**, no `contact.…`. Es lo primero que hay que mirar |
| El valor del If | `pagado`, exacto: `estado_apartado` es un desplegable con `apartado`, `pagado`, `vencido`, `cancelado` |
| El tag | `apartado-vencido`, escrito igual |
| Re-entry | Apagado |
| Los mensajes | Que las variables digan `opportunity.` y que ninguna quede sin resolver |

### 2.9 Las cuatro marcas *(verificar)* que esta construcción tiene que cerrar

| # | Qué no se sabe | Cómo se comprueba | Si sale que no |
|---|---|---|---|
| 1 | Si **`Payment Received` existe como goal** | Buscarlo en el selector de Goals al armarla | Se arma sin Goal. Los If ya cortan el flujo (§2.6) |
| 2 | Si `{{opportunity.…}}` **resuelve** en un workflow disparado por cambio de etapa | La corrida de prueba: si el primer mensaje llega con el artículo y el monto, resuelve | Hay que pasar los datos por otro lado; se replantea con lo que se vea |
| 3 | Si el **If lee el valor nuevo** después de un wait, o el que había al arrancar | Camino del que paga de §2.7: cambiar el campo durante el wait | Si lee el viejo, el cliente que ya pagó recibe recordatorios. Habría que mover el corte al Goal |
| 4 | Si el **status `abandoned`** se puede leer en un If | Camino del que no paga de §2.7 | Se cambia el If del paso 9 a `estado_apartado = vencido`, que `N2` también escribe |

La 3 es la que más importa: **si sale que no, el apartado le manda recordatorios a gente
que ya pagó.**

---

## 3. `AP02` · Escalamiento a humano

**La más corta del proyecto, y por eso la primera.** Cuatro nodos. Se eligió para probar
si la API interna de GHL sirve para crear workflows: si algo sale mal, se pierde esto y
no ocho workflows.

### 3.1 Qué hace, y por qué importa

Cuando el cliente pide hablar con una persona —o el bot detecta que es mayoreo, que está
fuera de alcance— hay que **apagar el bot en esa conversación** y avisarle a los dueños.

Si el bot no se apaga, pasa lo peor que puede pasar en este sistema: **el dueño contesta
y el bot le contesta encima al cliente.** Dos voces en el mismo WhatsApp.

### 3.2 El trigger

| | |
|---|---|
| Tipo | **Contact Tag Added** |
| Tag | `escalar-humano` |

> El tag **no existe todavía** en Greentex (sólo están `prueba-n1`, `prueba-n3` y
> `prueba-paca`). Se crea solo al escribirlo en el trigger, pero conviene revisar que
> quede escrito **exactamente así**, en minúsculas y con guión: quien lo pone es el bot,
> y un tag con otra letra no dispara nada y no avisa.

### 3.3 Los nodos, en orden

| # | Nodo | Qué se configura |
|---|---|---|
| 1 | **Update Conversation AI Bot Status** | **Off**. Va primero, antes que todo: cada segundo que tarde es un turno que el bot le puede ganar al dueño |
| 2 | **Create Task** | Asignada a los dueños. Título: `Atender a {{contact.first_name}} — pidió hablar con una persona`. Vencimiento: **mismo día** |
| 3 | **Send Email** | A `{{custom_values.email_duenos}}`. Asunto y cuerpo en §3.4 |

**El orden no es decorativo.** Apagar el bot es lo único urgente; la tarea y el correo
pueden tardar un segundo más sin que pase nada.

> **No lleva mensaje al cliente.** A propósito: quien debe contestarle ahora es una
> persona. Un *"en un momento te atendemos"* automático justo después de que pidió un
> humano se lee como que nadie lo escuchó.

### 3.4 El correo a los dueños

**Asunto:** `Un cliente pidió hablar con una persona — {{contact.first_name}} {{contact.last_name}}`

```
{{contact.first_name}} {{contact.last_name}} pidió que lo atienda una persona.

Teléfono: {{contact.phone}}
Correo:   {{contact.email}}

El asistente ya quedó apagado en esa conversación, así que pueden contestarle
directo por WhatsApp sin que les escriba encima.
```

> 🔴 **`email_duenos` sigue en `PENDIENTE`.** Es uno de los 2 custom values que faltan, y
> espera a que el cliente mande el correo. **El workflow se arma igual**: el nodo queda
> puesto y apuntando al custom value, y en cuanto el valor se llene empieza a funcionar
> sin tocar nada. Lo que no se puede es probar el correo hasta entonces.

### 3.5 Cómo se prueba

1. Ponerle el tag `escalar-humano` al contacto **«Prueba Paca»**.
2. Comprobar que la tarea se creó y quedó asignada.
3. El correo no se puede comprobar hasta que `email_duenos` tenga valor.
4. El apagado del bot tampoco, hasta que exista el bot — pero **el nodo tiene que quedar
   armado desde hoy**: es el que evita que dos voces le escriban al mismo cliente.

> Al terminar, quitarle el tag a «Prueba Paca» para dejarlo como estaba.

### 3.6 Qué se verifica por la API

| Qué | Bien es |
|---|---|
| El trigger | Tag Added, con el tag escrito `escalar-humano` exacto |
| El orden | *Update Conversation AI Bot Status* es el **primer** nodo |
| El estado del bot | **Off**, no Toggle: un toggle lo volvería a prender si ya estaba apagado |
| El correo | Apunta a `{{custom_values.email_duenos}}`, no a una dirección escrita a mano |
| Nodos vivos | Los 3 existen y ninguno quedó a medio configurar |
