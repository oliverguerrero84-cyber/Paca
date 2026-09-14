# Preguntas abiertas para el cliente

Ordenadas por urgencia. **Las primeras cuatro bloquean la construcción** — sin
ellas no se puede armar el bot ni cerrar el alcance.

---

## 🔴 Bloqueantes — sin esto no se puede construir

### 1. Precio de venta por SKU en menudeo
No aparece en ninguna de las cuatro llamadas ni en el PDF. **Es el dato que más
falta.** Sin precios no hay bot que cotice, ni liga de pago, ni monto que cobrar.

¿Un precio por calidad (Boutique / Premium / Especial) o precio distinto por cada
uno de los 30 SKUs? ¿Hay descuento por volumen dentro del menudeo (ej. 3 pacas)?

### 2. Envío: ¿se cobra, cuánto, va incluido?
Nunca se habló. Cambia la liga de pago, el mensaje del bot y el cálculo del total.
Con servicio a ocurre suele cobrarse aparte, pero hay que confirmarlo.

### 3. Cantidad de piezas por paca
El cliente **ya se ofreció a mandarlo**: *"te puedo sacar los estándares"*.
Es de las preguntas que más hacen los compradores. Se sabe que varía (verano
~185–225; invierno menos porque la ropa es más voluminosa) pero falta el estándar
por SKU. Mientras no llegue, el bot tiene que responder con rango.

### 4. Stock inicial por SKU asignado a menudeo
¿Cuántas pacas de cada uno de los 30 SKUs se destinan al menudeo? Es la carga
inicial de la columna `disponible`. La plantilla está lista en
`data/plantilla-stock.csv`.

---

## 🟡 Importantes — definen comportamiento del sistema

### 5. ¿Venta mínima?
¿Se puede comprar 1 paca o hay mínimo?

### 6. Guía: ¿quién la captura y desde qué dispositivo?
El almacén va a abrir un formulario y escribir el número de guía. ¿Lo hace desde
celular o computadora? ¿Una persona fija o varias? Define cómo se le hace llegar el
link del formulario.

### 7. Sucursal "ocurre": ¿lista cerrada o texto libre?
El bot tiene que capturar dónde recoge el cliente. Dos opciones:
- **Lista cerrada** de sucursales de Paquete Express → más limpio, pero hay que conseguir y mantener el catálogo.
- **Texto libre** (ciudad + sucursal) → más rápido de implementar, el almacén confirma después.

Recomendación: texto libre en Fase 1, lista cerrada en Fase 2 si la operación lo pide.

### 8. Confirmar las 24 horas de apartado
El cliente dijo 24 h; Omnia había propuesto 2–3 h en la llamada. El mapa está
construido sobre **24 h**. Confirmarlo, porque 24 h implica que más mensajes caen
fuera de la ventana de WhatsApp y necesitan template aprobado.

### 9. WhatsApp: ¿número nuevo o el actual?
¿Meta Business Manager ya verificado? Un número que hoy usan en la app de WhatsApp
normal **no puede** migrarse a la API sin perder el historial. Conviene número nuevo
dedicado al bot.

### 10. Cuenta de Mercado Pago
¿Ya la tienen abierta y **verificada**? Sin las verificaciones de identidad y
fiscales, Mercado Pago retiene fondos según el flujo recibido. Ya salió en la
llamada; Omnia quedó de enviarles los requisitos.

---

## 🟢 Deseables — se pueden resolver después

### 11. Facturación CFDI
No se habló y en México es común que el comprador la pida. Si la necesitan, es una
integración adicional que hoy **no está cotizada**.

### 12. Devoluciones y garantía
¿Qué pasa si la paca llega dañada o el cliente reclama? El bot debería saber qué
responder. No se habló en ninguna llamada.

### 13. Descripción de 5 SKUs
Estos cinco **no están descritos en ningún transcript** y el agente no puede
describir lo que no sabe:

- `CORSE VERANO BOUTIQUE` y `CORSE VERANO PREMIUM`
- `PLAYERA COMERCIAL`
- `CHAMARRA BOUTIQUE` y `CHAMARRA PREMIUM`
- `SUÉTER NAVIDEÑO`

Hace falta: qué trae, para quién es y qué tallas.

### 14. Redes sociales
Facebook está apagada pero recuperable; Instagram y TikTok se borraron. ¿Se
reactivan con el lanzamiento del menudeo? Define si `LS02` (campañas Meta/TikTok)
entra en Fase 1 o Fase 2.

---

## Resumen para la llamada

Si sólo hay tiempo para pedir una cosa: **los precios por SKU** (#1). Sin eso el
proyecto no arranca. Lo demás se puede ir resolviendo en paralelo con la
construcción.
