# Preguntas abiertas para el cliente

Ordenadas por urgencia. **Las primeras seis bloquean la construcción** — sin
ellas no se puede armar el bot ni cerrar el alcance.

---

## 🔴 Bloqueantes — sin esto no se puede construir

### 1. ~~Empresa proveedora de los envíos~~ — RESUELTA

Confirmado en la segunda junta: **Paquete Express, sólo a ocurre**, vía Envia.com.
Y el **envío va incluido en el precio**, igual a toda la República — lo que además
cierra la pregunta del costo de envío que arrastrábamos.

> Miguel: *"yo pongo una paca de seis mil trescientos pesos, es a cualquier parte,
> ya incluido el envío, a cualquier parte de la República."*

Queda un pendiente menor: **pedir tarifas a Envia.com** para su volumen real
(500–800 guías al mes) y confirmar que la cuenta permite filtrar paqueterías.

### 2. Imágenes **y videos** de las pacas
Fotos de cada uno de los 30 artículos, **y videos**. En la segunda junta Miguel lo
subrayó: *"luego piden, oye, video, quieren ver un video a través del WhatsApp"*.

**Sin ellos no hay tienda** ni fichas que el bot pueda mandar. **Bloquea el
Completo, no el Esencial.** **No están cotizados**: la producción la hace el cliente.

### 3. Descripciones de los artículos
Qué trae cada paca y para quién es, en texto listo para publicar. Sirve para dos
cosas: la landing y la Knowledge Base del agente.

Seis de los treinta **no están descritos en ningún transcript** y el agente no
puede describir lo que no sabe: `CORSE VERANO BOUTIQUE`, `CORSE VERANO PREMIUM`,
`PLAYERA COMERCIAL`, `CHAMARRA BOUTIQUE`, `CHAMARRA PREMIUM` y `SUÉTER NAVIDEÑO`.

### 4. Precio de venta por SKU en menudeo
No aparece en ninguna de las cuatro llamadas ni en el PDF. **Es el dato que más
falta.** Sin precios no hay bot que cotice, ni liga de pago, ni monto que cobrar.

¿Un precio por calidad (Boutique / Premium / Especial) o precio distinto por cada
uno de los 30 SKUs? ¿Hay descuento por volumen dentro del menudeo (ej. 3 pacas)?

### 5. Cantidad de piezas por paca
El cliente **ya se ofreció a mandarlo**: *"te puedo sacar los estándares"*.
Es de las preguntas que más hacen los compradores. Se sabe que varía (verano
~185–225; invierno menos porque la ropa es más voluminosa) pero falta el estándar
por SKU. Mientras no llegue, el bot tiene que responder con rango.

### 6. Stock inicial por SKU asignado a menudeo
¿Cuántas pacas de cada uno de los 30 SKUs se destinan al menudeo? Es la carga
inicial de la columna `disponible`. La plantilla está lista en
`data/plantilla-stock.csv`.

**Sólo aplica al Completo.** El Esencial no lleva inventario conectado: el asesor
confirma existencia a mano.

---

## 🟡 Importantes — definen comportamiento del sistema

### 7. ¿Venta mínima?
¿Se puede comprar 1 paca o hay mínimo?

### 8. Guía: ¿quién la captura y desde qué dispositivo?
El almacén va a abrir un formulario y escribir el número de guía. ¿Lo hace desde
celular o computadora? ¿Una persona fija o varias? Define cómo se le hace llegar el
link del formulario.

### 9. Sucursal "ocurre": ¿lista cerrada o texto libre?
El bot tiene que capturar dónde recoge el cliente. Dos opciones:
- **Lista cerrada** de sucursales del proveedor → más limpio, pero hay que conseguir y mantener el catálogo.
- **Texto libre** (ciudad + sucursal) → más rápido de implementar, el almacén confirma después.

