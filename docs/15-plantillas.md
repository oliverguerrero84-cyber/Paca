# Las 6 plantillas de mensaje

> **Listas para copiar y pegar.** Las cuatro primeras necesitan aprobación de Meta, que
> tarda de 24 a 48 horas y **es el único plazo del proyecto que no controlamos**. Se
> mandan a cola el mismo día que exista la WhatsApp Business Account (`A4`).
>
> El tono sale del Global Prompt de `docs/01-mapa-ghl.md` §3: cercano y mexicano, sin
> tecnicismos. Y la regla 2 aplica aquí también: **la calidad baja se llama Especial**,
> nunca «económica».

---

## Por qué existen

WhatsApp sólo deja escribirle libremente a alguien **dentro de las 24 horas** desde su
último mensaje. Fuera de esa ventana hace falta una plantilla aprobada. Y casi todo lo
que manda este sistema cae fuera: el recordatorio del apartado llega horas después, el
pago se acredita cuando el cliente va al OXXO, la guía se genera al día siguiente.

Por eso **son plantillas y no mensajes normales**.

## Lo que decide si Meta las aprueba

Meta clasifica cada plantilla y la categoría cambia el precio y la probabilidad de
rechazo:

- **UTILITY** — avisa sobre una transacción que el cliente ya inició. Es lo que
  queremos: más barata y se aprueba casi siempre.
- **MARKETING** — promueve, invita a comprar, ofrece. Más cara, y si una UTILITY trae
  lenguaje promocional, Meta la recategoriza o la rechaza.

Las cuatro de abajo están escritas como avisos de estado, a propósito.

---

## 1 · Recordatorio de apartado por vencer

**Categoría: UTILITY** · La dispara `SP02` unas horas antes de que venza el reloj.

```
Hola {{1}}, tu apartado de {{2}} vence hoy a las {{3}}.

Si ya no la quieres, no hagas nada: la paca se libera sola y no hay ningún cargo.

Si sí, aquí está tu liga para pagar: {{4}}
```

| Variable | Campo | Ejemplo |
|---|---|---|
| `{{1}}` | nombre del contacto | Laura |
| `{{2}}` | `articulo_apartado` | MUJER VERANO BOUTIQUE |
| `{{3}}` | `expira_en` | 6:30 p.m. |
| `{{4}}` | `liga_pago` | (la liga que crea `SP03`) |

> **«No hagas nada y no hay ningún cargo» va a propósito.** Quita la ansiedad de que
> apartar comprometa a algo, que es justo lo que frena a un comprador primerizo. Y de
> paso deja claro que el apartado no cobra nada por adelantado.

## 2 · Confirmación de pago

**Categoría: UTILITY** · La dispara `SP04` con el Goal Event `Payment Received`.

```
¡Listo {{1}}! Ya recibimos tu pago de ${{2}} MXN.

Tu orden {{3}} pasa a preparación. En cuanto salga del almacén te mandamos el número de guía para que la sigas.
```

| Variable | Campo | Ejemplo |
|---|---|---|
| `{{1}}` | nombre del contacto | Laura |
| `{{2}}` | `monto_apartado` | 6,300 |
| `{{3}}` | `orden_id` | ORD-1042 |

## 3 · Orden enviada con número de guía

**Categoría: UTILITY** · La dispara `SP05` cuando Envia genera la guía.

```
{{1}}, tu paca ya va en camino.

Guía: {{2}}
Paquetería: Paquete Express
La recoges en: {{3}}

Te avisamos en cuanto llegue a la sucursal. Llévate una identificación.
```

| Variable | Campo | Ejemplo |
|---|---|---|
| `{{1}}` | nombre del contacto | Laura |
| `{{2}}` | `numero_guia` | 7712345678 |
| `{{3}}` | `sucursal_ocurre` | Paquete Express Mérida Centro |

> **«Llévate una identificación»** evita el viaje perdido: con servicio a ocurre la
> sucursal la pide y mucha gente no lo sabe.

