# Arquitectura de inventario, apartado y cobro

> **Revisión 5.** El stock vive en GHL (la revisión 4 lo sacó de Google Sheets al
> descubrir que GHL sí lleva inventario nativo). Lo nuevo de esta revisión: **el
> cobro sale del checkout de la tienda y pasa a una liga de pago**, lo que convierte
> a n8n en **dueño único del contador**. Ver `07-decision-checkout.md`.

---

## 1. Diagrama general

```
  Campañas Meta e Instagram ──► WhatsApp (único canal de entrada)
                                      │
                                      ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  GHL                                                          │
  │  CRM · Bot (Conversation AI) · Productos con inventario        │
  │  Facturas cobradas con Stripe · Workflows                      │
  └──────────────────────────────────────────────────────────────┘
        │  webhook                          ▲  inbound webhook
        ▼                                   │
  ┌──────────────────────────────────────────────────────────────┐
  │  n8n — dos trabajos, nada más                                 │
  │  1. El apartado: Update Inventory ±1 y la factura por API     │
  │  2. El puente con Envia.com (guía, recolección, rastreo)      │
  └──────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    Envia.com ──► Paquete Express
```

**Lo que cambió:** el cobro y el inventario salieron de n8n y entraron a GHL.
n8n ya no es el motor del sistema, es un temporizador y un traductor.

---

## 2. Dónde vive cada cosa

| Dato | Dónde vive | Quién lo escribe |
|---|---|---|
| Catálogo de los 30 artículos | Productos de GHL — el precio vive aquí y lo usan las ligas de pago | Se carga una vez; los dueños editan precios |
| **Stock disponible** | `availableQuantity` del producto en GHL | Los dueños al reponer; n8n al apartar y liberar |
| Apartados vigentes | Oportunidades del pipeline + campos custom | Los workflows |
| Pagos | Facturas de GHL, cobradas con el Stripe del cliente | GHL |
| Guías y rastreo | Envia.com, reflejado en campos custom | n8n |

**No hay Google Sheet.** El cliente ve y edita su stock en la misma pantalla donde
ve sus ventas. Es una herramienta menos que aprender y una fuente de verdad menos
que sincronizar.

> El mayoreo sigue fuera: `availableQuantity` es sólo la porción asignada a menudeo.
> Cuando muevan pacas de un lado al otro, ajustan la cantidad en el producto.

---

## 3. El apartado tipo boleto de concierto

Es como lo pidió el cliente en la segunda junta: eliges, se abre un reloj, y si no
pagas se libera para el siguiente.

```
              [DISPONIBLE]
                   │
                   │  el cliente pulsa "Apartar"
                   │  n8n lee availableQuantity; si > 0 → Update Inventory −1
                   ▼
              [APARTADO]                    ⏱ arranca el reloj de 24 h
         se crea la oportunidad · se manda la liga de pago
                   │
        ┌──────────┴──────────┐
        │                     │
     paga                  vence sin pagar
        │                     │
        ▼                     ▼
    [VENDIDO]             [LIBERADO]
  el stock ya estaba      n8n → Update Inventory +1
  descontado: no se       se le avisa al cliente
  toca nada más          que se liberó
```

### Por qué n8n es dueño único del contador

**La venta no pasa por ningún checkout de tienda.** El agente arma el pedido, y n8n
aparta y, en la misma corrida, crea la factura con la API de Invoices de GHL: esa
factura es la **liga de pago**. Como
GHL sólo descuenta stock en órdenes de su tienda, y aquí no hay ninguna, **nadie
más toca el contador**. n8n descuenta al apartar y devuelve al vencer. Punto.

Eso elimina dos bugs que tenía el diseño de la revisión 4:

| Bug | Qué pasaba |
|---|---|
| **Doble descuento** | n8n descontaba al apartar y GHL volvía a descontar al completarse la orden de la tienda |
| **La última paca no se podía pagar** | Si alguien apartaba la última unidad, n8n la bajaba a 0 y la tienda se la mostraba agotada **a esa misma persona** cuando iba a pagar |

El segundo era el grave. Sacar el cobro de la tienda los elimina de raíz.

### Recordatorios

A las **12 h** y a las **2 h** de vencer. Los dos caen fuera de la ventana de 24 h
de WhatsApp, así que necesitan plantilla aprobada por Meta.

