# Los 5 flujos de n8n

> ⚠️ **Escritos, no probados.** No existe todavía la instancia donde correrlos
> (eslabón `0.3` de `docs/13-accesos.md`). Se verificó la estructura y que los campos
> que leen y escriben existan de verdad en Greentex, **pero ninguno se ha ejecutado**.
> Los supuestos van marcados abajo y en notas dentro de cada flujo.

| Flujo | Entrada | Qué hace |
|---|---|---|
| `N1-apartar` | Webhook `POST /apartar` | Lee el stock del SKU; si alcanza, descuenta y arranca el reloj |
| `N2-liberar-vencidos` | Cron 15 min | Devuelve el stock de los apartados vencidos |
| `N3-buscar-sucursal` | Webhook `POST /buscar-sucursal` | Código postal → las 3 sucursales más cercanas, con `branch_code` |
| `N4-generar-guia` | Webhook `POST /generar-guia` | Genera la guía y programa la recolección |
| `N5-rastrear` | Cron 1 h | Empuja el estatus de vuelta a GHL |

## Antes de importar

### 1. Las dos credenciales

Se crean en n8n como **Header Auth** y los flujos las llaman por nombre. **Nunca van
dentro del JSON.** Al importar, n8n va a pedir que se reasignen — es normal, el campo
dice `REEMPLAZAR`.

| Nombre exacto | Header | Valor |
|---|---|---|
| `GHL · PIT Greentex` | `Authorization` | `Bearer pit-…` de la subcuenta |
| `Envia · API` | `Authorization` | `Bearer …` de Envia. **Sandbox y producción tienen llaves distintas** y cada una sólo sirve en su ambiente: se crean en `shipping-test.envia.com/settings/developers` o en `shipping.envia.com/settings/developers` |

### 2. Las variables de entorno

```
GHL_LOCATION_ID       = c9jj5uu1WZOIkwi6Vfj5
GHL_PIPELINE_ID       = 80QTHEK406nT2KJhQ6TZ
GHL_STAGE_APARTADO    = 4e1d2753-b967-4817-b3b2-2b0a42efa5c6
GHL_STAGE_ENVIADO     = 352335f2-4150-43a0-8067-737cbcd8695e
GHL_STAGE_ENTREGADO   = ba84ff53-246f-4f04-9547-acd6f6210292
GHL_WEBHOOK_RASTREO   = (el id del Inbound Webhook de AP01, cuando exista)
GHL_USER_ID           = 3gkfNTQTfUHvcUlxwLEs   # Oliver en Greentex; firma la factura al mandarla (N1)
GHL_INVOICE_URL_BASE  = https://link.korvance.com   # dominio de ligas de la agencia; Greentex no tiene dominio propio. Se confirma en la validación 1
HORAS_APARTADO        = 24

ENVIA_API_URL         = https://api-test.envia.com        # producción: https://api.envia.com
ENVIA_QUERIES_URL     = https://queries.test.envia.com   # producción: https://queries.envia.com

ALMACEN_NOMBRE   ALMACEN_CALLE   ALMACEN_NUMERO   ALMACEN_COLONIA
ALMACEN_CIUDAD   ALMACEN_ESTADO  ALMACEN_CP       ALMACEN_TELEFONO   ALMACEN_EMAIL
```

Los `ALMACEN_*` son el origen de los envíos: **Nuevo Laredo, Tamaulipas**. Los datos
exactos todavía no los tenemos.

### 3. `N1` corre serializado — concurrencia 1

**Esto no se ve en el JSON y es lo más importante de toda la carpeta.** Se configura en
*Settings → Concurrency* del flujo.

Sin eso, dos clientes apartando la última paca en el mismo segundo hacen un
read-check-write concurrente y el stock queda en negativo. Con 30 artículos y 500 a 800
envíos al mes, serializar `N1` no cuesta nada.

## Lo que respetan, y por qué

**Ninguno toca Stripe.** `N1` crea la factura en GHL por su API de Invoices y devuelve
la liga; quien cobra es GHL con la pasarela conectada. n8n valida stock, busca
sucursales y mueve guías. Es decisión cerrada.

**Ninguno le habla al cliente.** Los mensajes salen de GHL con sus plantillas
aprobadas. `N5` sólo empuja el estatus para que `AP01` decida qué mandar. Si n8n
escribiera por su cuenta, se saltaría la ventana de 24 horas de WhatsApp y el mensaje
no llegaría.

