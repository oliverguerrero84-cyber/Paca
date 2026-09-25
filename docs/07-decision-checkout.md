# Decisión: el cobro va por liga de pago, no por la tienda

> Registro de la decisión del 16 de septiembre. Nació de una duda de Oliver sobre
> si el link del checkout se podía mandar por WhatsApp sin que se rompiera, y
> terminó cambiando la arquitectura de la revisión 4.

---

## 1. La duda original y su respuesta

**Pregunta:** si el cliente arma su carrito en la tienda y lo abandona, ¿se puede
extraer ese link de checkout y mandárselo por WhatsApp? ¿O llegaría corrompido por
depender de la sesión del navegador?

**Respuesta: el link sí es portable.** La documentación de HighLevel es explícita:

> *"works across devices, browsers, and sessions"* — con *"cross-device access"* y
> sin atadura a sesión ni credenciales de login.

El merge field es `{{ecom_checkout_page_url}}`. Tiene sentido: el rescate de
carritos abandonados se manda por correo desde siempre, y eso sólo funciona si el
link abre en otro dispositivo.

**Pero al investigarlo salieron tres cosas que nos sacan de ese camino:**

| Hallazgo | Por qué importa |
|---|---|
| El carrito abandonado nativo manda **una sola notificación** por abandono | No alcanza para la cadencia de recordatorios del apartado (12 h y 2 h) |
| Requiere que el cliente **haya escrito su email** en el checkout | Si sólo mira y se va, no hay evento ni link que mandar |
| **Invoices y Payment Links** son lo que HighLevel documenta para cobrar con Stripe; la tienda no se necesita | Cobrar por la tienda agrega una pieza que no hace falta |

---

## 2. La pregunta de fondo

Oliver la formuló mejor que la duda original:

> *"Si la gente está hablando en WhatsApp, ¿qué tiene que ver la tienda de GHL?"*

Tiene razón. Mandar a una tienda es fricción para un público que Mauricio describió
como *"gente que se dedica toda su vida al negocio informal; muchas veces no saben
cómo escribir bien, no saben cómo usar muy bien el teléfono, las redes"*.

**La conversación es el catálogo.** El agente manda fotos y videos por WhatsApp, que
es exactamente lo que pidieron en la junta. La tienda sale del camino de venta.

---

## 3. Quién hace qué

### El asistente — uno solo, en Conversation AI de GHL

No dos asistentes, y ninguno en n8n. Hasta el 25 sep era Agent Studio; ese día se
cambió a Conversation AI, y la razón está en la primera fila.

| Por qué Conversation AI | |
|---|---|
| **Tiene la acción Custom API** | Le pregunta a n8n *dentro del mismo turno*, con 10 s de límite. Se probó el 25 sep. Era lo único que sólo Agent Studio podía hacer, y ya no |
| **Es más simple** | Un prompt, la KB y tres acciones, en vez de 19 nodos con router y capturas. Menos que construir a mano y menos que se rompa |
| **Dos asistentes se estorban** | El playbook lo documenta: un Transfer Bot con condición agresiva **roba el primer turno** y las capturas no se ejecutan |

### n8n — tres trabajos, ninguno conversacional

1. **Validar y apartar stock** — lee y escribe `availableQuantity` en GHL
2. **Buscar sucursales** por código postal — Envia `carrier-branches` + `validate-zip-code`
3. **Generar guías y rastrear** — Envia `ship/generate`, `ship/pickup`, `ship/track`

> **n8n nunca habla con el cliente y nunca toca Stripe.** Le pide la factura a GHL por
> API, y GHL cobra. Es un servicio que el agente consulta, no un participante de la
> conversación.

### GHL — la conversación, el cobro y el registro

Y aquí está el nudo que faltaba resolver: **si Stripe vive en GHL, ¿quién genera la
liga?**

**La genera GHL, a petición de n8n.** La acción de workflow «Send Invoice» exige una
plantilla fija, así que no sirve por SKU y cantidad; la API de Invoices sí:

