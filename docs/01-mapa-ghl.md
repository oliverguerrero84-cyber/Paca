# Mapa de implementación GHL

Nomenclatura estándar: **LS** lead sources · **SP** sales pipeline ·
**AP** active projects.

Hay **dos paquetes**. Este documento describe el **Completo**; lo que lleva el
**Esencial** va marcado en cada sección.

| | Esencial | Completo |
|---|---|---|
| Pipeline | 5 etapas | 8 etapas |
| Workflows | 5 | 8 |
| Nodos del agente | 12 | 19 |
| Integraciones externas | 0 | 2 (Envia.com + n8n) |
| Catálogo | En la conversación | En la conversación + página pública opcional |
| Cobro | — | Liga de pago: factura de GHL cobrada con Stripe |

---

## 1. Pipelines

### `SP · Menudeo` — 8 etapas

| # | Etapa | Entra cuando |
|---|---|---|
| 1 | Lead Nuevo | Llega un mensaje de un contacto sin oportunidad abierta |
| 2 | En Conversación (Bot) | El agente toma la conversación |
| 3 | Pedido Apartado (24 h) | n8n confirma la reserva de stock |
| 4 | Liga de Pago Enviada | Se envió la liga de pago (la factura de GHL) |
| 5 | Pago Confirmado | Stripe acreditó — `Payment Received` |
| 6 | Orden en Almacén | Se disparó la orden de despacho |
| 7 | Enviado — Guía Generada | Envia generó la guía y el almacén despachó |
| 8 | Entregado / Cerrado | Cierre |

**En el Esencial son 5 etapas:** Lead Nuevo → En Conversación (Bot) → Pedido
Armado → Confirmado y Cobrado → Cerrado. Las etapas 3 a 7 del Completo (apartado,
liga de pago, pago confirmado, almacén, guía) se colapsan en una sola porque el
asesor las lleva a mano.

El pipeline de post-venta y recompra se retiró del alcance en los dos paquetes.

---

## 2. Workflows

### Completo — 8 workflows

| Código | Nombre | Trigger | Nodos |
|---|---|---|---:|
| `LS01` | Entrada de lead menudeo | Contact Created (WhatsApp) | 10 |
| `SP01` | Handoff al agente + control bot on/off | Customer Replied / Tag Added | 8 |
| `SP02` | Apartado 24 h + recordatorios + liberación | Inbound Webhook (n8n `N1`) | 16 |
| `SP04` | Pago confirmado → nº de orden | **Goal Event `Payment Received`** | 10 |
| `SP05` | Despacho: guía Envia + PDF al almacén + correo a dueños | Opportunity Stage Changed → Pagado | 12 |
| `AP01` | Rastreo: avisos hasta "llegó a tu sucursal" | Inbound Webhook (n8n `N5`) | 10 |
| `AP02` | Escalamiento a humano | Tag Added `escalar-humano` | 8 |
| `AP03` | Registro manual de pago por transferencia | Form Submitted (form interno) | 7 |

**Qué cambió respecto a la revisión 3:**
- `SP04` ya no necesita Inbound Webhook: la factura es un pago de GHL, cobre con la
  pasarela que cobre, y el **Goal Event `Payment Received` dispara solo**.
- `SP03` **desapareció el 25 sep** con el cambio a Stripe: la factura la crea `N1` por
  la API de Invoices en la misma corrida del apartado, y los recordatorios ya vivían
  en `SP02`.
- `SP05` genera la guía en vez de esperar a que el almacén la capture.
- `AP01` deja de ser un formulario y pasa a ser rastreo automático.
- `AP03` es nuevo: el registro manual de transferencias a su banco.

### Esencial — 5 workflows

| Código | Nombre | Trigger | Nodos |
|---|---|---|---:|
| `LS01` | Entrada de lead menudeo | Contact Created (filtro por canal) | 8 |
| `SP01` | Handoff al agente + control bot on/off | Customer Replied / Tag Added | 8 |
| `SP02` | Pedido armado → aviso al asesor + tarea | Tag Added `pedido-armado` | 10 |
| `SP03` | Seguimiento de pedido sin cerrar | Opportunity Stage Changed | 8 |
| `AP02` | Escalamiento a humano | Tag Added `escalar-humano` | 8 |

