# Alcance técnico — qué podemos construir y qué no

Documento interno para Omnia y Yera. Define la frontera del proyecto **antes** de
comprometer un número cerrado con el cliente.

Regla de la metodología (`ghl-onboarding-mapper`): *"el mapeo define los límites —
todo lo que queda fuera del mapa es alcance adicional y se cotiza aparte"*.
Este documento es ese mapa.

---

## 1. El negocio, en cuatro líneas

- Venden **pacas de ropa americana** — fardos cerrados de 100 lb / 45 kg. 30 SKUs.
- Están en **McAllen, Texas**; el almacén que despacha está en **Nuevo Laredo, Tamaulipas**, y distribuye a toda la República Mexicana.
- La mercancía **ya está importada y liberada** en México. No pasa aduana en el flujo de venta.
- Hoy hacen **sólo mayoreo**, manual. Apagaron Facebook y borraron Instagram y TikTok.

## 2. Por qué apagaron el menudeo

No fue por falta de demanda — les iba bien. Fue por desorden operativo. Textual de la llamada:

> "Llegamos a un punto en el que, pues también era como mucho, era mucho desorden,
> en el sentido de que cuando eran las direcciones y no había control."

Y sobre las direcciones mexicanas:

> "En México la gente tiene unas direcciones un poco extrañas, de pronto nos decían
> 'no, yo estoy en el kilómetro 3 pasando el rancho Fulanito', o sea, no lo puedes
> decir así a la paquetería, entonces era un show."

Por eso hoy manejan **únicamente Paquete Express** y **sólo servicio a ocurre** — el
cliente recoge en sucursal. Esto **simplifica el alcance**: no hay que validar
direcciones domiciliarias, sólo capturar ciudad y sucursal.

## 3. Lo que piden

Automatizar el menudeo completo: *"desde que llegue el lead al mensaje, el contacto,
llevar la venta, hasta el momento en el que hace el pago, los envíos, etcétera […]
que todo sea recibido a través de un robot"*.

**El mayoreo queda fuera y sigue manual.** Es explícito:

> "Mi mayoreo yo lo trabajo aparte. Lo que yo no sé entromete con mi menudeo."

Esto acota el alcance de forma importante y hay que dejarlo escrito en la propuesta.

---

## 4. Lo que SÍ se construye en GHL nativo

| Requerimiento del cliente | Cómo se resuelve |
|---|---|
| Atender leads por WhatsApp, Instagram, Facebook, TikTok | Canales nativos de GHL + Inbox unificado |
| Bot que conversa, entiende y vende | **Agent Studio** — agente con Router AI, KB del catálogo y nodos de captura |
| Que el bot conozca el catálogo (calidades, tallas, contenido) | **Knowledge Base** cargada desde `data/catalogo.csv` |
| Seguimiento de cada venta por etapas | Pipeline `SP · Menudeo` (8 etapas) |
| Temporizador del apartado + recordatorios | Workflow con `Wait` + `Goal Event` |
| Orden simple al almacén por WhatsApp | `Send Message` en workflow |
| Correo con el detalle completo a los dueños | `Send Internal Notification` / `Send Message — Email` |
| Captura de la guía por el almacén | Formulario GHL + trigger `Form Submitted` |
| Envío del tracking al cliente | `Send Message — WhatsApp` disparado por ese formulario |
| Escalamiento a humano | Tag + `Update Conversation AI Bot Status → Off` |

Todo esto entra sin fricción. Es aproximadamente el 70% del proyecto.

---

## 5. Lo que NO es nativo — la lista que define el alcance real

Esta es la sección que Yera necesita para no prometer de más.

### 5.1 · Inventario descontable — **no existe en GHL**

Es el requisito central del cliente:

> "Que tenga también detrás un inventario del robot para que no me vaya a sobrevender
> la venta en sí, porque la tenemos muy específica. O sea, tengo tantas de esta y no
> tengo más."

Pero la referencia interna de Omnia (`ghl-limitations.md`) es categórica:

> ❌ **No hay aritmética nativa en campos numéricos.** GHL no puede sumar, restar,
> multiplicar ni dividir valores de campos number.

**Solución:** el stock vive en **Google Sheets** y **n8n** hace toda la aritmética.
No es un parche — es la única arquitectura posible, y encaja con que el cliente
*ya* opera así: *"realmente es un Excel que manejamos compartido"* con el almacén.
Detalle completo en `02-arquitectura-inventario.md`.

### 5.2 · Mercado Pago — **no es pasarela nativa de GHL**

GHL trae Stripe, PayPal, NMI, Authorize.net y Razorpay. **Mercado Pago no está.**
El cliente lo pidió explícitamente y Omnia se lo recomendó en la llamada, así que
se queda — pero vía integración.

**Solución:** n8n genera la preferencia de pago con la API de Checkout Pro y
devuelve la liga; el webhook IPN de Mercado Pago avisa cuando se acredita.

