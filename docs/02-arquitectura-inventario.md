# Arquitectura de inventario, apartado y cobro

> **Reescrito en la revisión 4.** Las versiones anteriores ponían el stock en Google
> Sheets porque dábamos por hecho que GHL no sabía llevar inventario. **Era falso:**
> la tienda de GHL tiene control de stock nativo y un endpoint `Update Inventory`.
> El stock ahora vive en GHL, donde el cliente lo ve, y n8n queda reducido a una
> sola función: ser el reloj del apartado.

---

## 1. Diagrama general

```
  Campañas Meta e Instagram ──► WhatsApp (único canal de entrada)
                                      │
                                      ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  GHL                                                          │
  │  CRM · Agente de ventas · Tienda con los 30 artículos         │
  │  Inventario nativo · Mercado Pago nativo · Workflows          │
  └──────────────────────────────────────────────────────────────┘
        │  webhook                          ▲  inbound webhook
        ▼                                   │
  ┌──────────────────────────────────────────────────────────────┐
  │  n8n — dos trabajos, nada más                                 │
  │  1. El reloj del apartado (Update Inventory ±1)               │
  │  2. El puente con Envia.com (guía, recolección, rastreo)      │
  └──────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    Envia.com ──► Paquete Express
```

**Lo que cambió:** Mercado Pago y el inventario salieron de n8n y entraron a GHL.
n8n ya no es el motor del sistema, es un temporizador y un traductor.

---

## 2. Dónde vive cada cosa

| Dato | Dónde vive | Quién lo escribe |
|---|---|---|
| Catálogo de los 30 artículos | Productos de GHL | Se carga una vez; los dueños editan precios |
| **Stock disponible** | `availableQuantity` del producto en GHL | Los dueños al reponer; n8n al apartar y liberar |
| Apartados vigentes | Oportunidades del pipeline + campos custom | Los workflows |
| Pagos | Mercado Pago nativo, dentro de GHL | Mercado Pago |
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

### El detalle que evita un bug caro

**La venta NO pasa por el checkout de la tienda.** Va por una **liga de pago de
Mercado Pago atada a la reserva**. Si pasara por el checkout, GHL descontaría stock
otra vez al completarse la orden y la pieza quedaría en doble baja.

La tienda cumple dos funciones y ninguna es cobrar: **vitrina** con fotos y videos,
y **semáforo de disponibilidad real** (porque lee el mismo `availableQuantity` que
n8n escribe).

### Recordatorios

A las **12 h** y a las **2 h** de vencer. Los dos caen fuera de la ventana de 24 h
de WhatsApp, así que necesitan plantilla aprobada por Meta.

### El choque con el efectivo

Los pagos en OXXO y Paycash tardan **hasta 72 horas hábiles** en acreditarse — más
que el apartado de 24 h. Si el comprador elige efectivo:

- el apartado **se extiende hasta que venza la referencia** de Mercado Pago;
- el bot se lo dice al entregar el comprobante, para que no crea que tiene 24 h.

Tarjeta y SPEI se acreditan al instante y no necesitan la excepción.

### Pagos fuera de Mercado Pago

Tienen cuenta en un banco mexicano y reciben transferencias directas. Para ese caso
hay un formulario interno **"Registrar pago manual"**: se elige la orden, se marca
pagada y el workflow confirma la reserva y dispara el despacho.

> Ojo con la distinción: **OXXO y SPEI dentro de Mercado Pago se confirman solos.**
> El registro manual es únicamente para transferencias a su banco, fuera de la
> pasarela.

---

## 4. Los flujos de n8n

Sólo cinco, y ninguno lleva lógica de negocio pesada.

| Flujo | Entrada | Qué hace |
|---|---|---|
| `N1 · Apartar` | Webhook desde GHL | Lee `availableQuantity`; si hay, descuenta 1 y devuelve OK. Si no, devuelve agotado |
| `N2 · Liberar vencidos` | Cron cada 15 min | Busca apartados vencidos y devuelve el stock con `Update Inventory` |
| `N3 · Buscar sucursal` | API Call del agente o del checkout | Código postal → sucursales cercanas (ver `06-logistica-envia.md`) |
| `N4 · Generar guía` | Webhook al confirmarse el pago | Crea la guía en Envia, devuelve PDF y número de rastreo |
| `N5 · Rastrear` | Cron / webhook de Envia | Actualiza el estatus y dispara el aviso al cliente |

> **`N1` corre serializado (concurrencia 1).** Si dos clientes apartan la última paca
> en el mismo segundo, un read-check-write concurrente puede dejar el stock en
> negativo. Serializando ese flujo el problema desaparece. Con 30 artículos y el
> volumen que esperan (500–800 al mes) alcanza de sobra.

---

## 5. Cobro con Mercado Pago

**Nativo desde abril de 2026.** Se conecta en Pagos → Integraciones con Public Key y
Access Token. No hay middleware, no hay webhook IPN que interpretar, no hay n8n.

Un solo checkout cubre los tres métodos que pidieron en la junta:

| Método | Acreditación |
|---|---|
| Tarjeta de crédito o débito | Inmediata |
| Transferencia SPEI | Inmediata |
| Efectivo en OXXO o Paycash | Hasta 72 h hábiles |

**El Goal Event `Payment Received` sí funciona**, porque el pago es un pago de GHL.
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

Regla de oro del playbook: *"se guardó" no es "funciona"*. Tres supuestos de este
diseño dependen del comportamiento real de GHL y hay que probarlos con una venta de
prueba antes de dar por bueno el flujo:

1. Que `Update Inventory` se refleje de inmediato en la disponibilidad de la tienda.
2. Que una liga de pago de Mercado Pago **no** descuente stock por su cuenta.
3. Que `Payment Received` dispare igual con los tres métodos, incluido el efectivo.