`SP02`, `SP04`, `SP05` y `AP01` del Completo **no existen en el Esencial**:
todos dependen de n8n, de Stripe o de la cadena de despacho. En su lugar,
`SP02` del Esencial avisa al asesor y le crea la tarea para que cierre él.

### Detalle de los tres workflows críticos

**`SP02` — Apartado 24 h (16 nodos).** El corazón del sistema.
Trigger inbound webhook desde n8n `N1` (que ya descontó el stock) → actualiza
campos del apartado → mueve a etapa 3 → envía resumen con términos y condiciones →
`Wait 12 h` → IF ¿ya pagó? → si no, recordatorio (template) → `Wait 10 h` → IF ¿ya
pagó? → si no, recordatorio final (template) → `Wait 2 h` → IF ¿ya pagó? → si no,
webhook a n8n `N2` para liberar → tag `apartado-vencido` → mensaje de recuperación.
`Goal Event` = **`Payment Received`**, que salta todos los waits y corta el flujo.

> Rama del efectivo, **sólo si la validación 4 confirma que el checkout de GHL muestra
> OXXO**: los `Wait` se calculan sobre la vigencia del voucher de Stripe (5 días por
> defecto) más un día hábil para que acredite, no sobre 24 h. OXXO no admite
> reembolsos ni contracargos.

**`SP04` — Pago confirmado (10 nodos).** Trigger **Goal Event `Payment Received`**,
que dispara porque la factura es de GHL, cobre con la pasarela que cobre. Guarda `orden_id`,
monto y método → mueve a etapa 5 → quita el tag de apartado → confirma al cliente
(template) → dispara `SP05`.

**`SP05` — Despacho (12 nodos).** Llama a n8n `N4`, que genera la guía en Envia.
Manda el **PDF de la etiqueta al WhatsApp del almacén** con nombre, cantidad,
destino y CP —**nunca el monto**, regla explícita de Miguel— y el correo completo a
los dueños. Programa la recolección y mueve a etapa 6.

### Retirados del alcance

`LS02` (campañas Meta/TikTok) y `PS01` (post-venta, reseña y recompra a 30 días)
estaban contemplados y **se sacaron**. Si más adelante reactivan las redes o
quieren trabajar la recompra, se cotizan aparte.

---

## 2.bis Quién llama a quién

La pregunta que más se repite. La respuesta cabe en una regla:

> **El agente llama a n8n cuando el cliente está esperando.
> El workflow llama a n8n cuando no hay nadie esperando.**

```
  mensaje del cliente
         │
         ▼
      BOT ───► Custom API ───► n8n             SÍNCRONO
         │       (espera la respuesta en el mismo turno, 10 s máx.)
         │
         └─► tag ───► WORKFLOW ───► webhook ───► n8n     ASÍNCRONO
                          ▲                        │
                          └── Inbound Webhook ◄────┘
                              (otro workflow continúa)
```

**Ningún workflow invoca al bot.** El bot arranca por mensaje entrante y punto. Lo único que un workflow puede hacerle es
**prenderlo o apagarlo** con `Update Conversation AI Bot Status`. Un bot tampoco puede
mandar mensajes desde un workflow: para eso está `Send Message`.

**El carril asíncrono no es una preferencia, es una limitación.** El webhook de salida
de GHL no espera respuesta, así que todo ida y vuelta con n8n se cierra con n8n
disparando un Inbound Webhook y un segundo workflow continuando. Por eso `SP02` y
`AP01` tienen ese trigger.

**El carril síncrono lo cubre la acción Custom API de Conversation AI.** Llama a n8n y
espera la respuesta dentro del turno, con **10 s de límite**. Se usa tres veces, las
tres con el cliente mirando la pantalla: apartado con liga de pago (`N1`), sucursal
(`N3`) y rastreo (`N5`). Nada más.

De ahí se sigue lo que más se pregunta: **no hace falta un asistente para llamar a una
API.** Un asistente sirve para conversar. Confirmar el pago, crear la guía o rastrear
ocurren cuando nadie conversa, así que los hace un workflow llamando a n8n. Y un segundo
asistente no sobra: estorba, porque dos bots en el mismo WhatsApp se pelean el primer
turno.