> ⚠️ **Trampa técnica:** el Goal Event `Payment Received` de GHL **no dispara** con
> Mercado Pago — sólo funciona con pagos nativos de GHL. Hay que usar un
> **Inbound Webhook** como trigger. Si esto se pasa por alto en la construcción, el
> flujo de confirmación de pago simplemente nunca se ejecuta.

### 5.3 · Ventana de 24 horas de WhatsApp — **el principal riesgo de cronograma**

Fuera de las 24 h desde el último mensaje entrante del cliente, WhatsApp **sólo**
permite enviar templates aprobados por Meta. La aprobación tarda **24–48 h**.

Los mensajes que **caen fuera de la ventana** en este flujo:

| Mensaje | Por qué cae fuera |
|---|---|
| Recordatorio de apartado por vencer (12 h y 2 h antes) | El cliente lleva horas sin escribir |
| Confirmación de pago | Puede pagar al día siguiente |
| Orden enviada + número de guía | El almacén despacha días después |
| Recuperación de apartado vencido | Por definición, +24 h |

**Cuatro de los mensajes más importantes del sistema requieren template aprobado.**
Hay que crearlos y mandarlos a aprobación **al inicio del proyecto**, no al final.
Es el ítem que más fácilmente atora un go-live.

### 5.4 · Paquete Express no tiene API pública

No hay forma de generar la guía ni leer el tracking automáticamente. Omnia ya se lo
adelantó al cliente en la llamada:

> "Claramente sí tiene que ser híbrido, o sea ustedes tendrían que meter esa liga en
> donde nosotros le indiquemos para que el sistema dispare automáticamente ese
> mensaje al cliente correspondiente."

**Solución:** formulario GHL con el `orden_id` precargado. El almacén captura la
guía, el `Form Submitted` dispara el WhatsApp al cliente correcto. El paso manual
es escribir un número — nada más.

### 5.5 · Otras limitaciones que condicionan el diseño

| Limitación | Consecuencia en este proyecto |
|---|---|
| El bot de Conversation AI **no envía mensajes desde workflows** | Todo outbound programado va con `Send Message`, nunca por el bot |
| El webhook de salida de GHL **no espera respuesta** | Todo ida y vuelta con n8n es asíncrono: n8n responde disparando un Inbound Webhook y un segundo workflow continúa |
| Los campos `Date` de GHL **no guardan hora** | El `expira_en` del apartado se calcula y vive en n8n, no en un campo de GHL |
| Google Sheets **no tiene transacciones** | El workflow de reserva corre serializado en n8n (concurrencia 1) |
| `Wait` usa **días calendario**, no hábiles | Irrelevante aquí: el apartado es de 24 h literales |

---

## 6. Decisiones de alcance tomadas

| Decisión | Valor | Origen |
|---|---|---|
| Unidad de venta | Paca completa cerrada de 100 lb, de 1 en 1 | Definido con el usuario. No se venden piezas sueltas — obligaría a un inventario por prenda/talla/foto y multiplicaría el proyecto |
| Motor externo | n8n + Google Sheets | El cliente ya comparte un Excel con el almacén → cero curva de aprendizaje |
| Mayoreo | **Fuera de alcance**, sigue manual | Textual del cliente |
| Duración del apartado | 24 h | El cliente pidió 24; Omnia había propuesto 2–3 h |
| Paquetería | Paquete Express, sólo a ocurre | Único proveedor que usan |
| Pasarela | Mercado Pago | Pedido por el cliente, recomendado por Omnia en la llamada |

---

## 7. Fases

**Fase 1 — Núcleo de venta menudeo.** Es el sistema que el cliente pidió: bot que
vende, inventario que no sobrevende, apartado de 24 h, cobro por Mercado Pago, orden
al almacén, guía al cliente y escalamiento a humano. 8 workflows + 1 agente + 2
integraciones + 1 pipeline.

**Fase 2 — Crecimiento.** Landing de catálogo, dashboard de ventas y stock,
post-venta con reseñas y recompra a 30 días, workflow de campañas de Meta y TikTok
para cuando reactiven las redes. 2 workflows más + 1 pipeline + landing + reportes.

Números en `04-precotizacion.md`.

---

## 8. Riesgos abiertos

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | **Faltan los precios de venta por SKU.** Sin ellos no hay bot ni liga de pago | Pregunta bloqueante #1 — pedirla hoy |
| 2 | Templates de Meta sin aprobar al go-live | Redactarlos y enviarlos a aprobación en la semana 1 |
| 3 | Dos clientes apartando la última paca a la vez | n8n serializado; ruta de escape a Supabase documentada |
| 4 | El cliente edita el Sheet a mano y rompe una fórmula | Pestañas protegidas; sólo `disponible` y `precio` editables |
| 5 | Cuenta de Mercado Pago sin verificar → retención de fondos | Ya salió en la llamada; enviarles los requisitos |
| 6 | 5 de los 30 SKUs no están descritos en ningún transcript (corsé, playera comercial, chamarra, suéter navideño) | El agente no puede describir lo que no sabe — pedir la descripción |
