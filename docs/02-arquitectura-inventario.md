# Arquitectura de inventario, apartado y cobro

Cómo se resuelve lo que GHL no puede hacer solo.

---

## 1. Diagrama general

```
  Canales: WhatsApp API · Instagram · Facebook · TikTok · Widget web
                              │
                              ▼
  ┌───────────────────────────────────────────────────────┐
  │  GHL                                                  │
  │  CRM · Conversaciones · Workflows · Agent Studio      │
  └───────────────────────────────────────────────────────┘
        │  webhook saliente          ▲  inbound webhook
        ▼  (no espera respuesta)     │  (n8n responde por acá)
  ┌───────────────────────────────────────────────────────┐
  │  n8n — el motor                                       │
  │  aritmética · reservas · nº de orden · Mercado Pago    │
  └───────────────────────────────────────────────────────┘
        │                                    │
        ▼                                    ▼
  Google Sheets                        Mercado Pago
  (fuente de verdad del stock)      (Checkout Pro + IPN)
```

**Por qué n8n en el medio:** GHL no hace aritmética en campos numéricos
(`ghl-limitations.md`), así que no puede restar una paca del stock. Y su webhook
saliente **no espera respuesta**, así que todo ida y vuelta es asíncrono.

---

## 2. Google Sheets — la fuente de verdad

Cuatro pestañas. Plantillas listas en `data/`.

### `STOCK` — 30 filas, una por SKU

| Columna | Quién la escribe |
|---|---|
| `sku`, `nombre_display`, `temporada`, `categoria`, `calidad` | Fijas, del catálogo |
| `precio_menudeo_mxn` | **Los dueños** ⚠️ pendiente |
| `piezas_aprox` | **Los dueños** ⚠️ pendiente |
| `disponible` | Los dueños al cargar; n8n al reservar y liberar |
| `apartado` | Sólo n8n |
| `vendido_hist` | Sólo n8n |
| `activo` | Los dueños (SI/NO — saca un SKU del bot sin borrarlo) |

**`disponible` es únicamente la porción asignada a menudeo.** El mayoreo nunca entra
a este Sheet. Cuando los dueños mueven pacas de un lado al otro, editan la celda a
mano — ese es exactamente el "híbrido" que pidieron:

> "Ustedes tendrían que poner que ustedes por aparte, por fuera vendieron 500."

### `APARTADOS` · `ORDENES` · `CONFIG`

`APARTADOS` y `ORDENES` las escribe **sólo n8n** — nadie las toca a mano, salvo la
columna `guia` de `ORDENES`, que el almacén llena vía formulario GHL.
`CONFIG` guarda los parámetros del sistema (horas de apartado, costo de envío,
WhatsApp del almacén, correo de los dueños).

> **Protección:** todas las pestañas protegidas salvo las columnas que los dueños
> sí deben editar (`disponible`, `precio_menudeo_mxn`, `piezas_aprox`, `activo`).
> Es la mitigación del riesgo #4: que alguien rompa una fórmula sin darse cuenta.

---

## 3. Máquina de estados del apartado

Lo que el cliente pidió como *"guardar la pieza 24 horas"*:

```
              [disponible]
                   │
                   │  el bot arma el pedido → n8n reserva
                   ▼
              [apartado]                      ⏱ arranca el reloj de 24 h
         disponible −1 · apartado +1
                   │
        ┌──────────┴──────────┐
        │                     │
     paga                  vence sin pagar
        │                     │
        ▼                     ▼
    [pagado]              [liberado]
  apartado −1            apartado −1
  vendido_hist +1        disponible +1
```

**Por qué dos contadores y no uno:** si sólo se restara de `disponible`, una paca
apartada y no pagada quedaría invisible para siempre. Con `apartado` separado, los
dueños ven en todo momento cuántas pacas están comprometidas pero sin cobrar — que
es justo el dolor que describieron:

> "Muchas veces los pagos no son inmediatos. O sea, mucha gente de repente dice
> 'ah, bueno, sí, quiero tantas y tantas y te pago al rato'. 'Ay, sí, se me pasó el
> rato, voy mañana'."

