# Mapa de implementación GHL

Nomenclatura estándar: **LS** lead sources · **SP** sales pipeline ·
**AP** active projects.

Entrega única — todo lo de este documento va en el mismo alcance.

---

## 1. Pipelines

### `SP · Menudeo` — 8 etapas

| # | Etapa | Entra cuando |
|---|---|---|
| 1 | Lead Nuevo | Llega un mensaje de un contacto sin oportunidad abierta |
| 2 | En Conversación (Bot) | El agente toma la conversación |
| 3 | Pedido Apartado (24 h) | n8n confirma la reserva de stock |
| 4 | Liga de Pago Enviada | Se envió la liga de Mercado Pago |
| 5 | Pago Confirmado | Webhook IPN validó el pago |
| 6 | Orden en Almacén | Se disparó la orden de despacho |
| 7 | Enviado — Guía Generada | El almacén capturó el número de guía |
| 8 | Entregado / Cerrado | Cierre |

Un solo pipeline. El de post-venta y recompra se retiró del alcance.

---

## 2. Workflows

| Código | Nombre | Trigger | Nodos |
|---|---|---|---:|
| `LS01` | Entrada de lead menudeo | Contact Created (filtro por canal) | 10 |
| `SP01` | Handoff al agente + control bot on/off | Customer Replied / Tag Added | 8 |
| `SP02` | Apartado 24 h + recordatorios + liberación | Inbound Webhook (n8n N2) | 18 |
| `SP03` | Liga de pago Mercado Pago | Opportunity Stage Changed → Apartado | 12 |
| `SP04` | Confirmación de pago + nº de orden | Inbound Webhook (n8n N4) | 14 |
| `SP05` | Despacho: almacén + dueños | Opportunity Stage Changed → Pago Confirmado | 10 |
| `AP01` | Captura de guía → tracking al cliente | Form Submitted (form almacén) | 9 |
| `AP02` | Escalamiento a humano | Tag Added `escalar-humano` | 8 |

### Detalle de los tres workflows críticos

**`SP02` — Apartado 24 h (18 nodos).** El corazón del sistema.
Trigger inbound webhook desde n8n → actualiza campos del apartado → mueve a etapa
3 → envía resumen con términos y condiciones → `Wait 12 h` → IF ¿ya pagó? → si no,
recordatorio (template) → `Wait 10 h` → IF ¿ya pagó? → si no, recordatorio final
(template) → `Wait 2 h` → IF ¿ya pagó? → si no, webhook a n8n para liberar →
tag `apartado-vencido` → mensaje de recuperación (template).
`Goal Event` = pago confirmado, que salta todos los waits y corta el flujo.

**`SP04` — Confirmación de pago (14 nodos).** Trigger **Inbound Webhook**, no
`Payment Received` (ver `02-arquitectura-inventario.md` §5). Guarda `orden_id`,
monto y fecha → mueve a etapa 5 → quita tag de apartado → confirma al cliente
(template) → dispara SP05.

**`AP01` — Guía → tracking (9 nodos).** Trigger `Form Submitted` del formulario
interno del almacén, que lleva el `orden_id` precargado. Guarda la guía → mueve a
etapa 7 → envía al cliente su número de guía (template) → notifica a los dueños.
El `orden_id` precargado es lo que garantiza que *"esa liga no se le envíe a nadie
más"*, la preocupación que Miguel planteó en la llamada.

### Retirados del alcance

`LS02` (campañas Meta/TikTok) y `PS01` (post-venta, reseña y recompra a 30 días)
estaban contemplados y **se sacaron**. Si más adelante reactivan las redes o
quieren trabajar la recompra, se cotizan aparte.

---

## 3. Agente de Agent Studio — `Agente Ventas Menudeo`

17 nodos, con IA generativa avanzada.

| # | Nodo | Función |
|---:|---|---|
| 1 | Start Trigger — Chat Message | Cualquier mensaje entrante |
| 2 | AI Agent | Saluda y califica: ¿menudeo o mayoreo? |
| 3 | Router AI | mayoreo → escalar · menudeo → seguir · duda general → KB |
| 4 | Search KB | Catálogo de las 30 pacas |
| 5 | Single Choice | Temporada: Verano / Invierno |
| 6 | Single Choice | Categoría: Mujer / Hombre / Niño / Especiales |
| 7 | Single Choice | Calidad: Boutique / Premium / Especial |
| 8 | Text Input | Cantidad de pacas |
| 9 | API Call → n8n `N1` | Consulta de stock en tiempo real |
| 10 | Router Condicional | ¿Hay stock suficiente? |
| 11 | AI Agent | Ofrece alternativas si no hay |
| 12 | Capture | Nombre y teléfono |
| 13 | Text Input | Ciudad, estado y sucursal de la paquetería |
| 14 | API Call → n8n `N2` | Crea apartado, reserva stock, genera `orden_id` |
| 15 | Text Gen | Resumen del pedido + T&C del apartado de 24 h |
| 16 | API Call → n8n `N3` | Genera la liga de Mercado Pago |
| 17 | End Node | — |