### El choque con el efectivo — sólo si hay OXXO

Depende de la validación 4: Stripe abre OXXO a cuentas de EE.UU., pero el checkout de
GHL con Stripe no lo lista oficialmente. Si aparece, el efectivo tarda más que el
apartado de 24 h: el voucher de OXXO vale **5 días** y el pago acredita al siguiente
día hábil. Si el comprador elige efectivo:

- el apartado **se extiende hasta que venza el voucher** de Stripe, más un día hábil;
- el bot se lo dice al entregar el comprobante, para que no crea que tiene 24 h;
- OXXO no admite reembolsos ni contracargos, que encaja con la venta sin devoluciones.

Tarjeta se acredita al instante y no necesita la excepción. Si el checkout no muestra
OXXO ni SPEI, esta sección no aplica.

### Pagos fuera de Stripe

Tienen cuenta en un banco mexicano y reciben transferencias directas. Para ese caso
hay un formulario interno **"Registrar pago manual"** (`AP03`): se elige la orden, se
marca pagada y el workflow confirma la reserva y dispara el despacho.

> Ojo con la distinción: **lo que se paga en la liga se confirma solo.** El registro
> manual es únicamente para transferencias a su banco, fuera de la pasarela — y es el
> plan B para SPEI si el checkout de GHL no lo ofrece.

---

## 4. Los flujos de n8n

Sólo cinco, y ninguno lleva lógica de negocio pesada.

| Flujo | Entrada | Qué hace |
|---|---|---|
| `N1 · Apartar` | Acción Custom API del bot | Lee `availableQuantity`; si hay, descuenta 1, crea la factura en GHL por la API de Invoices y devuelve `liga_pago` e `invoice_id`. Si no, devuelve agotado |
| `N2 · Liberar vencidos` | Webhook desde `SP02`, **más** un cron de respaldo cada 15 min | Devuelve el stock con `Update Inventory`. Son dos caminos, no uno — ver abajo |
| `N3 · Buscar sucursal` | Acción Custom API del bot | Código postal → 2-3 sucursales cercanas (ver `06-logistica-envia.md`) |
| `N4 · Generar guía` | Webhook al confirmarse el pago | Crea la guía en Envia, devuelve PDF y número de rastreo |
| `N5 · Rastrear` | Cron / webhook de Envia | Actualiza el estatus y dispara el aviso al cliente |

> **`N1` corre serializado (concurrencia 1).** Si dos clientes apartan la última paca
> en el mismo segundo, un read-check-write concurrente puede dejar el stock en
> negativo. Serializando ese flujo el problema desaparece. Con 30 artículos y el
> volumen que esperan (500–800 al mes) alcanza de sobra.

### Los dos caminos para liberar, y por qué son dos

**El reloj vive en GHL, no en n8n.** La cadena de `Wait` de `SP02` —12 h, 10 h, 2 h—
es quien mide, y al vencer le avisa a `N2` cuál apartado soltar. n8n no decide nada:
ejecuta. Por eso **n8n se queda sin estado**, que es lo que corresponde a un servicio
que sólo se consulta.

El **cron cada 15 minutos es una barredora**, no el mecanismo principal. Existe para
un caso concreto: si la cadena de `SP02` se rompe a media ejecución —contacto
borrado, workflow editado mientras corría, un tropiezo de GHL— ese apartado no se
libera nunca y esa paca queda muerta en el inventario sin que nadie se entere. Es una
fuga silenciosa de stock, y el cron es lo único que la atrapa.

Para saber qué barrer, el cron lee **`expira_en`, un campo de texto en GHL** — no un
`Date`, que descarta la hora. Es el mismo precedente de `fecha_pago`.

> **El riesgo de tener dos caminos: que ambos suelten el mismo apartado y el stock
> suba +2.** Es el espejo exacto del doble descuento que ya eliminamos. El seguro es
> `estado_apartado`: soltar **sólo si sigue en `apartado`**, y ponerlo en `vencido` en
> el mismo paso. Ese check-and-set tiene que pasar por el **mismo flujo serializado de
> `N1`**, o dos procesos leen `apartado` a la vez y suman los dos.

---

## 5. Cobro con Stripe

