# Los 5 flujos de n8n

> ⚠️ **Escritos, no probados.** No existe todavía la instancia donde correrlos
> (eslabón `0.3` de `docs/13-accesos.md`). Se verificó la estructura y que los campos
> que leen y escriben existan de verdad en Greentex, **pero ninguno se ha ejecutado**.
> Los supuestos van marcados abajo y en notas dentro de cada flujo.

| Flujo | Entrada | Qué hace |
|---|---|---|
| `N1-apartar` | Webhook `POST /apartar` | Lee el stock del SKU; si alcanza, descuenta y arranca el reloj |
| `N2-liberar-vencidos` | Cron 15 min | Devuelve el stock de los apartados vencidos |
| `N3-buscar-sucursal` | Webhook `POST /buscar-sucursal` | Código postal → 2 o 3 sucursales |
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
| `Envia · API` | `Authorization` | `Bearer …` de la cuenta de Envia |

### 2. Las variables de entorno

```
GHL_LOCATION_ID       = c9jj5uu1WZOIkwi6Vfj5
GHL_PIPELINE_ID       = 80QTHEK406nT2KJhQ6TZ
GHL_STAGE_APARTADO    = 4e1d2753-b967-4817-b3b2-2b0a42efa5c6
GHL_STAGE_ENVIADO     = 352335f2-4150-43a0-8067-737cbcd8695e
GHL_STAGE_ENTREGADO   = ba84ff53-246f-4f04-9547-acd6f6210292
GHL_WEBHOOK_RASTREO   = (el id del Inbound Webhook de AP01, cuando exista)
HORAS_APARTADO        = 24

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

**Ninguno toca Mercado Pago.** El cobro lo hace GHL con la API de Invoices. n8n valida
stock, busca sucursales y mueve guías. Es decisión cerrada.

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
| 3 | **La URL base de Envia y sus parámetros** | `N3`, `N4`, `N5` | Es el hueco 1 de `docs/13-accesos.md` §8: nadie ha visto la documentación con credenciales en mano |
| 4 | **Que `carrier-branches` traiga coordenadas** | `N3` | Sin ellas se filtra por ciudad. El flujo ya lo maneja y lo reporta en `ordenadas_por` |
| 5 | **El esquema de `ship/generate`** | `N4` | Hay que confirmarlo contra docs.envia.com antes de la primera guía real |
| 6 | **Los textos de estatus de Paquete Express** | `N5` | La lista de palabras hay que afinarla con la primera guía real |

Los supuestos 3, 5 y 6 se resuelven con lo mismo: **conseguir las credenciales de
Envia y hacer una guía de prueba.** Es lo que más destraba de esta carpeta.

## Orden de importación

Da igual: no dependen entre sí. Pero para probar conviene `N3` primero —es el único
que no escribe nada— y luego `N1`.