### El eslabón entre el bot y `SP02` — cerrado con el cambio a Stripe

Antes el agente sólo marcaba `pedido-listo` y nadie llamaba a
`url_n8n_crear_apartado`. Desde el 25 sep la acción **Apartar paca y liga de pago** hace la
llamada: `N1` aparta, crea la factura y devuelve la liga en el mismo turno, y `N1` dispara el
Inbound Webhook con el que arranca `SP02`:

```
acción «Apartar paca y liga de pago» → url_n8n_crear_apartado
   → n8n N1 descuenta el stock y crea la factura por la API de Invoices
   → N1 responde liga_pago e invoice_id; el agente manda la liga
   → N1 dispara el Inbound Webhook
   → SP02 arranca el reloj de 24 h
```

> **Efecto en la cotización.** Se cae `SP03` (12 nodos) y no entra ningún workflow
> nuevo: quedan 8 workflows y 81 nodos contra los 9 y 93 cotizados. No se recotiza; el
> trabajo se movió a `N1`.

### `SP01` — qué es y qué no

Aparece en la tabla como *"Handoff al agente + control bot on/off"* con 8 nodos, y
**nunca se detalló**. El nombre engaña: no invoca al agente, porque nada lo invoca.

Como `AP02` ya se encarga de apagar —tag `escalar-humano` →
`Update Conversation AI Bot Status → Off`—, si `SP01` también apagara habría dos
workflows peleándose el mismo interruptor. El reparto que deja a cada uno con un
trabajo limpio:

| | Qué hace | Trigger |
|---|---|---|
| `AP02` | **Apaga** el bot: el cliente pide un humano, o el agente detecta mayoreo | Tag Added `escalar-humano` |
| `SP01` | **Prende** el bot: el cliente vuelve a escribir después de que un humano cerró | Customer Replied |

> **Es una propuesta, no un hallazgo.** Ningún documento lo dice. Confírmalo al
> construirlo, en la semana 3.

---

## 3. Bot de Conversation AI — `Agente Ventas Menudeo`

**Decidido el 25 sep 2026.** El asistente vive en **Conversation AI**, no en Agent
Studio. Lo que antes eran 19 nodos con Router AI y capturas es ahora **un prompt, la
Knowledge Base del catálogo y tres acciones Custom API** contra n8n. Se probó ese
mismo día con un endpoint falso: el bot pidió cantidad, pidió confirmación, llamó una
sola vez y mandó la liga. Ya no se mide en nodos y **no se recotiza**: la partida de
«agente de 19 nodos» cubre este bot.

La conversación es el catálogo: el bot muestra, resuelve y arma el pedido completo
sin que el cliente salga de WhatsApp. **Sale una sola vez: para pagar.**

### El prompt — qué hace

1. Saluda y **califica**: menudeo sigue; cualquier señal de mayoreo → tag
   `escalar-humano` y se despide. El mayoreo está fuera del sistema.
2. Resuelve dudas de tallas, calidades, contenido y peso **desde la KB**.
3. Ayuda a elegir: temporada, categoría (mujer / hombre / niño / especiales) y calidad
   (Boutique / Premium / Especial). **Manda foto y video** del artículo elegido.
4. Antes de apartar, se asegura de tener **clave de la paca, cantidad, nombre, correo
   y teléfono** del contacto. La API de facturas exige correo y teléfono: sin ellos
   la factura no se crea.
5. Pide el **código postal** y ofrece las sucursales que devuelva n8n; el cliente elige.
6. Da el resumen del pedido, avisa que **no hay devoluciones**, pide confirmación y
   sólo entonces aparta y manda la liga.

Guarda en el contacto: `temporada`, `categoria`, `calidad`, `sku_elegido`,
`cantidad`, `codigo_postal`, `sucursal_elegida` (ver §4 y las gotchas de los campos
gemelos).

### Las tres acciones Custom API

Todas `POST`, JSON, **10 s de timeout**, sin reintento. Los campos de entrada se
recogen con esquema JSON (pestaña *AI - JSON Schema*); `contactId` va siempre.

