# Alcance técnico — qué podemos construir y qué no

Documento interno de 786 Marketing. Define la frontera del proyecto **antes** de
comprometer un número cerrado con el cliente.

Regla de la metodología: *"el mapeo define los límites —
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

Por eso históricamente manejaron **únicamente Paquete Express** y **sólo servicio a
ocurre** — el cliente recoge en sucursal. Esto **simplifica el alcance**: no hay que
validar direcciones domiciliarias, sólo capturar ciudad y sucursal.

En la segunda junta lo confirmaron: **siguen con Paquete Express y sólo a ocurre.**
Miguel lo explicó sin rodeos: *"Paquete Express es muy así de Cancún, Mérida,
Villahermosa. No llega a Zacatlán de las Manzanas."* Llega a unas 146 sucursales en
ciudades principales, y esa limitación **les sirve como filtro**: quien no tenga
sucursal cerca se descalifica solo, y para ellos eso es una ventaja, no una pérdida.

También cerraron el precio del envío: **va incluido**. Miguel: *"yo pongo una paca
de seis mil trescientos pesos, es a cualquier parte, ya incluido el envío, a
cualquier parte de la República."* Eso **cierra la pregunta bloqueante del costo de
envío** que arrastrábamos desde la primera llamada.

## 3. Lo que piden

Automatizar el menudeo completo: *"desde que llegue el lead al mensaje, el contacto,
llevar la venta, hasta el momento en el que hace el pago, los envíos, etcétera […]
que todo sea recibido a través de un robot"*.

**El mayoreo queda fuera y sigue manual.** Es explícito:

> "Mi mayoreo yo lo trabajo aparte. Lo que yo no sé entromete con mi menudeo."

Esto acota el alcance de forma importante y hay que dejarlo escrito en la propuesta.

### Cómo se cierra la venta: todo en la conversación, salvo el pago

> **Esta decisión cambió en la revisión 5.** Antes decía "el bot atiende y la tienda
> cobra". Ver `07-decision-checkout.md` para el razonamiento completo.

La venta ocurre **íntegra en WhatsApp**. El agente atiende, muestra fotos y videos,
resuelve dudas, arma el pedido, pide el código postal y deja elegir sucursal. Al
final manda **una liga de pago**: el cliente sale de WhatsApp una sola vez, a una
página de un solo paso, y vuelve solo.

Tres razones para no mandarlos a una tienda:

1. **Fricción para su público.** Mauricio: *"muchas veces no saben cómo escribir
   bien, no saben cómo usar muy bien el teléfono, las redes"*. Un checkout con
   carrito los pierde.
2. **Invoices y Payment Links son lo que HighLevel documenta para cobrar con Stripe.**
   El checkout de la tienda es una pieza que no hace falta.
3. **El apartado y el checkout de la tienda chocan.** Si alguien aparta la última
   paca, la tienda se la muestra agotada *a esa misma persona* cuando va a pagar.

Sobre la captura de dirección, Germán tenía razón en que conversando sale mal — pero
la solución no es un formulario, es **pedir sólo el código postal**. Cinco dígitos
es lo único que ese público da sin equivocarse, y el sistema devuelve las sucursales
para que elija de una lista. Detalle en `06-logistica-envia.md`.

**La página pública sobrevive como catálogo**, no como caja: es el destino de la
publicidad, porque no tienen Instagram ni TikTok.

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
| Cobro con tarjeta (OXXO y SPEI por validar) | **Liga de pago**: factura por la API de Invoices, cobrada con Stripe |
| Catálogo con fotos y videos | **En la conversación**, más una página pública para la publicidad |
| Inventario que no sobrevende | Productos de GHL + `Update Inventory` desde n8n |
| Envío del rastreo al cliente | `Send Message — WhatsApp` disparado por los eventos de Envia |
| Escalamiento a humano | Tag + `Update Conversation AI Bot Status → Off` |

Todo esto entra sin fricción. Es aproximadamente el 70% del proyecto.

---

## 5. Lo que NO es nativo — la lista que define el alcance real

Esta es la sección que Yera necesita para no prometer de más.

### 5.1 · Apartar sin cobrar — eso sí que no existe en GHL

Es el requisito central del cliente:

> "Que tenga también detrás un inventario del robot para que no me vaya a sobrevender
> la venta en sí, porque la tenemos muy específica. O sea, tengo tantas de esta y no
> tengo más."

Y en la segunda junta lo precisó como un boleto de concierto: eliges, se abre un
reloj de 24 h, y si no pagas la pieza se libera para el siguiente.

**GHL sí lleva inventario.** Su tienda tiene control de stock nativo
(Pagos → Productos → Inventario) y un endpoint oficial `Update Inventory` con
`availableQuantity`. Lo que **no** sabe hacer es reservar una pieza sin cobrarla:
descuenta al pagarse la orden, no antes.

