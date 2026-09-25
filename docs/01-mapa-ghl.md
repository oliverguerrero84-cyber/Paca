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
      AGENTE ───► API Call ───► n8n            SÍNCRONO
         │          (espera la respuesta en el mismo turno)
         │
         └─► tag ───► WORKFLOW ───► webhook ───► n8n     ASÍNCRONO
                          ▲                        │
                          └── Inbound Webhook ◄────┘
                              (otro workflow continúa)
```

**Ningún workflow invoca al agente.** El agente arranca por mensaje entrante —nodo 1,
`Start Trigger — Chat Message`— y punto. Lo único que un workflow puede hacerle es
**prenderlo o apagarlo** con `Update Conversation AI Bot Status`. Un bot tampoco puede
mandar mensajes desde un workflow: para eso está `Send Message`.

**El carril asíncrono no es una preferencia, es una limitación.** El webhook de salida
de GHL no espera respuesta, así que todo ida y vuelta con n8n se cierra con n8n
disparando un Inbound Webhook y un segundo workflow continuando. Por eso `SP02` y
`AP01` tienen ese trigger.

**El carril síncrono es la razón entera de usar Agent Studio.** Su nodo `API Call` sí
espera dentro del turno. Se usa tres veces, las tres con el cliente mirando la
pantalla: stock (nodo 11), sucursal (nodo 16) y apartado con liga de pago (nodo 19).
Nada más.

De ahí se sigue lo que más se pregunta: **no hace falta un asistente para llamar a una
API.** Un asistente sirve para conversar. Confirmar el pago, crear la guía o rastrear
ocurren cuando nadie conversa, así que los hace un workflow llamando a n8n. Y un segundo
asistente no sobra: estorba, porque dos bots en el mismo WhatsApp se pelean el primer
turno.

### El eslabón entre el nodo 19 y `SP02` — cerrado con el cambio a Stripe

Antes el nodo 19 sólo marcaba `pedido-listo` y nadie llamaba a
`url_n8n_crear_apartado`. Desde el 25 sep el propio nodo 19 hace la llamada: `API Call
→ N1` aparta, crea la factura y devuelve la liga en el mismo turno, y `N1` dispara el
Inbound Webhook con el que arranca `SP02`:

```
nodo 19: API Call → url_n8n_crear_apartado
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

## 3. Agente de Agent Studio — `Agente Ventas Menudeo`

**Completo: 19 nodos.** Con IA generativa avanzada.

La conversación es el catálogo: el agente muestra, resuelve y arma el pedido
completo sin que el cliente salga de WhatsApp.

| # | Nodo | Función |
|---:|---|---|
| 1 | Start Trigger — Chat Message | Cualquier mensaje entrante |
| 2 | AI Agent | Saluda y califica: ¿menudeo o mayoreo? |
| 3 | Router AI | mayoreo → escalar · menudeo → seguir · duda general → KB |
| 4 | Search KB | Catálogo de las 30 pacas |
| 5 | AI Agent | Resuelve dudas de tallas, calidades, contenido y peso |
| 6 | Text Input | Temporada (campo gemelo, ver gotchas) |
| 7 | Text Input | Categoría: mujer / hombre / niño / especiales |
| 8 | Text Input | Calidad: Boutique / Premium / Especial |
| 9 | Text Gen | **Manda foto y video** del artículo elegido |
| 10 | Text Input | Cantidad de pacas |
| 11 | API Call → n8n `N1` | Consulta de disponibilidad real en GHL |
| 12 | Router Condicional | ¿Hay stock suficiente? |
| 13 | AI Agent | Ofrece alternativas si no hay |
| 14 | Capture | Nombre y teléfono |
| 15 | Text Input | **Código postal** — 5 dígitos |
| 16 | API Call → n8n `N3` | Buscador de sucursal: devuelve 2-3 opciones cercanas |
| 17 | Single Choice | El cliente **elige** sucursal de la lista |
| 18 | Text Gen | Resumen del pedido + aviso de que no hay devoluciones |
| 19 | API Call → n8n `N1` + End Node | Aparta y crea la factura; recibe `liga_pago` y la manda. `N1` dispara `SP02` |

**Qué cambió en la revisión 5:** el agente ya no manda a la tienda. Absorbe el
catálogo (fotos y videos por WhatsApp, como pidieron en la junta) y el buscador de
sucursal, y cierra dejando el pedido armado. **El cliente sale de WhatsApp una sola
vez: para pagar.**

### Esencial — 12 nodos

Atiende y arma el pedido igual, pero **sin consultar nada**: no lleva las llamadas
API a n8n, ni el router de stock, ni el nodo de alternativas, ni el buscador de
sucursal. Cierra derivando a un asesor:

| # | Nodo | Función |
|---:|---|---|
| 9 | Capture | Nombre y teléfono |
| 10 | Text Input | Ciudad y estado |
| 11 | Text Gen | Resumen del pedido + aviso de que un asesor confirma disponibilidad y cobra |
| 12 | End Node | Marca `pedido-armado`, que dispara `SP02` |

### Global Prompt — reglas permanentes

1. **Nunca inventar stock, precios ni cantidad de piezas.** Siempre leerlos de la KB o de la API. Si el dato no está, decirlo.
2. **Nunca decir "económica"** para la calidad baja. Se llama **Especial**. Regla explícita del cliente.
3. **Cualquier señal de mayoreo → escalar a humano** de inmediato. El mayoreo está fuera del sistema.
4. Las piezas por paca **varían**: responder con rango y aclararlo, nunca con cifra exacta.
5. Todas las pacas pesan **100 lb / 45 kg**. Ese dato sí es fijo.
6. Tono: cercano y mexicano, sin tecnicismos.
7. **No hay devoluciones.** Política explícita del cliente: *"tratamos que la venta
   sea sincera y directa: es esto, trae esto, y no hay devolución"*. El bot debe
   decirlo antes de mandar al checkout, nunca después de cobrar.
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

- **Los bots no pueden escribir en dropdowns** (`SINGLE_OPTIONS`). Por eso los
  nodos 6, 7 y 8 —temporada, categoría y calidad— son campos de texto gemelos + un
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
