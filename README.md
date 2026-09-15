# Paca — Automatización de menudeo sobre GoHighLevel

Documentación de alcance y pre-propuesta de **786 Marketing** para el proyecto de
**pacas de ropa americana** (cliente: Pamela y Miguel — McAllen TX, almacén en
Nuevo Laredo, Tamaulipas). Proyecto referido por Yera.

> **Estado: pre-propuesta.** Esto **no es** una propuesta definitiva. El alcance
> final depende de 6 datos que el cliente todavía no entrega
> (ver `docs/05-preguntas-cliente.md`).

## Qué pide el cliente

Reactivar el **menudeo automatizado** con un bot que venda de punta a punta:
lead → conversación → apartado → pago → orden al almacén → guía al cliente.
El **mayoreo sigue aparte y manual** — textual: *"mi mayoreo yo lo trabajo aparte,
no se entromete con mi menudeo"*.

## Alcance y precio

Entrega única, sin fases posteriores: **USD 4,065** de implementación y
**USD 330 al mes**. Cronograma de **3 a 4 semanas**, con fechas exactas fijadas al
entregar la propuesta final con el mapeo.

## Documentos

| Documento | Para qué |
|---|---|
| [`docs/00-alcance-tecnico.md`](docs/00-alcance-tecnico.md) | **Empieza aquí.** Qué sí se puede construir, qué no es nativo en GHL y qué requiere pieza externa |
| [`docs/01-mapa-ghl.md`](docs/01-mapa-ghl.md) | Pipeline, workflows LS/SP/AP, agente de 17 nodos y landing de catálogo |
| [`docs/02-arquitectura-inventario.md`](docs/02-arquitectura-inventario.md) | Google Sheets + n8n, máquina de estados del apartado, concurrencia |
| [`docs/03-catalogo-productos.md`](docs/03-catalogo-productos.md) | Los 30 SKUs normalizados — fuente de la Knowledge Base |
| [`docs/04-precotizacion.md`](docs/04-precotizacion.md) | Desglose por módulo y comparación con paquetes |
| [`docs/05-preguntas-cliente.md`](docs/05-preguntas-cliente.md) | Lo que falta preguntar — 6 de ellas bloquean la construcción |
| [`propuesta/pre-propuesta-paca.html`](propuesta/pre-propuesta-paca.html) | Pre-propuesta visual para enviar al cliente |

## Datos de partida

`data/` trae el catálogo de 30 SKUs y las plantillas de las pestañas del Google
Sheet que va a operar como fuente de verdad del inventario.

## Lo que hay que saber en una línea

GHL **no puede llevar el inventario solo** (no tiene aritmética en campos numéricos)
y **Mercado Pago no es pasarela nativa**. Las dos cosas centrales que pidió el
cliente viven fuera de GHL, en **n8n + Google Sheets**. El detalle está en
`docs/00-alcance-tecnico.md`.

## Pendiente en este repo

El logo de 786 Marketing en `propuesta/pre-propuesta-paca.html` es un **wordmark
provisional reconstruido en CSS**. El bloque del header trae las instrucciones para
sustituirlo por el archivo real; la clase `.logo-img` ya está lista.