**Solución:** el stock vive en GHL y **n8n es el reloj del apartado**, escribiendo
por `Update Inventory` al reservar y al liberar. Detalle completo en
`02-arquitectura-inventario.md`.

> Lo que sigue siendo cierto de la referencia de limitaciones: **GHL no hace
> aritmética en campos de contacto.** Por eso el conteo no puede vivir en un campo
> custom — pero sí vive en el producto de la tienda, que es otra cosa.

### 5.2 · Stripe — la pasarela, desde el 25 de septiembre

> ⚠️ **Corrección.** Las revisiones 2 y 3 de este documento decían que Mercado Pago
> no era nativo. **Era falso**: lo es desde el 27 de abril de 2026. Pero el 25 de
> septiembre el cliente decidió cobrar con **su Stripe** (entidad de EE.UU.) y Mercado
> Pago quedó fuera. Stripe se conecta en Pagos → Integraciones; la subcuenta va en
> **MXN** porque GHL no convierte moneda.

Consecuencias:

- **El Goal Event `Payment Received` sí dispara**, porque la factura es un pago de GHL.
  No hace falta Inbound Webhook ni middleware.
- **Tarjeta está confirmado.** OXXO y transferencia SPEI existen en Stripe para
  cuentas de EE.UU. con comprador en México, pero el checkout de GHL con Stripe no los
  lista oficialmente: es la **validación 4**. Si no aparecen, el plan B es tarjeta por
  la liga y transferencia manual con `AP03`.
- No hay verificación de cuenta pendiente: el Stripe del cliente ya está activo.

> ⚠️ **Si hay OXXO:** el voucher vale **5 días** y el pago acredita al siguiente día
> hábil, más que el apartado de 24 h. El apartado se extiende hasta que venza el
> voucher, más un día hábil, y el bot se lo dice. OXXO no admite reembolsos ni
> contracargos. Tarjeta y SPEI son instantáneos.

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

### 5.4 · Paquete Express no tiene API propia — pero Envia.com sí

> ⚠️ **Corrección.** Las revisiones anteriores decían que no había forma de generar
> la guía ni leer el rastreo automáticamente, y que el almacén tendría que capturar
> el número a mano. **Ya no aplica.** Oliver trajo a **Envia.com**, un agregador que
> sí expone Paquete Express por API.

Lo que Envia resuelve (detalle en `06-logistica-envia.md`):

| Endpoint | Para qué |
|---|---|
| `POST /ship/generate/` | **Genera la guía con número de rastreo** |
| `POST /ship/pickup/` | Programa la recolección en el almacén |
| `GET /ship/track/` | Estatus y eventos → avisos automáticos al cliente |
| `GET /carrier-branches` | **Catálogo de sucursales** por paquetería y país |
| `GET /validate-zip-code` | Valida el código postal y devuelve ciudad y estado |

**Se cae el único paso manual del sistema.** Hoy el almacén va a Paquete Express,
recoge las guías y las captura en Excel. Con esto, el sistema genera la guía al
confirmarse el pago, le manda el PDF al almacén para que lo imprima y pegue,
programa la recolección y rastrea hasta que el paquete llega a la sucursal.

**Costo:** prepago, sin mensualidad ni comisión. Se carga saldo y se paga por guía.
Va en costos de terceros, junto con WhatsApp API y la comisión de Stripe.

### 5.5 · Otras limitaciones que condicionan el diseño

| Limitación | Consecuencia en este proyecto |
|---|---|
| El bot de Conversation AI **no envía mensajes desde workflows** | Todo outbound programado va con `Send Message`, nunca por el bot |
| El webhook de salida de GHL **no espera respuesta** | Todo ida y vuelta con n8n es asíncrono: n8n responde disparando un Inbound Webhook y un segundo workflow continúa |
| Los campos `Date` de GHL **no guardan hora** | `expira_en` va como campo de **texto**, igual que `fecha_pago`. No vive en n8n: n8n se queda sin estado |
| Un read-check-write concurrente puede dejar el stock en negativo | El flujo de reserva `N1` corre serializado en n8n (concurrencia 1) |
| `Wait` usa **días calendario**, no hábiles | Irrelevante aquí: el apartado es de 24 h literales |

---

## 6. Decisiones de alcance tomadas

