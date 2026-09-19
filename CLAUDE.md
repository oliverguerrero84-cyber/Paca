# Proyecto Paca — instrucciones para Claude Code

Automatización del **menudeo** de un negocio de **pacas de ropa americana** de 100 lb
(Pamela, Miguel y Mauricio Hernández — McAllen TX, almacén en Nuevo Laredo,
Tamaulipas). Lo construye **786 Marketing** sobre GoHighLevel. El **mayoreo queda
aparte y manual**, textual del cliente: *"mi mayoreo yo lo trabajo aparte, no se
entromete con mi menudeo"*.

**Si te acabas de incorporar, lee `docs/08-traspaso.md` antes de tocar nada.**

---

## Reglas duras

### Rama

Se trabaja y se empuja a **`claude/cool-dirac-4sht9y`**. Nunca a otra sin permiso
explícito.

### Precios cerrados (18 sep 2026)

| | Esencial | Completo |
|---|---:|---:|
| Implementación | **$2,899** | **$4,497** |
| Mensualidad | **$437** | **$637** |

### Lo interno nunca sale al documento del cliente

`propuesta/propuesta-paca.html` es lo único que ve el cliente. **Jamás** puede
contener:

- el piso de negociación (**$2,599** y **$4,300**) ni la holgura
- ninguna cifra en **pesos mexicanos**, ni el reparto con 786
- el **primer año** ($8,143 y $12,141) — se quitó a propósito para que la cifra anual
  no opaque la mensualidad
- datos de contacto de ningún tipo

Todo eso vive en `docs/04-precotizacion.md` y ahí se queda.

### Checklist del HTML

Está también en el comentario del `<style>` de la página, y no se negocia:

- **sin emojis** — los iconos son glifos CSS (`.gl`)
- **sin `transition: all`**
- **colores sólo desde `:root`** — cero hex, `rgb()` o `hsl()` sueltos
- estados de **`:focus-visible`**, **`:active`** y **`[disabled]`**
- **`prefers-reduced-motion`** respetado
- sin `{{marcadores}}` sin resolver
- la marca es **786 Marketing**; cero menciones a Omnia

### Verificar significa medir

No supongas que el responsivo está bien. Ábrelo en Chromium
(`/opt/pw-browsers/chromium`, Playwright ya está en `/opt/node22/lib/node_modules`) a
**320, 400, 560, 768 y 1280 px**, haz un `window.scrollTo(500, 0)` **de verdad** y
comprueba que `window.scrollX === 0`. Medir `scrollWidth` a secas da falsos positivos:
ya pasó una vez con la tabla comparativa y se coló un desbordamiento a 320 px.

---

## Dónde está cada cosa

| Ruta | Qué es |
|---|---|
| `docs/08-traspaso.md` | **Empieza aquí.** Estado, decisiones tomadas y lo que sigue |
| `docs/00-alcance-tecnico.md` | Qué se puede construir y qué lleva cada paquete |
| `docs/01-mapa-ghl.md` | Pipeline, workflows, agente de Agent Studio y landing |
| `docs/02-arquitectura-inventario.md` | Inventario, apartado de 24 h, concurrencia |
| `docs/03-catalogo-productos.md` | Los 30 SKUs — fuente de la Knowledge Base |
| `docs/04-precotizacion.md` | Números, margen y piso — **interno** |
| `docs/05-preguntas-cliente.md` | Lo que falta preguntarle al cliente |
| `docs/06-logistica-envia.md` | Envia.com: guías, recolección y rastreo |
| `docs/07-decision-checkout.md` | Por qué el cobro va por liga y no por la tienda |
| `docs/09-conversacion.md` | Cómo se llegó a cada decisión — **no es fuente de verdad** |
| `propuesta/propuesta-paca.html` | La propuesta que ve el cliente |
| `data/catalogo.csv` | 30 SKUs: 17 de verano, 13 de invierno |

---

## Decisiones cerradas — no las reabras sin razón nueva

1. **La venta vive en la conversación de WhatsApp; el cobro sale por liga de pago.**
   No por el checkout de la tienda. Ver `docs/07-decision-checkout.md`.
2. **El asistente es uno solo, en Agent Studio de GHL.** Su nodo `API Call` le permite
   consultar a n8n dentro del mismo turno. Dos bots en el mismo WhatsApp se pelean el
   primer turno.
3. **n8n nunca habla con el cliente y nunca toca Mercado Pago.** Sólo valida y aparta
   stock, busca sucursal por código postal, y genera guías y rastrea.
4. **El inventario vive en los productos de GHL**, con n8n como dueño único del
   contador.
5. **Mercado Pago es pasarela nativa de HighLevel** desde el 27 de abril de 2026, y
   México está entre los países soportados. Cubre tarjeta, OXXO y SPEI.

> Dos afirmaciones de revisiones viejas eran **falsas** y están corregidas: que
> Mercado Pago no era nativo, y que GHL no llevaba inventario. Si las encuentras
> repetidas en algún lado, son un error que quedó suelto.

---

## Cómo se escribe aquí

Los documentos y la propuesta están en **español de México**, dirigidos a gente que no
es técnica. Se explica qué cambia para el negocio, no cómo funciona por dentro. Sin
adornos y sin vender de más: si algo está por validar, se dice que está por validar.