Recomendación: texto libre en esta entrega y lista cerrada más adelante, si la
operación lo pide. Depende del proveedor que elijan (pregunta #1).

### 10. Confirmar las 24 horas de apartado
El cliente dijo 24 h; nosotros habíamos propuesto 2–3 h en la llamada. El mapa está
construido sobre **24 h**. Confirmarlo, porque 24 h implica que más mensajes caen
fuera de la ventana de WhatsApp y necesitan template aprobado.

### 11. ~~WhatsApp: ¿número nuevo o el actual?~~ — RESUELTA a medias

El número del bot es **+1 (956) 820-2011**, y es **nuevo, sin usar**. Nadie lo trae
en el celular, así que no aplica la pérdida de historial que advertía esta pregunta:
darlo de alta en la API no apaga nada.

Es un número de McAllen, y eso no estorba. WhatsApp corre sobre datos —el comprador
mexicano no paga larga distancia— y Meta cobra la conversación según el país de
**quien recibe**, así que la tarifa sigue siendo la de México.

Quedan dos cabos, los dos nuestros y los dos de la semana 1:

- **¿El Meta Business Manager ya está verificado?** Es la otra mitad de esta pregunta
  y sigue abierta. Sin BM verificado no hay WhatsApp Business Account.
- **¿El número recibe SMS o llamada de voz?** Meta manda el código de verificación por
  uno de los dos. Si resultara ser VoIP, el alta puede fallar y habría que conseguir
  otro — mejor saberlo ahora que en la semana 3.

> El alta de este número **habilita el envío de las plantillas a Meta**, que es el
> plazo más largo del proyecto. Por eso subió a la semana 1 en
> `docs/11-cronograma.md`.

### 12. Cuenta de Stripe
**Cambió el 25 de septiembre:** el cobro va por Stripe, con la cuenta de EE.UU. del
cliente, no por Mercado Pago. Dos cosas que sólo ellos pueden hacer:

- **¿Quién conecta Stripe en Greentex?** Se hace desde Pagos → Integraciones con su
  propio inicio de sesión de Stripe; 786 no necesita sus llaves. Sin esto no corren
  las validaciones 1, 2 y 4.
- **¿Quién activa OXXO y transferencia bancaria de México en su panel de Stripe?**
  Stripe los permite a cuentas de EE.UU. cobrando en pesos. Que aparezcan en el
  checkout de GHL es lo que se prueba en la validación 4; si no aparecen, el menudeo
  cobra con tarjeta por la liga y las transferencias se registran a mano.

---

## 🟢 Deseables — se pueden resolver después

### 13. Facturación CFDI
No se habló y en México es común que el comprador la pida. Si la necesitan, es una
integración adicional que hoy **no está cotizada**.

### 14. Devoluciones y garantía
¿Qué pasa si la paca llega dañada o el cliente reclama? El bot debería saber qué
responder. No se habló en ninguna llamada.

### 15. Redes sociales
Facebook está apagada pero recuperable; Instagram y TikTok se borraron. ¿Se
reactivan con el lanzamiento? El workflow de campañas (`LS02`) **salió del
alcance**, así que hoy los leads entran por WhatsApp, por los canales que sigan
vivos y por la landing. Si quieren pauta, se cotiza aparte.

### 16. ¿El cliente podrá preguntarle al bot por su paquete?

Hoy **no**, y conviene que lo sepan antes de la entrega, no después.

El rastreo está diseñado **sólo de ida**: n8n vigila el envío y dispara los avisos
—"va en camino", "llegó a tu sucursal"—. Pero si el comprador escribe *"¿dónde está mi
pedido?"* antes de que llegue el aviso, el agente no tiene cómo contestarle: sus 19
nodos terminan cuando el pedido queda armado, y su Knowledge Base es el catálogo, no
las órdenes. La única salida es escalar a un humano a mano.

Con servicio a ocurre —el cliente tiene que ir físicamente por su paquete— y 500 a 800
envíos al mes, va a pasar seguido. Y es justo el dolor que describió Pamela:

> *"Oye, no me llegó y que no sé qué. Y ahí, órale, a rastrear."*

**Qué costaría agregarlo:** un `API Call` más en el agente y un flujo de n8n que
consulte `ship/track` por número de orden — reaprovecha lo que `N5` ya hace contra
Envia. No es alcance contratado, así que se cotiza aparte.

Un detalle que juega a favor: como el cliente escribe primero, la respuesta es **mensaje
libre y no necesita plantilla de Meta**. No suma trámite, sólo construcción.

---

## Resumen para la llamada

Ya sólo quedan **dos cosas que de verdad bloquean**: los **precios por SKU** (#4) y
el **material de producto** — fotos y videos (#2) más las descripciones (#3).

Sin precios el bot no puede cotizar ni se puede armar la tienda. Sin material no hay
tienda que mostrar. Las piezas por paca (#5) y el stock inicial (#6) el cliente ya
se ofreció a mandarlos: basta con recordárselo.

El proveedor de envíos y el costo del envío **se cerraron en la segunda junta**.