## 4 · Apartado vencido

**Categoría: UTILITY** · La dispara `SP02` cuando el reloj llega a cero y `N2` libera el
stock.

```
{{1}}, tu apartado de {{2}} venció y la paca volvió a estar disponible.

Si todavía la quieres, contéstanos por aquí y la revisamos.
```

| Variable | Campo | Ejemplo |
|---|---|---|
| `{{1}}` | nombre del contacto | Laura |
| `{{2}}` | `articulo_apartado` | MUJER VERANO BOUTIQUE |

> ⚠️ **Ésta es la que se puede rechazar.** En el mapa se llama «vencido /
> recuperación», y ahí está el riesgo: si invita a comprar —una oferta, un descuento,
> una prisa— Meta la manda a MARKETING. Escrita como aviso de estado, pasa como
> UTILITY.
>
> **Si la rechazan, la línea que hay que quitar es la segunda.** El aviso solo basta:
> el cliente contesta y con eso abre la ventana de 24 horas para hablar libremente.

## 5 · Correo del detalle de la orden a los dueños

**Sin aprobación de Meta** — es correo. La dispara `SP05`.

**Asunto:** `Orden {{orden_id}} — {{articulo_apartado}} — {{ciudad}}, {{estado_mx}}`

```
Nueva orden pagada.

Orden:      {{orden_id}}
Cliente:    {{nombre}} · {{telefono}}
Artículo:   {{articulo_apartado}} ({{sku_apartado}})
Cantidad:   {{cantidad_apartada}}
Monto:      ${{monto_apartado}} MXN
Pagado:     {{fecha_pago}}

Destino:    {{ciudad}}, {{estado_mx}} · CP {{codigo_postal}}
Sucursal:   {{sucursal_ocurre}}
Guía:       {{numero_guia}}
```

Va a `email_duenos`, que hoy está en `PENDIENTE` hasta que el cliente lo mande.

## 6 · Orden al almacén

**Sin aprobación de Meta** — va al `whatsapp_almacen`, que es un número propio. La
dispara `SP05` junto con el PDF de la etiqueta.

```
Orden {{1}}

{{2}} — {{3}} paca(s)
Destino: {{4}}, {{5}} · CP {{6}}
Sucursal: {{7}}

Etiqueta adjunta. Imprimir y pegar.
```

| Variable | Campo | Ejemplo |
|---|---|---|
| `{{1}}` | `orden_id` | ORD-1042 |
| `{{2}}` | `articulo_apartado` | MUJER VERANO BOUTIQUE |
| `{{3}}` | `cantidad_apartada` | 1 |
| `{{4}}` | `ciudad` | Mérida |
| `{{5}}` | `estado_mx` | Yucatán |
| `{{6}}` | `codigo_postal` | 97000 |
| `{{7}}` | `sucursal_ocurre` | Paquete Express Mérida Centro |

> 🔴 **Aquí nunca va el monto.** Regla dura del diseño, textual de Miguel sobre el
> almacén: *"ellos no tienen por qué enterarse"*. Ni `monto_apartado`, ni el precio, ni
> nada que se le parezca.

---

## Dos cosas técnicas al darlas de alta

**La liga de pago va en el cuerpo, no en un botón.** Meta permite botones de URL
dinámica, pero sólo dejan variar el **final** de una dirección fija. La liga la genera
Mercado Pago o GHL con su propio dominio y su propio identificador, así que no encaja
en ese molde. Como variable de texto funciona siempre.

**Dos campos que no existían y se crearon para esto** (24 sep): `articulo_apartado` y
`codigo_postal`. El primero porque `sku_apartado` guarda la clave (`PV-MUJ-BOU`) y
ningún mensaje al cliente puede decir *"tu apartado de PV-MUJ-BOU"*. El segundo porque
`SP05` manda el CP al almacén y la regla 8 del Global Prompt obliga a pedirlo, pero no
tenía dónde vivir. Los dos están en `docs/01-mapa-ghl.md` §4 y ya creados en Greentex.
