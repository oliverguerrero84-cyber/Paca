# Pre-cotización — dos paquetes

Calculada con `ghl-cotizador/scripts/ghl_cotizador.py` y la tabla de precios de
referencia. **Precios en USD.**

> **Esto es una pre-cotización.** El número final puede moverse cuando lleguen los
> datos de `05-preguntas-cliente.md`.

---

## Resumen

| | Esencial | Completo |
|---|---:|---:|
| **Implementación** (pago único) | **$1,997** | **$3,600** |
| **Mensualidad** | **$297** | **$497** |
| Primer año | $5,561 | $9,564 |
| Desde el año 2 | $3,564 | $5,964 |
| Entrega | 2 semanas | 3 a 4 semanas |

El Completo queda en **1.72×** el Esencial al primer año. Brecha de entrada:
**$1,603 de setup y $200 al mes**.

---

## Por qué subió el Completo de $3,200 a $3,600

La segunda junta y la investigación técnica cambiaron el alcance. El cálculo sube
poco —de $4,065 a **$4,179**— pero **lo que el cliente ve crecer es mucho más**:

| Lo que se agregó | Por qué importa |
|---|---|
| **Catálogo con fotos y videos en la conversación** | El agente muestra cada paca sin que el cliente salga de WhatsApp |
| **Guía generada sola** (Envia.com) | El almacén deja de ir por guías y de capturarlas en Excel |
| **Rastreo hasta "llegó a tu sucursal"** | Con servicio a ocurre, es el aviso más valioso del flujo |
| **Buscador de sucursal por código postal** | Ataca la razón de fondo por la que apagaron el menudeo |
| **Tarjeta, OXXO y SPEI en una sola liga** | Los tres métodos que pidieron, sin desarrollo extra |
| **Registro manual de transferencias** | Para los pagos que llegan a su banco |

Y **desaparece el último paso manual**: las revisiones anteriores decían que
capturar el número de guía era inevitable. Ya no lo es.

**El Esencial no se mueve** porque nada de esto le toca: no lleva tienda, ni Envia,
ni Mercado Pago, ni inventario. Subirlo sería cobrar por algo que no recibe.

**La mensualidad tampoco se mueve.** Subir setup y mensual a la vez es difícil de
defender, y los $497 ya tienen buen margen sobre los $330 calculados.

---

## Calculado contra comercial

Los precios de venta son **decisión comercial del equipo**, no salida del cotizador.

| Paquete | Calculado | Comercial | Diferencia |
|---|---|---|---|
| Esencial | $2,044 / $230 | **$1,997 / $297** | setup −$47 · mensual +$67 |
| Completo | $4,179 / $330 | **$3,600 / $497** | setup −$579 (−14%) · mensual +$167 (+51%) |

> ⚠️ **La estructura del Completo sigue sin ser un descuento.** Contra la estructura
> original ($4,065 / $330), el primer año pasa de $8,025 a **$9,564** y el año 2 de
> $3,960 a $5,964. La barrera de entrada baja; el recurrente sube más. Es una
> decisión legítima, pero **se cobra más, no menos** — que nadie lo presente al
> cliente como una rebaja.

---

## Desglose del Completo · calculado $4,179 / $330

| Módulo | Setup | Mensual |
|---|---:|---:|
| Setup de subcuenta (DNS, dominio, WhatsApp API, correos) | $250 | — |
| CRM & Pipelines — 1 pipeline de 8 etapas + 3 vistas | $320 | — |
| Automatizaciones & Workflows — 9 workflows | $1,034 | — |
| Chatbot / AI Chat — agente de 19 nodos con IA avanzada | $685 | $80 |
| Integraciones — Envia.com + motor de apartado (n8n) | $600 | $100 |
| Documentos & Templates — 6 plantillas | $400 | — |
| Catálogo público — 6 secciones | $490 | — |
| Capacitación — 2 sesiones (dueños y almacén) | $400 | — |
| Soporte post-implementación | — | $150 |
| **Total calculado** | **$4,179** | **$330** |

> **Mercado Pago e inventario ya no aparecen como integraciones** porque son nativos
> de GHL. Antes pesaban $600 de setup y $100 al mes ellos solos.

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

---

## Qué diferencia realmente a los dos paquetes

El corte sigue siendo el mismo, aunque la frontera se movió: **el Esencial es la
atención; el Completo es la operación.**

| | Esencial | Completo |
|---|---|---|
| Catálogo con fotos y videos | — | ● |
| Inventario en vivo | — | ● GHL nativo |
| Apartado de 24 h con reloj | — | ● n8n + `Update Inventory` |
| Cobro (tarjeta, OXXO, SPEI) | — | ● Mercado Pago nativo |
| Guía y recolección automáticas | — | ● Envia.com |
| Rastreo hasta la sucursal | — | ● |
| Buscador de sucursal por CP | — | ● |
| Integraciones externas | **0** | 2 |

En el Esencial el agente arma el pedido y **deriva a un asesor**, que confirma
disponibilidad y cobra.

> ⚠️ **Advertencia de alcance.** El cliente dijo que no sobrevender era central
> (*"tengo tantas de esta y no tengo más"*). **El Esencial no resuelve eso.** Se
> presenta como rampa de entrada, nunca como equivalente del Completo.

---

## Qué NO incluye ninguno de los dos

| Fuera de alcance | Nota |
|---|---|
| **Mayoreo** | El cliente lo pidió explícitamente aparte y manual |
| Venta de piezas sueltas | Exigiría inventario por prenda/talla/foto — otro proyecto |
| Reportes y dashboards | Se retiró del alcance |
| Post-venta, reseñas y recompra | Se retiró. Además **no quieren reseñas de Google** por el hate de la competencia |
| Campañas de Meta y TikTok (`LS02`) | Se retiró del alcance |
| Facturación CFDI | No se habló. Sería integración adicional |
| **Fotografía y video de producto** | **No cotizado** — los entrega el cliente |
| Devoluciones | **No hay**, es política del cliente. No se construye flujo |
| Pauta publicitaria | Gasto del cliente, aparte |
| Costos de terceros | WhatsApp API por conversación, comisiones de Mercado Pago, **saldo de Envia.com por guía**, n8n si es alojado, Google Workspace |

> **Envia.com es prepago, sin mensualidad ni comisión**: se carga saldo y se paga
> por guía. Con 500–800 envíos al mes, conviene pedirles tarifa por volumen.

---

## Cómo reproducir los números

```python
import sys; sys.path.insert(0,'<ruta>/ghl-cotizador/scripts')
from ghl_cotizador import calcular_cotizacion

wf=[('LS01',10),('SP01',8),('SP02',16),('SP03',12),('SP04',10),
    ('SP05',12),('AP01',10),('AP02',8),('AP03',7)]
completo=dict(setup_subcuenta='completo',
  pipelines=[{'nombre':'SP','etapas':8}], vistas_filtros=3,
  workflows=[{'nombre':a,'nodos':b} for a,b in wf],
  chatbots=[{'nombre':'Agente','nodos':19,'ia_avanzada':True}],
  integraciones=2, plantillas=6, calendarios=False,
  landing_pages=[{'nombre':'Catalogo','secciones':6}],
  reportes=False, sesiones_capacitacion=2, soporte=True)
# -> 4179 / 330
```

El Esencial no cambió; su scope está en la revisión anterior de este documento y en
`01-mapa-ghl.md`.
