# Paca — Automatización de menudeo sobre GoHighLevel

Documentación de alcance y pre-propuesta de **786 Marketing** para el proyecto de
**pacas de ropa americana** (cliente: Pamela y Miguel — McAllen TX, almacén en
Nuevo Laredo, Tamaulipas). Proyecto referido por Yera.

> **Estado: pre-propuesta.** Esto **no es** una propuesta definitiva. El alcance
> final depende de los datos que el cliente todavía no entrega
> (ver `docs/05-preguntas-cliente.md`).

## Qué pide el cliente

Reactivar el **menudeo automatizado** con un bot que venda de punta a punta:
lead → conversación → apartado → pago → orden al almacén → guía al cliente.
El **mayoreo sigue aparte y manual** — textual: *"mi mayoreo yo lo trabajo aparte,
no se entromete con mi menudeo"*.

## Dos paquetes

| | Esencial | Completo |
|---|---:|---:|
| Implementación | **$1,997** | **$3,600** |
| Mensualidad | **$297** | **$497** |
| Primer año | $5,561 | $9,564 |
| Entrega | 2 semanas | 3 a 4 semanas |

El corte: **el Esencial es la atención; el Completo es la operación.** El Completo
agrega tienda con inventario en vivo, apartado de 24 h, cobro con tarjeta/OXXO/SPEI,
y guía, recolección y rastreo automáticos vía Envia.com.

> ⚠️ El Esencial resuelve **la atención**, no **la operación**. El cliente dijo que
> no sobrevender era central; eso sólo lo resuelve el Completo. Se ofrece como
> rampa de entrada, nunca como equivalente.

## Documentos

| Documento | Para qué |
|---|---|
| [`docs/00-alcance-tecnico.md`](docs/00-alcance-tecnico.md) | **Empieza aquí.** Qué sí se puede construir, qué no es nativo en GHL y qué lleva cada paquete |
| [`docs/01-mapa-ghl.md`](docs/01-mapa-ghl.md) | Pipeline, workflows, agente y landing, marcados por paquete |
| [`docs/02-arquitectura-inventario.md`](docs/02-arquitectura-inventario.md) | Google Sheets + n8n, máquina de estados del apartado, concurrencia |
| [`docs/03-catalogo-productos.md`](docs/03-catalogo-productos.md) | Los 30 SKUs normalizados — fuente de la Knowledge Base |
| [`docs/04-precotizacion.md`](docs/04-precotizacion.md) | Los dos paquetes, calculado contra comercial |
| [`docs/05-preguntas-cliente.md`](docs/05-preguntas-cliente.md) | Lo que falta preguntar |
| [`propuesta/pre-propuesta-paca.html`](propuesta/pre-propuesta-paca.html) | Pre-propuesta comparativa para enviar al cliente |

## Datos de partida

`data/catalogo.csv` trae los 30 SKUs y es la fuente de la Knowledge Base del agente
y de la carga de productos en la tienda.

## Lo que hay que saber en una línea

**Mercado Pago y el inventario ya son nativos de GHL** — las revisiones 2 y 3 de
estos documentos decían lo contrario y estaban equivocadas. Lo único que GHL no sabe
hacer es **apartar sin cobrar**, y ahí es donde queda n8n: como reloj del apartado,
no como motor del sistema. La logística la resuelve **Envia.com**, que genera guías,
programa recolecciones, rastrea y da el catálogo de sucursales.

Los datos de `data/` (los 30 SKUs) siguen igual; las plantillas de Google Sheets
quedaron obsoletas al mudar el stock a GHL.

## Pendiente en este repo

El logo de 786 Marketing en `propuesta/pre-propuesta-paca.html` es un **wordmark
provisional reconstruido en CSS**. El bloque del header trae las instrucciones para
sustituirlo por el archivo real; la clase `.logo-img` ya está lista.