```
  Agente captura SKU y cantidad
        │
        ├─► Custom API → n8n N1: ¿hay stock? → n8n lee GHL, aparta, y crea la
        │                                       factura con la API de Invoices
        │                                       (producto, cantidad, contacto, MXN)
        ▼
  n8n devuelve liga_pago e invoice_id en el mismo turno
        │     el monto sale del producto de GHL
        │     el cobro sale por Stripe, conectado a nivel cuenta
        ▼
  El agente manda la liga por WhatsApp
```

n8n pidió la factura y la entregó. Nunca tocó un peso: cobra GHL.

---

## 4. Dónde vive el stock: en GHL, no en un Sheet

**Las ligas de pago necesitan los productos de GHL de todos modos**, porque ahí vive
el precio. Si el stock está en el mismo producto, hay una sola fuente de verdad en
lugar de dos que sincronizar.

Y trae un beneficio que resuelve dos bugs de la revisión 4:

> **Como el cobro ya no pasa por el checkout de la tienda, GHL nunca descuenta stock
> por su cuenta.** n8n es dueño absoluto del contador.

| Bug que desaparece | Qué pasaba |
|---|---|
| **Doble descuento** | n8n descontaba al apartar y GHL volvía a descontar al pagarse la orden de la tienda |
| **La última paca no se podía pagar** | Si alguien apartaba la última unidad, n8n la bajaba a 0 y la tienda se la mostraba agotada **a esa misma persona** al ir a pagar |

El segundo era peor que el primero y no lo había visto. Sacar el cobro de la tienda
elimina los dos de raíz.

---

## 5. El flujo completo

```
 1. Llega por WhatsApp (campañas de Meta e Instagram)
 2. El agente atiende: calidades, tallas, qué trae, peso, fotos y videos
 3. Detecta intención de compra → captura SKU y cantidad
 4. Custom API → n8n valida stock contra GHL                  ── n8n
 5. El agente pide CÓDIGO POSTAL — cinco dígitos
 6. Custom API → n8n devuelve 2-3 sucursales cercanas         ── n8n + Envia
 7. El cliente elige de la lista (nunca escribe la sucursal)
 8. n8n APARTA: availableQuantity −1 · arranca el reloj de 24 h
 9. n8n crea la factura en GHL; el agente manda la liga      ── n8n + GHL
10. El cliente paga con tarjeta (OXXO y SPEI, si el checkout los muestra)
11. Payment Received confirma la venta
12. n8n genera la guía y programa la recolección              ── n8n + Envia
13. La etiqueta en PDF llega al almacén, sin el monto
14. n8n rastrea hasta "ya llegó a tu sucursal"                ── n8n + Envia
```

**El cliente sale de WhatsApp una sola vez: para pagar.** Y vuelve solo.

---

## 6. Qué hay que probar antes de prometerlo

Regla de oro del playbook: *"se guardó" no es "funciona"*. Tres pruebas en una
cuenta real antes de comprometer esto con el cliente:

| # | Qué probar | Por qué importa |
|---|---|---|
| 1 | Que una **factura creada por API cobre con Stripe** | Es el supuesto que sostiene todo el diseño. Hay que verla cobrar y ver el formato de la liga |
| 2 | Que **pagar una liga no descuente stock solo** | Si lo descontara, vuelve el doble descuento |
| 3 | Que **`N1` responda en menos de 10 s**, el límite de la acción Custom API | Si tarda, la acción falla y la conversación se siente trabada |

### Plan B si falla la prueba 1

Cobrar por el checkout de la tienda y **renunciar al apartado de 24 h**, porque ahí
sí chocan: quien aparta la última paca no puede pagarla. Conviene saberlo antes de
prometer el apartado, no después.

---

## 7. Qué queda de la tienda

**Catálogo opcional, sólo como destino de publicidad.** No tienen Instagram ni
TikTok, así que hoy los leads sólo pueden llegar por el número de WhatsApp. Una
página pública con los 30 artículos les da a dónde mandar los anuncios.

No cobra, no arma carritos y no descuenta stock. Cada artículo lleva un botón que
abre WhatsApp con el SKU precargado, para que el agente ya sepa de qué le preguntan.
