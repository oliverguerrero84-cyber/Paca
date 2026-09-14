# Pre-cotización

Calculada con `ghl-cotizador/scripts/ghl_cotizador.py` y la tabla de precios de
Omnia. **Precios en USD.**

> **Esto es una pre-cotización.** El número final puede moverse cuando lleguen los
> datos de `05-preguntas-cliente.md` — sobre todo si el cliente pide cosas que hoy
> no están en el mapa.

---

## Resumen

| Escenario | Setup | Mensual |
|---|---:|---:|
| **Fase 1 — Núcleo menudeo** | **$3,575** | **$330** |
| **Fase 1 + 2 — Completo** | **$4,754** | **$390** |

**Modalidad recomendada: à la carte** en los dos escenarios. Ningún paquete
(Starter, Pro, Enterprise) genera ahorro — el scope es más pesado que los límites
de todos ellos, sobre todo en workflows.

---

## Fase 1 — Núcleo menudeo · $3,575 setup / $330 mes

| Módulo | Setup | Mensual |
|---|---:|---:|
| Setup de subcuenta (DNS, dominio, WhatsApp API, correos) | $250 | — |
| CRM & Pipelines — 1 pipeline de 8 etapas + 3 vistas | $320 | — |
| Automatizaciones & Workflows — 8 workflows | $1,000 | — |
| Chatbot / AI Chat — agente de 17 nodos con IA avanzada | $655 | $80 |
| Integraciones — Mercado Pago + motor de inventario | $600 | $100 |
| Documentos & Templates — 5 plantillas | $350 | — |
| Capacitación — 2 sesiones (dueños y almacén) | $400 | — |
| Soporte post-implementación | — | $150 |
| **Total** | **$3,575** | **$330** |

**Dónde está el peso:** Workflows, $1,000 — el 28% del setup. La tabla de Omnia
incluye 3 workflows de 8 nodos en la base; acá son 8 workflows y varios pasan de 8
nodos (SP02 tiene 18, SP04 tiene 14). Es un proyecto de complejidad alta y vale la
pena comunicarlo como valor diferencial, no disculparse por el número.

## Fase 1 + 2 — Completo · $4,754 setup / $390 mes

Todo lo anterior más:

| Agregado | Setup | Mensual |
|---|---:|---:|
| 2° pipeline (post-venta y recompra) + 1 vista | +$25 | — |
| 2 workflows más (`LS02`, `PS01`) | +$164 | — |
| 1 plantilla más | +$50 | — |
| Landing de catálogo (6 secciones) | +$490 | — |
| Reportes & dashboards (ventas, stock, apartados vencidos) | +$250 | $60 |
| 1 sesión de capacitación más | +$200 | — |
| **Total** | **$4,754** | **$390** |

---

## Comparación con paquetes

| Modalidad | Setup | Mensual | Ahorro 1er año |
|---|---:|---:|---:|
| **À la carte (Fase 1)** | **$3,575** | **$330** | — |
| Starter | $3,650 | $330 | −$75 |
| Pro | $3,328 | $460 | −$1,313 |
| Enterprise | $4,128 | $580 | −$3,553 |

Ninguno ahorra. À la carte es la recomendación.

> **Nota sobre el cálculo de Pro y Enterprise.** Hay un bug en el script del
> cotizador: `ghl_cotizador.py:435` suma `cantidad_cb × $80` al mensual de extras
> aunque el paquete **ya incluya** el chatbot, inflando el mensual de Pro y
> Enterprise. Corrigiéndolo, Pro quedaría en $3,328 setup / $380 mes — que en el
> primer año da $7,888 contra $7,535 de à la carte. **La recomendación no cambia**,
> pero el número que imprime el script hoy está mal y conviene arreglarlo antes de
> usarlo en otra cotización.

---

## Qué NO incluye

Para que no haya sorpresas después:

| Fuera de alcance | Nota |
|---|---|
| **Mayoreo** | El cliente lo pidió explícitamente aparte y manual |
| Venta de piezas sueltas | Exigiría inventario por prenda/talla/foto — otro proyecto |
| Integración con Paquete Express | No tiene API pública; la guía se captura a mano |
| Facturación CFDI | No se habló. Si lo quieren, es integración adicional |
| Fotografía y contenido de producto | No cotizado |
| Pauta publicitaria en Meta o TikTok | No cotizado — es gasto del cliente, aparte |
| Costos de terceros | WhatsApp API por conversación, comisiones de Mercado Pago, n8n si es alojado, Google Workspace |

> Los **costos de terceros** los paga el cliente directamente y no pasan por Omnia.
> Conviene mencionarlo en la conversación para que el mensual no sorprenda.

---

## Cómo reproducir estos números

```bash
python3 -c "
import sys; sys.path.insert(0,'<ruta>/ghl-cotizador/scripts')
from ghl_cotizador import calcular_cotizacion
# scopes en docs/00-alcance-tecnico.md §7 y docs/01-mapa-ghl.md §2-4
"
```

Los scopes exactos (workflows con su conteo de nodos, chatbot de 17 nodos con
`ia_avanzada: True`, 2 integraciones) están en `01-mapa-ghl.md`.

---

## Nota sobre el descuento de la calculadora

La pre-propuesta HTML muestra un **5% de descuento sobre la implementación** al
contratar las dos fases juntas: $4,754 → **$4,516**, un ahorro de $238.

**Ese 5% no sale del cotizador** — es una palanca comercial que se fijó al armar la
página, porque hacer la Fase 2 como proyecto separado más adelante tiene costo de
re-arranque. Está puesto en un solo lugar del código (`PACK_DISCOUNT = 0.05`) por si
se quiere cambiar o quitar antes de enviarlo.

Lo que **sí** sale del cotizador, sin tocar:

| Concepto | Valor |
|---|---:|
| Fase 1 — setup | $3,575 |
| Fase 1 — mensual | $330 |
| Fase 2 — setup incremental | $1,179 |
| Fase 2 — mensual incremental | $60 |
| Ambas fases, sin descuento | $4,754 |