| Acción | Llama a | Entrada | Salida que se mapea |
|---|---|---|---|
| **Apartar paca y liga de pago** | `N1` · `url_n8n_crear_apartado` | `sku`, `cantidad`, `contactId` | `ok`, `articulo`, `expira_texto`, `liga_pago` |
| **Sucursal por código postal** | `N3` · `url_n8n_buscar_sucursal` | `codigo_postal`, `contactId` | `sucursales` (2-3 opciones con nombre y dirección) |
| **Rastrear envío** | `N5` · `url_n8n_rastrear` | `contactId` | `estatus`, `estatus_texto` |

**Apartar paca y liga de pago**
- *When:* «Cuando el cliente ya dijo qué paca quiere y cuántas, ya eligió sucursal, y
  confirmó que quiere apartarla. Antes de llamar, asegúrate de tener la clave de la
  paca, la cantidad, y que el contacto tenga correo y teléfono.»
- *What to say:* «Si `ok` es true, dile que su paca quedó apartada hasta
  `expira_texto` y mándale `liga_pago` tal cual para pagar. Si `ok` es false, dile que
  ya no hay de esa paca y ofrécele otra. No menciones que consultaste un sistema.»

**Sucursal por código postal**
- *When:* «Cuando el cliente ya eligió su paca y te dio su código postal de 5 dígitos.
  Nunca adivines la sucursal.»
- *What to say:* «Enlista las sucursales que vinieron, con nombre y dirección, y pídele
  que elija una. Si no vino ninguna, pídele que confirme el código postal.»

**Rastrear envío**
- *When:* «Cuando el cliente pregunta dónde va su paquete o cuándo llega, y ya tiene
  una guía.»
- *What to say:* «Dile `estatus_texto` tal cual. Si no hay guía todavía, dile que su
  pedido está en preparación.»

> `N1` aparta, crea la factura y **dispara el Inbound Webhook** con el que arranca
> `SP02`. El bot no marca tags ni etapas para eso.

### Esencial

El mismo prompt y la misma KB, **sin las tres acciones**: no consulta stock, no busca
sucursal ni rastrea. Pide nombre, teléfono, ciudad y estado, da el resumen con el
aviso de que un asesor confirma disponibilidad y cobra, y marca `pedido-armado`, que
dispara `SP02`.

### Reglas permanentes del prompt

1. **Nunca inventar stock, precios ni cantidad de piezas.** Siempre leerlos de la KB o de la API. Si el dato no está, decirlo.
2. **Nunca decir "económica"** para la calidad baja. Se llama **Especial**. Regla explícita del cliente.
3. **Cualquier señal de mayoreo → escalar a humano** de inmediato. El mayoreo está fuera del sistema.
4. Las piezas por paca **varían**: responder con rango y aclararlo, nunca con cifra exacta.
5. Todas las pacas pesan **100 lb / 45 kg**. Ese dato sí es fijo.
6. Tono: cercano y mexicano, sin tecnicismos.
7. **No hay devoluciones.** Política explícita del cliente: *"tratamos que la venta
   sea sincera y directa: es esto, trae esto, y no hay devolución"*. El bot debe
   decirlo antes de mandar la liga, nunca después de cobrar.
8. **Nunca adivinar la sucursal ni la ubicación.** Siempre pedir el código postal y
   dejar que el buscador devuelva las opciones.
9. **Sólo en el Esencial:** nunca afirmar disponibilidad. El bot arma el pedido y
   avisa que un asesor confirma existencia y cobra. No hay inventario conectado que
   consultar.

### Knowledge Base

Se carga desde `data/catalogo.csv`: 30 SKUs con temporada, categoría, calidad,
tallas, público, contenido y peso. Más las preguntas frecuentes del transcript 3:
*"¿qué es lo que mayormente preguntan los clientes? De tallas, calidades, qué tanto viene"*.

> ⚠️ 5 SKUs (corsé ×2, playera comercial, chamarra ×2, suéter navideño) **no están
> descritos en ningún transcript**. El agente no puede describir lo que no sabe.
> Pregunta #3 en `05-preguntas-cliente.md`.

---

## 4. Custom fields

