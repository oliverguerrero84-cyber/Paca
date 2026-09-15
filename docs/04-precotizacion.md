# Pre-cotización — dos paquetes

Calculada con `ghl-cotizador/scripts/ghl_cotizador.py` y la tabla de precios de
referencia. **Precios en USD.**

> **Esto es una pre-cotización.** El número final puede moverse cuando lleguen los
> datos de `05-preguntas-cliente.md`.

---

## Resumen

| | Esencial | Completo |
|---|---:|---:|
| **Implementación** (pago único) | **$1,997** | **$3,200** |
| **Mensualidad** | **$297** | **$497** |
| Primer año | $5,561 | $9,164 |
| Desde el año 2 | $3,564 | $5,964 |
| Entrega | 2 semanas | 3 a 4 semanas |

El Completo queda en **1.65×** el Esencial al primer año. La brecha de entrada es de
**$1,203 de setup y $200 al mes**.

---

## Calculado contra comercial

Los precios de venta son **decisión comercial del equipo**, no salida del cotizador.
Ambos números quedan registrados aquí para que nadie los confunda.

| Paquete | Calculado | Comercial | Diferencia |
|---|---|---|---|
| Esencial | $2,044 / $230 | **$1,997 / $297** | setup −$47 · mensual +$67 (+29%) |
| Completo | $4,065 / $330 | **$3,200 / $497** | setup −$865 (−21%) · mensual +$167 (+51%) |

> ⚠️ **La reestructura del Completo no es un descuento.** Contra la estructura
> anterior ($4,065 / $330), el Completo pasa de $8,025 a **$9,164** el primer año
> (**+$1,139**) y de $3,960 a **$5,964** anuales desde el segundo
> (**+$2,004 al año**). Baja la barrera de entrada en $865 y lo recupera con creces
> en el recurrente. Es una decisión legítima, pero **se está cobrando más, no
> menos** — que nadie lo presente al cliente como una rebaja.

---

## Desglose del Completo · calculado $4,065 / $330

| Módulo | Setup | Mensual |
|---|---:|---:|
| Setup de subcuenta (DNS, dominio, WhatsApp API, correos) | $250 | — |
| CRM & Pipelines — 1 pipeline de 8 etapas + 3 vistas | $320 | — |
| Automatizaciones & Workflows — 8 workflows | $1,000 | — |
| Chatbot / AI Chat — agente de 17 nodos con IA avanzada | $655 | $80 |
| Integraciones — Mercado Pago + motor de inventario | $600 | $100 |
| Documentos & Templates — 5 plantillas | $350 | — |
| Landing de catálogo — 6 secciones | $490 | — |
| Capacitación — 2 sesiones (dueños y almacén) | $400 | — |
| Soporte post-implementación | — | $150 |
| **Total calculado** | **$4,065** | **$330** |

## Desglose del Esencial · calculado $2,044 / $230

| Módulo | Setup | Mensual |
|---|---:|---:|
| Setup de subcuenta | $250 | — |
| CRM & Pipelines — 1 pipeline de 5 etapas + 2 vistas | $250 | — |
| Automatizaciones & Workflows — 5 workflows | $514 | — |
| Chatbot / AI Chat — agente de 12 nodos con IA avanzada | $580 | $80 |
| Documentos & Templates — 3 plantillas | $250 | — |
| Capacitación — 1 sesión | $200 | — |
| Soporte post-implementación | — | $150 |
| **Total calculado** | **$2,044** | **$230** |

**Qué le quitamos al Completo para llegar al Esencial:** las 2 integraciones
externas (−$600 setup, −$100 mes), la landing (−$490), 3 workflows y los nodos de
los que quedan (−$486), 5 nodos del agente (−$75), 2 plantillas (−$100), 1 sesión
de capacitación (−$200), 3 etapas de pipeline y 1 vista (−$70).

---

## Qué diferencia realmente a los dos paquetes

El corte no es arbitrario: **el Esencial es todo lo que GHL hace nativo, el
Completo agrega lo que necesita piezas externas.**