**El Stripe del cliente** (entidad de EE.UU.), conectado por él en Pagos →
Integraciones de Greentex. No hay middleware ni webhook que interpretar. La subcuenta
va en **MXN**: GHL no convierte moneda, Stripe presenta en pesos y liquida en dólares.

**La liga es una factura de GHL, y la pide `N1`.** El agente captura qué quiere el
cliente; `N1` confirma que hay stock, lo aparta y en la misma corrida crea la factura
con la API de Invoices —producto, cantidad, contacto— y le devuelve al agente
`liga_pago` e `invoice_id`. El monto sale del producto; el cobro sale por Stripe
porque está conectado a nivel cuenta. **n8n nunca toca Stripe**: le pide una factura a
GHL, y GHL cobra. La acción de workflow «Send Invoice» no sirve para esto porque exige
una plantilla fija; la API sí toma producto y cantidad en cada llamada.

Métodos:

| Método | Estado | Acreditación |
|---|---|---|
| Tarjeta de crédito o débito | Confirmado en GHL | Inmediata |
| Transferencia SPEI | Por validar (4) | Inmediata |
| Efectivo en OXXO | Por validar (4) | Siguiente día hábil; voucher de 5 días; sin reembolsos |

Stripe abre OXXO y transferencia MX a cuentas de EE.UU., pero el checkout de GHL con
Stripe lista tarjeta, Apple/Google Pay, Klarna, iDEAL, SEPA y Link — no OXXO ni SPEI
(artículo de HighLevel, feb 2026). Si no aparecen, el plan B es tarjeta por la liga y
transferencia manual con `AP03`.

**El Goal Event `Payment Received` sí funciona**, porque la factura es un pago de GHL.
Los workflows de confirmación se disparan solos.

---

## 6. Despacho y rastreo

```
  Pago confirmado
        │
        ├──► n8n genera la guía en Envia.com
        │         │
        │         ├──► PDF de la etiqueta al ALMACÉN por WhatsApp
        │         │    (nombre · cantidad · destino · CP — nunca el dinero)
        │         │
        │         └──► programa la recolección en Nuevo Laredo
        │
        └──► correo a los DUEÑOS con la orden completa, incluido el monto
                  │
        Envia rastrea el paquete y n8n dispara los avisos:
          "va en camino" → "llegó a tu sucursal, ya puedes recogerlo"
```

Este reparto sale textual de la primera llamada: *"un correo con detalle a ustedes y
un whatsapp simple al almacén que llegue con número de orden y la pieza, y la
dirección"*. Y Miguel lo reforzó en la segunda: **el almacén no ve dinero.**

> **El aviso de "ya llegó a tu sucursal" es el mensaje más valioso del sistema.**
> Con servicio a ocurre el cliente tiene que ir físicamente por su paquete. Pamela
> describió el dolor exacto: *"oye, no me llegó y que no sé qué. Y ahí, órale, a
> rastrear."*

---

## 7. Qué hay que validar en la cuenta antes de construir

Regla de oro del playbook: *"se guardó" no es "funciona"*. **Cinco** supuestos de este
diseño dependen del comportamiento real de GHL y hay que probarlos en cuenta antes de
dar por bueno el flujo. La numeración es la misma que en `docs/11-cronograma.md` y
`docs/13-accesos.md`, y no se cambia:

1. Que una **factura creada por API cobre con Stripe.** Hay que verla cobrar y ver el
   formato de la liga que devuelve: es el supuesto que sostiene todo el diseño.
2. Que **pagar una liga no descuente stock solo.** Si lo hiciera, vuelve el doble
   descuento y n8n dejaría de ser dueño único del contador.
3. Que **`N1` responda en menos de 10 s**, el límite de la acción Custom API de
   Conversation AI. Necesita `N1` vivo, así que va en la semana 2.
4. Que el checkout de GHL **muestre OXXO y SPEI**, y que `Payment Received` dispare
   igual con cada método que muestre.
5. Que **Conversation AI con Custom API funcione en el canal de WhatsApp** y que la KB
   responda del catálogo. Prueba de humo en la semana 1. La mitad ya se vio el 25 sep
   en el probador del bot con un endpoint falso; falta verlo por WhatsApp.

**Plan B si falla la prueba 1:** cobrar por el checkout de la tienda y renunciar al
apartado de 24 h, porque ahí sí chocan. Conviene saberlo antes de prometer el
apartado, no después.