| Decisión | Valor | Origen |
|---|---|---|
| Unidad de venta | Paca completa cerrada de 100 lb, de 1 en 1 | Definido con el usuario. No se venden piezas sueltas — obligaría a un inventario por prenda/talla/foto y multiplicaría el proyecto |
| Motor externo | n8n, contra los productos de GHL | Revisión 5: el stock vive en `availableQuantity` del producto. Una herramienta menos que aprender y una fuente de verdad menos que sincronizar |
| Mayoreo | **Fuera de alcance**, sigue manual | Textual del cliente |
| Duración del apartado | 24 h | El cliente pidió 24; nosotros habíamos propuesto 2–3 h |
| Paquetería | **Paquete Express vía Envia.com**, sólo a ocurre | Confirmado en la segunda junta |
| Costo de envío | **Incluido en el precio**, igual a toda la República | Confirmado: *"es a cualquier parte, ya incluido el envío"* |
| Cierre de la venta | **Todo en WhatsApp**; sale una vez a la liga de pago | Revisión 5 — ver `07-decision-checkout.md` |
| Devoluciones | **No hay**, política explícita | *"tratamos que la venta sea sincera y directa: es esto y trae esto y no hay devolución"* |
| Volumen esperado | 500 a 800 envíos al mes, hasta 1,000 | Miguel: *"de acuerdo a la experiencia, arriba de 500 muy fácilmente"* |
| Pasarela | Stripe del cliente (entidad de EE.UU.), cobrando en MXN | Decisión del cliente del 25 sep 2026; antes era Mercado Pago |

---

## 7. Los dos paquetes

Se ofrecen **dos niveles**, y el corte entre ellos no es arbitrario: **el Esencial
es todo lo que GHL hace nativo; el Completo agrega lo que necesita piezas externas.**

### Completo — $4,497 setup / $637 al mes · 3 a 4 semanas

El sistema que el cliente pidió: bot que atiende y califica, tienda con los 30
artículos e inventario en vivo, apartado de 24 h con reloj, cobro por liga de pago
(tarjeta; OXXO y SPEI por validar), guía y recolección automáticas, rastreo hasta la sucursal, buscador de
sucursal por código postal y escalamiento a humano.

1 pipeline de 8 etapas · 8 workflows · 1 agente de 19 nodos · 2 integraciones ·
6 plantillas · catálogo público de 6 secciones · 2 capacitaciones · soporte.

### Esencial — $2,899 setup / $437 al mes · 2 semanas

El mismo agente atendiendo todo el día, pero **sin nada de la operación**. El bot
arma el pedido y **deriva a un asesor**, que confirma disponibilidad y cobra.

1 pipeline de 5 etapas · 5 workflows · 1 agente de 12 nodos · **0 integraciones** ·
3 plantillas · 1 capacitación · soporte.

**No lleva:** inventario conectado, apartado con reloj, cobro automático, aviso al
almacén, guía al cliente ni landing. Nada de n8n, Sheets ni pasarela conectada.

> ⚠️ **Advertencia de alcance, para no vender de más.** El cliente dijo que no
> sobrevender era central — *"tengo tantas de esta y no tengo más"*. **El Esencial
> no resuelve eso.** Resuelve la atención, que es lo que consumía a las cuatro
> vendedoras, pero deja el inventario, el cobro y el despacho en sus manos. Se
> presenta como rampa de entrada para medir volumen, nunca como equivalente.

### Retirado de ambos

Reportes y dashboards, post-venta con reseñas y recompra a 30 días, workflow de
campañas de Meta y TikTok (`LS02`) y el segundo pipeline. Si más adelante los
quieren, se cotizan aparte.

Números y desgloses en `04-precotizacion.md`.

---

## 8. Riesgos abiertos

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | **Faltan los precios de venta por SKU.** Sin ellos no hay bot ni liga de pago | Pregunta bloqueante #1 — pedirla hoy |
| 2 | Templates de Meta sin aprobar al go-live | Redactarlos y enviarlos a aprobación en la semana 1 |
| 3 | Dos clientes apartando la última paca a la vez | n8n serializado; ruta de escape a Supabase documentada |
| 4 | Los dueños ajustan `availableQuantity` a mano mientras hay apartados vivos | n8n es dueño único del contador; el ajuste manual es para reponer, no para corregir apartados |
| 5 | OXXO y SPEI dependen de que el checkout de GHL con Stripe los muestre | Validación 4. Plan B: tarjeta por la liga y transferencia manual con `AP03` |
| 6 | 6 de los 30 SKUs no están descritos en ningún transcript (2 corsé, playera comercial, 2 chamarra, suéter navideño) | El agente no puede describir lo que no sabe — pedir la descripción |
| 7 | **No hay fotos de producto.** La landing y las fichas del bot no se pueden montar sin ellas | Pregunta bloqueante #2. **No están cotizadas**: las produce el cliente |
| 8 | **El almacén nunca debe ver dinero.** Miguel fue explícito: *"ellos no tienen por qué enterarse"* | El aviso al almacén lleva sólo nombre, cantidad, destino y CP. Regla dura del diseño |
| 9 | Piden **fotos y videos** de producto, no sólo fotos | Sube el peso del pendiente de material. Sigue sin cotizarse: lo entrega el cliente |