**Recordatorios** durante la ventana: a las 12 h y a las 2 h de vencer.
Ambos requieren template aprobado por Meta (caen fuera de la ventana de 24 h de WhatsApp).

---

## 4. Flujos de n8n

| Flujo | Entrada | Qué hace | Salida |
|---|---|---|---|
| `N1 · Consultar stock` | API Call del agente (nodo 9) | Lee `STOCK`, filtra por SKU, devuelve `disponible` | Respuesta directa al agente |
| `N2 · Crear apartado` | API Call del agente (nodo 14) | Verifica stock, `disponible −1`, `apartado +1`, genera `orden_id`, calcula `expira_en` | Inbound Webhook → GHL (dispara SP02) |
| `N3 · Generar liga de pago` | API Call del agente (nodo 16) | Crea preferencia en Checkout Pro con el monto de `CONFIG` | Devuelve la liga + guarda `mp_preference_id` |
| `N4 · Confirmar pago` | Webhook IPN de Mercado Pago | Valida el pago, `apartado −1`, `vendido_hist +1`, marca la orden pagada | Inbound Webhook → GHL (dispara SP04) |
| `N5 · Liberar vencidos` | Cron cada 15 min | Busca apartados con `expira_en` pasado y estado `apartado`; `apartado −1`, `disponible +1` | Inbound Webhook → GHL (dispara recuperación) |

> **`N2` corre en modo cola con concurrencia 1.** Google Sheets no tiene
> transacciones: si dos clientes apartan la última paca al mismo tiempo, un
> read-check-write concurrente puede dejar el stock en negativo. Serializando ese
> flujo el problema desaparece. Para 30 SKUs y volumen de menudeo alcanza de sobra.
> Si el volumen crece, la ruta de escape es mover `STOCK` a Supabase o Airtable y
> usar un update atómico — el resto de la arquitectura no cambia.

> **`N5` existe porque el reloj no puede vivir en GHL.** Los campos `Date` de GHL no
> guardan hora, así que `expira_en` se calcula y se evalúa en n8n. El `Wait` de SP02
> es el camino feliz; `N5` es la red de seguridad que libera stock aunque el
> workflow de GHL se haya caído o el contacto haya salido del flujo.

---

## 5. Cobro con Mercado Pago

```
  Agente (nodo 16) → n8n N3 → Checkout Pro API → liga de pago
                                                      │
                          GHL envía la liga por WhatsApp
                                                      │
                                              cliente paga
                                                      │
                          Mercado Pago → webhook IPN → n8n N4
                                                      │
                          Inbound Webhook → GHL → SP04 → despacho
```

> ⚠️ **El Goal Event `Payment Received` de GHL no sirve acá.** Sólo dispara con
> pagos procesados por GHL. Con Mercado Pago el trigger es un **Inbound Webhook**.
> Es el error más fácil de cometer en la construcción y deja el flujo de
> confirmación sin ejecutarse nunca.

Mercado Pago funciona como wallet: recibe y aloja el dinero, y de ahí se transfiere
a la cuenta bancaria mexicana que el cliente ya tiene. Antes del go-live necesitan
la cuenta **verificada** — sin las verificaciones de identidad y fiscales, Mercado
Pago retiene fondos según el flujo recibido. Ya salió en la llamada; hay que
enviarles los requisitos.

---

## 6. Despacho y tracking

```
  Pago confirmado
        │
        ├──► WhatsApp al ALMACÉN:  nº de orden · SKU · cantidad · ciudad · sucursal
        │
        └──► Email a los DUEÑOS:   orden completa · cliente · monto · SKU · destino
                │
        el almacén prepara y lleva a Paquete Express
                │
        abre el formulario GHL (con orden_id precargado) y escribe la guía
                │
        Form Submitted → workflow AP01 → WhatsApp al cliente con su guía
```

Este reparto sale textual de la llamada:

> "Un correo con detalle a ustedes y un whatsapp simple al almacén que llegue con
> número de orden y la pieza, o sea qué pieza es y ya, y la dirección."

**El único paso manual de todo el sistema es escribir el número de guía.** Es
inevitable: Paquete Express no tiene API pública.