**Carpeta `Apartado`:** `orden_id` (texto) · `sku_apartado` (texto) ·
`articulo_apartado` (texto — el nombre legible; `sku_apartado` guarda la clave y
ningún mensaje al cliente puede decir «tu apartado de PV-MUJ-BOU») ·
`cantidad_apartada` (número) · `monto_apartado` (número) · `estado_apartado`
(dropdown: apartado / pagado / vencido / cancelado) · `expira_en` (texto — **no**
Date, por la hora; lo escribe `SP02` y lo lee el cron de respaldo de `N2`)

**Carpeta `Pago`:** `invoice_id` (texto — el campo se creó el 24 sep como
`mp_preference_id`; se le renombra la etiqueta en Greentex, no se crea otro) ·
`liga_pago` (texto) ·
`fecha_pago` (texto — **no** Date: los Date de GHL no guardan hora)

**Carpeta `Envío`:** `ciudad` · `estado_mx` · `codigo_postal` (lo pide la regla 8 del
Global Prompt y `SP05` lo manda al almacén) · `sucursal_ocurre` · `numero_guia` ·
`fecha_envio`

**Carpeta `Atribución`:** `canal_origen` · `utm_source` · `utm_medium` ·
`utm_campaign` · `fecha_primer_contacto`

> Los UTM **no se capturan solos** en GHL (`ghl-limitations.md`). `LS01` los lee de
> la URL del widget y los escribe en estos campos.

**Tipos, como quedaron creados el 24 sep.** Todo es `TEXT` salvo tres:
`cantidad_apartada` y `monto_apartado` son `NUMERICAL`, y `estado_apartado` es
`SINGLE_OPTIONS`. **Las cuatro fechas van en `TEXT`, no en `DATE`**: los `DATE` de
GHL no guardan hora, y eso vale igual para `fecha_envio` y `fecha_primer_contacto`
que para las dos que ya lo decían.

> `estado_apartado` sí puede ser desplegable porque **lo escriben los workflows, no
> el bot**. La limitación del toolkit es que los bots no pueden escribir en
> `SINGLE_OPTIONS`; `SP02` sí.

## 5. Custom values

`url_n8n_consultar_stock` · `url_n8n_crear_apartado` · `url_n8n_buscar_sucursal` ·
`url_n8n_generar_guia` · `url_n8n_rastrear` · `whatsapp_almacen` · `email_duenos` ·
`horas_apartado`

> Las URLs de n8n van en custom values, nunca hardcodeadas en los workflows.

**Dos que se cayeron de la lista**, los dos residuos de revisiones viejas:

- `url_n8n_liga_pago` — la liga es la factura que `N1` crea con la API de Invoices de
  GHL en la misma llamada del apartado (`url_n8n_crear_apartado`). **n8n nunca toca
  Stripe**, así que no hay URL aparte que guardar
- `form_captura_guia_link` — el formulario de captura de guía desapareció (ver §6).
  Envia genera la guía sola

## 6. Formularios

| Formulario | Quién lo usa | Campos |
|---|---|---|
| `Registrar Pago Manual` | Los dueños | `orden_id`, `monto`, `fecha`, `referencia` — para transferencias a su banco, fuera de Stripe |
| `Ajuste Manual de Stock` | Los dueños (opcional) | `sku`, `nuevo_disponible`, `motivo` |

> El formulario de captura de guía **desapareció**: Envia genera la guía sola.

## 7. Plantillas de mensaje

| # | Canal | Cuándo | ¿Template de Meta? |
|---|---|---|:--:|
| 1 | WhatsApp | Recordatorio de apartado por vencer | **Sí** |
| 2 | WhatsApp | Confirmación de pago | **Sí** |
| 3 | WhatsApp | Orden enviada + número de guía | **Sí** |
| 4 | WhatsApp | Apartado vencido / recuperación | **Sí** |
| 5 | Email | Detalle completo de la orden a los dueños | No |
| 6 | WhatsApp | Orden simple al almacén | No |

> Los cuatro primeros necesitan **aprobación de Meta (24–48 h)**. Redactarlos y
> enviarlos a aprobación en la semana 1 del proyecto, no al final. Es el ítem que
> más fácilmente atora el go-live.

## 8. Catálogo público — sólo Completo