**`expira_en` va en ISO 8601 con offset**, siempre — `2026-09-25T18:30:00.000Z`. `N1`
lo escribe así y `N2` lo compara así. **`SP02` tiene que escribirlo igual**: si alguien
lo guarda como «25/09 6:30 pm», `N2` no puede compararlo y el apartado no se libera
nunca. Por eso el campo es `TEXT` y no `DATE`: los `DATE` de GHL no guardan hora.

**Al almacén nunca le va el monto.** `N4` devuelve los datos y `SP05` arma el mensaje;
en el cuerpo del envío no viaja ningún precio.

## Los supuestos, sin disimular

Escribir esto obligó a fijar cosas que nadie ha verificado. Están marcadas también
dentro de cada flujo:

| # | Supuesto | Dónde | Qué pasa si falla |
|---|---|---|---|
| 1 | **`availableQuantity` vive en el `price`, no en el `product`** | `N1`, `N2` | Cambia la URL del PUT. Se confirma al cargar los 30 productos |
| 2 | **El SKU se guarda en el campo `sku` del price** | `N1`, `N2` | Si no, hay que resolver por nombre de producto |
| ~~3~~ | ~~La URL base de Envia y sus parámetros~~ — **resuelto el 25 sep** con `scripts/probar-envia.py`: envíos en `api[-test].envia.com`, consultas en `queries[.test].envia.com`, códigos postales en `geocodes.envia.com`; la paquetería se llama `paquetexpress` | `N3`, `N4`, `N5` | — |
| ~~4~~ | ~~Que las sucursales traigan coordenadas~~ — **resuelto el 25 sep**: `branches/paquetexpress/MX?zipcode=` trae 5 de 5 con coordenadas, ya ordenadas por `distance` en km. Se quitó el cálculo de distancia | `N3` | — |
| ~~5~~ | ~~El esquema de `ship/generate`~~ — **resuelto el 25 sep**: guía generada en el sandbox con `ground` y con `ground_do` (a sucursal, exige `destination.branchCode`). Los errores llegan con HTTP 200 y `meta: "error"` | `N4` | — |
| ~~6~~ | ~~Los textos de estatus~~ — **resuelto a medias el 25 sep**: `generaltrack` devuelve un catálogo de 28 estatus en inglés (`Created` al generar). El mapa de `N5` cubre los nombres de la referencia; los que no reconozca quedan como `en_transito` y se afinan con la primera guía real | `N5` | — |
| ~~7~~ | ~~Qué exige `POST /invoices/` y el formato de la liga~~ — **resuelto el 25 sep** con `scripts/probar-factura.py`: pide `businessDetails` y el contacto completo; la liga es `{dominio}/invoice/{id}` | `N1` | — |

**Lo que se vio del sandbox de Envia el 25 sep**: cotiza y factura en **ARS** aunque el
envío sea dentro de México —es una rareza del ambiente de prueba, no del flujo; en
producción la cuenta va en MXN—. Tarifas de referencia Nuevo Laredo → Monterrey, 45 kg:
`ground_do` 600, `ground` 770 MXN. Las sucursales traen `branch_rules` con
`max_weight: 50` kg: una paca por guía si va a ocurre. **La recolección
(`ship/pickup/`) no se probó**: el cuerpo de `N4` sigue la referencia oficial.

**Campos nuevos que `N4` escribe en el contacto y todavía no existen en Greentex:**
`etiqueta_pdf` y `track_url`. Hay que crearlos en la carpeta Envío antes de importar.

**Pendiente nuevo (25 sep):** `N4` manda una sola caja de `45 × cantidad` kg. Las
sucursales aceptan máximo 50 kg por paquete, así que un pedido de varias pacas a
`ground_do` necesita una guía por paca. Falta ese ciclo en `N4`.

**`N5` tiene dos disparadores (25 sep):** el cron de cada hora, que avisa a `AP01`, y un
webhook `rastrear` que la acción «Rastrear envío» del bot llama con `{ contactId }` y
que contesta `estatus`, `estatus_texto`, `entrega_estimada` y `track_url` en el mismo
turno. Su URL va en el custom value `url_n8n_rastrear`.

## Orden de importación

Da igual: no dependen entre sí. Pero para probar conviene `N3` primero —es el único
que no escribe nada— y luego `N1`.