### Global Prompt — reglas permanentes

1. **Nunca inventar stock, precios ni cantidad de piezas.** Siempre leerlos de la KB o de la API. Si el dato no está, decirlo.
2. **Nunca decir "económica"** para la calidad baja. Se llama **Especial**. Regla explícita del cliente.
3. **Cualquier señal de mayoreo → escalar a humano** de inmediato. El mayoreo está fuera del sistema.
4. Las piezas por paca **varían**: responder con rango y aclararlo, nunca con cifra exacta.
5. Todas las pacas pesan **100 lb / 45 kg**. Ese dato sí es fijo.
6. Tono: cercano y mexicano, sin tecnicismos.

### Knowledge Base

Se carga desde `data/catalogo.csv`: 30 SKUs con temporada, categoría, calidad,
tallas, público, contenido y peso. Más las preguntas frecuentes del transcript 3:
*"¿qué es lo que mayormente preguntan los clientes? De tallas, calidades, qué tanto viene"*.

> ⚠️ 5 SKUs (corsé ×2, playera comercial, chamarra ×2, suéter navideño) **no están
> descritos en ningún transcript**. El agente no puede describir lo que no sabe.
> Pregunta #13 en `05-preguntas-cliente.md`.

---

## 4. Custom fields

**Carpeta `Apartado`:** `orden_id` (texto) · `sku_apartado` (texto) ·
`cantidad_apartada` (número) · `monto_apartado` (número) · `estado_apartado`
(dropdown: apartado / pagado / vencido / cancelado)

**Carpeta `Pago`:** `mp_preference_id` (texto) · `liga_pago` (texto) ·
`fecha_pago` (texto — **no** Date: los Date de GHL no guardan hora)

**Carpeta `Envío`:** `ciudad` · `estado_mx` · `sucursal_ocurre` · `numero_guia` ·
`fecha_envio`

**Carpeta `Atribución`:** `canal_origen` · `utm_source` · `utm_medium` ·
`utm_campaign` · `fecha_primer_contacto`

> Los UTM **no se capturan solos** en GHL (`ghl-limitations.md`). `LS01` los lee de
> la URL del widget y los escribe en estos campos.

## 5. Custom values

`url_n8n_consultar_stock` · `url_n8n_crear_apartado` · `url_n8n_liga_pago` ·
`whatsapp_almacen` · `email_duenos` · `horas_apartado` · `form_captura_guia_link`

> Las URLs de n8n van en custom values, nunca hardcodeadas en los workflows.

## 6. Formularios

| Formulario | Quién lo usa | Campos |
|---|---|---|
| `Captura de Guía — Almacén` | El almacén | `orden_id` (precargado, oculto), `numero_guia`, `fecha_envio` |
| `Ajuste Manual de Stock` | Los dueños (opcional) | `sku`, `nuevo_disponible`, `motivo` |

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

## 8. Landing de catálogo

Página pública con los 30 artículos, montada en GHL. **6 secciones:**

| # | Sección | Contenido |
|---|---|---|
| 1 | Portada | Propuesta de valor + CTA a WhatsApp |
| 2 | Cómo funciona | Los 3 pasos de compra, en versión corta |
| 3 | Catálogo verano | Los 17 artículos con foto, calidad y contenido |
| 4 | Catálogo invierno | Los 13 artículos, mismo formato |
| 5 | Preguntas frecuentes | Peso, piezas, tallas, calidades, envío |
| 6 | Cierre | CTA final a WhatsApp + datos del negocio |

Cada tarjeta de artículo arranca la conversación en WhatsApp con el SKU
precargado, de modo que el agente ya sabe de qué paca le están preguntando y se
salta los nodos 5 a 7 (temporada, categoría, calidad).

> ⚠️ **Bloqueada por contenido.** La landing no se puede montar sin **fotos** y
> **descripciones** de cada artículo, y ninguna de las dos cosas existe hoy. No
> están cotizadas: las entrega el cliente. Preguntas #2 y #3 de
> `05-preguntas-cliente.md`.

## 9. Calendarios

**No se necesitan.** El menudeo no agenda citas. Si más adelante quieren
consultoría de mayoreo con cita, se agrega como módulo aparte.