**No cobra, no arma carritos y no descuenta stock.** La venta ocurre íntegra en la
conversación (ver `07-decision-checkout.md`). Esta página existe por una razón
concreta: **no tienen Instagram ni TikTok**, así que hoy los leads sólo pueden
llegar por el número de WhatsApp. Es el destino de la publicidad.

Cada artículo lleva un botón que **abre WhatsApp con el SKU precargado**, para que
el agente sepa de qué le preguntan desde el primer mensaje. **6 secciones:**

| # | Sección | Contenido |
|---|---|---|
| 1 | Portada | Propuesta de valor + CTA a WhatsApp |
| 2 | Cómo funciona | Los 3 pasos de compra, en versión corta |
| 3 | Catálogo verano | Los 17 artículos con foto, calidad y contenido |
| 4 | Catálogo invierno | Los 13 artículos, mismo formato |
| 5 | Preguntas frecuentes | Peso, piezas, tallas, calidades, envío |
| 6 | Cierre | CTA final a WhatsApp + datos del negocio |

Al llegar con el SKU precargado, el agente se salta los nodos 6 a 8 (temporada,
categoría y calidad) y va directo a cantidad y disponibilidad.

> ⚠️ **Bloqueada por contenido.** No se puede montar sin **fotos, videos y
> descripciones** de cada artículo, y hoy no existe ninguna de las tres. No están
> cotizadas: las entrega el cliente. Preguntas #2 y #3 de `05-preguntas-cliente.md`.
>
> Nota: el catálogo de la conversación necesita el mismo material. La diferencia es
> que el agente puede arrancar sin fotos —describiendo— y la página no.

## 9. Calendarios

**No se necesitan.** El menudeo no agenda citas. Si más adelante quieren
consultoría de mayoreo con cita, se agrega como módulo aparte.

---

## 10. Gotchas del toolkit — leer antes de construir

Del `PLAYBOOK-GHL.md` del CLI v2.2. Cada regla costó un bug en producción real.

### Qué se puede automatizar y qué no

| Pieza | Cómo se construye |
|---|---|
| Workflows y triggers | **Por API** (la interna, con token Firebase). Los 8 workflows son guionables |
| Pipelines, campos, custom values | Por API pública (PIT) |
| **Bots de Conversation AI** | **Sólo UI.** Prompts, acciones y canales se pegan a mano — no hay atajo |

Esto importa para estimar: el agente es trabajo manual aunque todo lo demás se
scripte.

### Reglas que cambian el diseño del agente

- **Los bots no pueden escribir en dropdowns** (`SINGLE_OPTIONS`). Por eso
  temporada, categoría y calidad son campos de texto gemelos + un
  workflow normalizador que los pasa al dropdown real. Si se diseñan como Single
  Choice, no guardan nada.
- **Las acciones tienen límite de 500 caracteres.** El prompt no, pero las acciones
  sí. Hay que contarlos antes de entregar el texto.
- **Contact Info sólo llena campos vacíos** y extrae de lo que dice la persona. No
  sobreescribe ni corrige.
- **Un Transfer Bot con condición agresiva roba el primer turno** y las capturas no
  se ejecutan. Las condiciones de transferencia deben prohibir transferir en el
  primer mensaje — crítico para el escalamiento a mayoreo.
- **Una acción de Contact Info puede dejar de ejecutar sola**, con la configuración
  intacta. Lo que la destraba es reordenar las acciones.
- **KB subida ≠ KB asociada al bot.** Son dos pasos.
- Prompts de ~500 palabras obedecen mejor que los de 1,200.

### Sobre la ventana de 24 horas

El playbook confirma lo que ya teníamos: **los mensajes libres no necesitan
plantilla de Meta mientras el cliente haya iniciado la conversación.** Las
plantillas sólo hacen falta para mensajes que arranca la empresa — que en este
proyecto son cuatro (ver §7).

### La regla de oro

> **GHL guarda y muestra nodos malformados que después no ejecutan, sin dar error.**

De ahí el protocolo: crear el nodo a mano en la UI una vez, leerlo por API y clonar
su forma exacta. Y verificar por API, nunca por el panel del contacto, que cachea.
