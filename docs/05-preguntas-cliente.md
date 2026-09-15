# Preguntas abiertas para el cliente

Ordenadas por urgencia. **Las primeras seis bloquean la construcción** — sin
ellas no se puede armar el bot ni cerrar el alcance.

---

## 🔴 Bloqueantes — sin esto no se puede construir

### 1. Empresa proveedora de los envíos
¿Con quién se despacha y bajo qué modalidad? Históricamente usaban Paquete Express
con servicio a ocurre, pero el proveedor de este sistema está por confirmar.

De esta respuesta salen tres cosas: las **tarifas** (y por lo tanto el total que
cobra el bot), las **coberturas**, y **qué datos tiene que pedirle el bot al
cliente**. Si se mantienen en modalidad a ocurre, basta con ciudad y sucursal; si
pasan a entrega a domicilio, hay que rehacer la captura de dirección — que es
justamente lo que los desbordó la vez pasada.

### 2. Imágenes de las pacas
Fotos de cada uno de los 30 artículos. **Sin ellas no hay landing de catálogo** ni
fichas que el bot pueda mandar por WhatsApp.

Este dato subió de prioridad al incluir la landing en el alcance: un catálogo web
no se puede montar sin imágenes. **No están cotizadas** — la producción del
material la hace el cliente.

### 3. Descripciones de los artículos
Qué trae cada paca y para quién es, en texto listo para publicar. Sirve para dos
cosas: la landing y la Knowledge Base del agente.

Cinco de los treinta **no están descritos en ningún transcript** y el agente no
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

### 11. WhatsApp: ¿número nuevo o el actual?
¿Meta Business Manager ya verificado? Un número que hoy usan en la app de WhatsApp
normal **no puede** migrarse a la API sin perder el historial. Conviene número nuevo
dedicado al bot.

### 12. Cuenta de Mercado Pago
¿Ya la tienen abierta y **verificada**? Sin las verificaciones de identidad y
fiscales, Mercado Pago retiene fondos según el flujo recibido. Ya salió en la
llamada; quedamos de enviarles los requisitos.

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

---

## Resumen para la llamada

Si sólo hay tiempo para pedir tres cosas: **los precios por SKU** (#4), las
**fotos** (#2) y el **proveedor de envíos** (#1). Sin precios el bot no puede
cotizar, sin fotos no hay landing y sin proveedor no se sabe qué total cobrar.

Las descripciones (#3) y las piezas por paca (#5) el cliente ya se ofreció a
mandarlas — basta con recordárselo. El resto se puede resolver en paralelo con la
construcción.
