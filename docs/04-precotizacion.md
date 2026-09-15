# Pre-cotización

Calculada con `ghl-cotizador/scripts/ghl_cotizador.py` y la tabla de precios de
referencia. **Precios en USD.**

> **Esto es una pre-cotización.** El número final puede moverse cuando lleguen los
> datos de `05-preguntas-cliente.md` — sobre todo si el cliente pide cosas que hoy
> no están en el mapa.

---

## Resumen

| Concepto | Monto |
|---|---:|
| **Implementación** (pago único) | **$4,065** |
| **Mensualidad** | **$330** |

Entrega única, sin fases posteriores. **Modalidad: à la carte** — ningún paquete
genera ahorro con este scope.

---

## Desglose

| Módulo | Setup | Mensual |
|---|---:|---:|
| Setup de subcuenta (DNS, dominio, WhatsApp API, correos) | $250 | — |
| CRM & Pipelines — 1 pipeline de 8 etapas + 3 vistas | $320 | — |
| Automatizaciones & Workflows — 8 workflows | $1,000 | — |
| Chatbot / AI Chat — agente de 17 nodos con IA avanzada | $655 | $80 |
| Integraciones — Mercado Pago + motor de inventario | $600 | $100 |
| Documentos & Templates — 5 plantillas | $350 | — |
| **Landing de catálogo — 6 secciones** | **$490** | — |
| Capacitación — 2 sesiones (dueños y almacén) | $400 | — |
| Soporte post-implementación | — | $150 |
| **Total** | **$4,065** | **$330** |

**Dónde está el peso:** Workflows, $1,000 — el 25% del setup. La tabla incluye 3
workflows de 8 nodos en la base; acá son 8 workflows y varios pasan de 8 nodos
(SP02 tiene 18, SP04 tiene 14). Es un proyecto de complejidad alta y vale la pena
comunicarlo como valor diferencial, no disculparse por el número.

**La landing suma $490:** base $450 más una sección extra sobre las 5 incluidas
($40). No tiene cuota mensual, por eso el recurrente no se mueve.

---

## Comparación con paquetes

| Modalidad | Setup | Mensual | Primer año |
|---|---:|---:|---:|
| **À la carte** | **$4,065** | **$330** | **$8,025** |
| Starter | $4,140 | $330 | $8,100 |
| Pro | $3,818 | $460 | $9,338 |
| Enterprise | $4,128 | $580 | $11,088 |

Pro tiene el setup más bajo, pero su mensual de $460 se lo come en el primer año.
Ninguno ahorra. **À la carte es la recomendación.**

> **Nota sobre el cálculo de Pro y Enterprise.** Hay un bug en el script del
> cotizador: `ghl_cotizador.py:435` suma `cantidad_cb × $80` al mensual de extras
> aunque el paquete **ya incluya** el chatbot, inflando el mensual de Pro y
> Enterprise. Corrigiéndolo, Pro quedaría en $3,818 setup / $380 mes — $8,378 al
> primer año, que sigue perdiendo contra los $8,025 de à la carte. **La
> recomendación no cambia**, pero el número que imprime el script hoy está mal y
> conviene arreglarlo antes de usarlo en otra cotización.

---

## Qué NO incluye

Para que no haya sorpresas después:

| Fuera de alcance | Nota |
|---|---|
| **Mayoreo** | El cliente lo pidió explícitamente aparte y manual |
| Venta de piezas sueltas | Exigiría inventario por prenda/talla/foto — otro proyecto |
| Reportes y dashboards | Se retiró del alcance |
| Post-venta, reseñas y recompra | Se retiró del alcance |
| Campañas de Meta y TikTok (`LS02`) | Se retiró del alcance |
| Integración con la paquetería | Sin API pública; la guía se captura a mano |
| Facturación CFDI | No se habló. Si lo quieren, es integración adicional |
| Fotografía y contenido de producto | **No cotizado** — las fotos y textos los entrega el cliente |
| Pauta publicitaria | No cotizado — es gasto del cliente, aparte |
| Costos de terceros | WhatsApp API por conversación, comisiones de Mercado Pago, n8n si es alojado, Google Workspace |

> Las **fotos y descripciones de producto** las entrega el cliente. La landing y las
> fichas del bot se montan con ese material; producirlo no está en esta cotización.

> Los **costos de terceros** los paga el cliente directamente y no pasan por
> 786 Marketing. Conviene mencionarlo para que el mensual no sorprenda.

---

## Cómo reproducir el número

```bash
python3 -c "
import sys; sys.path.insert(0,'<ruta>/ghl-cotizador/scripts')
from ghl_cotizador import calcular_cotizacion
wf=[('LS01',10),('SP01',8),('SP02',18),('SP03',12),('SP04',14),('SP05',10),('AP01',9),('AP02',8)]
scope=dict(setup_subcuenta='completo',
  pipelines=[{'nombre':'SP Menudeo','etapas':8}], vistas_filtros=3,
  workflows=[{'nombre':a,'nodos':b} for a,b in wf],
  chatbots=[{'nombre':'Agente','nodos':17,'ia_avanzada':True}],
  integraciones=2, plantillas=5, calendarios=False,
  landing_pages=[{'nombre':'Catalogo','secciones':6}],
  reportes=False, sesiones_capacitacion=2, soporte=True)
r=calcular_cotizacion(scope)['a_la_carte']
print(r['setup'], r['mensual'])   # -> 4065 330
"
```

El detalle de cada workflow y sus nodos está en `01-mapa-ghl.md`.