| | Esencial | Completo |
|---|---|---|
| Inventario conectado | — | n8n + Google Sheets |
| Apartado de 24 h con reloj | — | Workflow + n8n |
| Cobro por Mercado Pago | — | n8n + API Checkout Pro |
| Aviso al almacén y correo de orden | — | Workflow nativo |
| Guía al cliente | — | Formulario + workflow |
| Landing de catálogo | — | GHL Pages |
| Integraciones externas | **0** | 2 |

En el Esencial el agente arma el pedido y **deriva a un asesor**, que confirma
disponibilidad y cobra. Resuelve la atención, no la operación.

> ⚠️ **Advertencia de alcance.** El cliente dijo que no sobrevender era central
> (*"tengo tantas de esta y no tengo más"*). **El Esencial no resuelve eso.** Se
> presenta como rampa de entrada para medir volumen, nunca como equivalente del
> Completo.

---

## Comparación con paquetes de la tabla

| Modalidad | Setup | Mensual | Primer año |
|---|---:|---:|---:|
| **Completo à la carte** | **$4,065** | **$330** | **$8,025** |
| Starter | $4,140 | $330 | $8,100 |
| Pro | $3,818 | $460 | $9,338 |
| Enterprise | $4,128 | $580 | $11,088 |

Ninguno ahorra. À la carte sigue siendo la base de cálculo.

> **Nota sobre Pro y Enterprise.** Hay un bug en `ghl_cotizador.py:435`: suma
> `cantidad_cb × $80` al mensual de extras aunque el paquete ya incluya el chatbot.
> Corregido, Pro daría $3,818 / $380 = $8,378 al primer año, que sigue perdiendo
> contra los $8,025 de à la carte. La conclusión no cambia, pero el número que
> imprime el script está mal.

---

## Qué NO incluye ninguno de los dos

| Fuera de alcance | Nota |
|---|---|
| **Mayoreo** | El cliente lo pidió explícitamente aparte y manual |
| Venta de piezas sueltas | Exigiría inventario por prenda/talla/foto — otro proyecto |
| Reportes y dashboards | Se retiró del alcance |
| Post-venta, reseñas y recompra | Se retiró del alcance |
| Campañas de Meta y TikTok (`LS02`) | Se retiró del alcance |
| Integración con la paquetería | Sin API pública; la guía se captura a mano |
| Facturación CFDI | No se habló. Sería integración adicional |
| **Fotografía y textos de producto** | **No cotizado** — los entrega el cliente |
| Pauta publicitaria | Gasto del cliente, aparte |
| Costos de terceros | WhatsApp API por conversación, comisiones de Mercado Pago, n8n si es alojado, Google Workspace |

> Los **costos de terceros** los paga el cliente directamente y no pasan por
> 786 Marketing.

---

## Cómo reproducir los números

```python
import sys; sys.path.insert(0,'<ruta>/ghl-cotizador/scripts')
from ghl_cotizador import calcular_cotizacion

wf_full=[('LS01',10),('SP01',8),('SP02',18),('SP03',12),('SP04',14),('SP05',10),('AP01',9),('AP02',8)]
completo=dict(setup_subcuenta='completo',
  pipelines=[{'nombre':'SP','etapas':8}], vistas_filtros=3,
  workflows=[{'nombre':a,'nodos':b} for a,b in wf_full],
  chatbots=[{'nombre':'Agente','nodos':17,'ia_avanzada':True}],
  integraciones=2, plantillas=5, calendarios=False,
  landing_pages=[{'nombre':'Catalogo','secciones':6}],
  reportes=False, sesiones_capacitacion=2, soporte=True)
# -> 4065 / 330

wf_lite=[('LS01',8),('SP01',8),('SP02',10),('SP03',8),('AP02',8)]
esencial=dict(setup_subcuenta='completo',
  pipelines=[{'nombre':'SP','etapas':5}], vistas_filtros=2,
  workflows=[{'nombre':a,'nodos':b} for a,b in wf_lite],
  chatbots=[{'nombre':'Agente','nodos':12,'ia_avanzada':True}],
  integraciones=0, plantillas=3, calendarios=False,
  reportes=False, sesiones_capacitacion=1, soporte=True)
# -> 2044 / 230
```

El detalle de cada workflow y sus nodos está en `01-mapa-ghl.md`.
