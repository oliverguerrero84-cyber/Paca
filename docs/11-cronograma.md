# Cronograma interno — 4 semanas al go-live

> **Interno. No sale del equipo.** Es el plan de construcción del paquete Completo,
> ya pagado. Arranca el **martes 22 de septiembre de 2026** y entrega el **martes 20
> de octubre de 2026**.
>
> El contrato dice *"3 a 4 semanas desde la sesión de mapeo"* y la sesión **todavía
> no ocurre**. Este cronograma asume que el onboarding cae **dentro de la semana 1**.
> Si se recorre, la entrega se recorre el mismo número de días: no se compensa
> apretando las semanas 3 y 4, porque ahí no hay holgura.

---

## 1. El marco

| Semana | Fechas | Qué se cierra |
|---|---|---|
| **1** | 22 – 28 sep | Onboarding, accesos, los 3 supuestos y las plantillas a Meta |
| **2** | 29 sep – 5 oct | Motor: inventario, apartado de 24 h y cobro |
| **3** | 6 – 12 oct | Conversación y logística |
| **4** | 13 – 20 oct | Punta a punta, capacitación y entrega |

**El mes de gracia de la mensualidad arranca el 20 de octubre.** El primer cargo de
los USD 637 cae alrededor del **20 de noviembre**.

---

## 2. Las dos cosas que arrancan el día 1, pase lo que pase

No dependen del Excel, ni de las fotos, ni de nada que tenga que mandar el cliente.
Son las únicas dos con plazo externo, y por eso van primero aunque el onboarding se
atrase.

**Las 4 plantillas que necesitan aprobación de Meta.** Redactarlas y mandarlas en la
semana 1. Meta puede tardar días y puede rechazarlas: si salen en la semana 3, no hay
go-live en la 4. Está marcado como riesgo vivo en `docs/10-contexto-completo.md` §8.

> **Orden, no se invierte.** Las plantillas viven dentro de una WhatsApp Business
> Account, y la WABA no existe hasta que el número está dado de alta en Meta. Por eso
> el alta de **+1 (956) 820-2011** va también en la semana 1, antes que las
> plantillas. Que el número sea nuevo y sin usar es lo que permite adelantarla sin
> riesgo: no hay app que apagar ni historial que perder.
>
> Por validar en cuenta: que GHL permita el alta y la creación de la WABA sin tener el
> agente armado. Si no, las plantillas se mandan desde Business Manager directo — pero
> el alta sigue siendo de la semana 1.

**La validación 1 — que la liga de pago cobre con Mercado Pago.** Sostiene todo el
diseño. Si falla, el Plan B es cobrar por el checkout de la tienda y **renunciar al
apartado de 24 h**, que es justo lo que el cliente pidió como un boleto de concierto.
Hay que saberlo antes de prometerlo en la reunión de onboarding, no después.

---

## 3. Semana 1 · 22 – 28 sep — Onboarding, accesos y supuestos

**El orden importa y está en `docs/13-accesos.md`.** Aquí van las fechas; allá va qué
habilita a qué. Esta tabla sigue esa cadena, no al revés.

| Qué | Quién | Nota |
|---|---|---|
| **Reunión de onboarding (mapeo)** | 786 + cliente | Es la compuerta. Todo lo demás cuelga de aquí |
| Salir de la reunión con fecha comprometida del Excel | 786 | `entregables/catalogo-menudeo-para-llenar.xlsx` ya está en sus manos |
| **Rotar el PIT de Korvance** | 786 | Eslabón `0.1`. Se compartió en texto plano por chat |
| **Crear la subcuenta**, pipeline `SP · Menudeo` de 8 etapas, campos custom y custom values | 786 | Eslabón `0.2`. **Es la raíz**: sin ella no hay productos, ligas ni workflows |
| **Levantar la instancia de n8n** y dejar sus URLs en los custom values | 786 | Eslabón `0.3`. Habilita los 5 flujos y la validación 3 |
| Verificar el Meta Business Manager y agregar a 786 como socio | Cliente | `A1` y `A2`. Es el primer bloqueante del carril más largo |
| Confirmar que el número recibe SMS o llamada de voz | 786 | `A3`. No espera a nadie, y si es VoIP hay que conseguir otro número |
| Redactar las 6 plantillas | 786 | `A5`. Tampoco espera a nadie: se adelanta |
| **Dar de alta el número en Meta y crear la WhatsApp Business Account** | 786 | `A4`. Necesita `A2` |
| **Mandar las 4 plantillas a Meta** | 786 | `A6`. Necesita `A4`. Cuello de botella: 24 a 48 h y puede rechazar |
| Conectar Mercado Pago con las credenciales de 786 | 786 | `B1` y `B2`. En Korvance, sin esperar al cliente |
| **Validación 1** — la liga cobra con Mercado Pago | 786 | `B3`. Con monto mínimo real, no en papel |
| **Validación 2** — pagar la liga no descuenta stock solo | 786 | `B4`. Si lo descontara, vuelve el doble descuento |
| **Validación 4** — `Payment Received` dispara con los tres métodos | 786 | `B5`. Arrancar la de efectivo ya: OXXO tarda hasta 72 h hábiles |
| **Validación 5** — Agent Studio soporta los nodos diseñados | 786 | `D1`. Prueba de humo en Korvance. Si no puede, se rediseña el carril del agente entero |
| Arrancar verificación de identidad y fiscal en Mercado Pago | Cliente | `B6`. Ya no bloquea el diseño, pero sí el cobro real |
| Abrir cuenta de Envia.com y fondearla | Cliente | `C1` y `C2`. Prepago, sin mensualidad ni comisión |
| Cargar los 30 SKUs con nombre y las 24 descripciones que sí existen | 786 | Precio y stock se llenan después |

**Cierre de la semana:** la subcuenta y n8n de pie, las plantillas en cola de Meta, y
las validaciones 1, 2 y 4 respondidas con sí o no.

> **La validación 3 se movió a la semana 2.** Mide cuánto tarda el nodo `API Call` en
> recibir respuesta de `N1`, y `N1` no existe hasta la semana 2. Probarla antes es
> medir contra nada.

---

## 4. Semana 2 · 29 sep – 5 oct — Motor: inventario, apartado y cobro

Es la semana de la pieza que más miedo les da: *"tengo tantas de esta y no tengo
más."*

| Qué | Nota |
|---|---|
| `N1` apartar — serializado, concurrencia 1 | El que evita que dos clientes aparten la última paca |
| **Validación 3** — el nodo `API Call` responde a tiempo | Va aquí y no en la semana 1: necesita `N1` vivo para medir contra algo |
| `N2` liberar vencidos — cron cada 15 min | El reloj que suelta lo que no se pagó |
| `SP02` apartado de 24 h, recordatorios y liberación | 16 nodos. El más grande de los 9 |
| `SP03` crea la liga de pago por la API de Invoices | 12 nodos |
| `SP04` pago confirmado → número de orden | Goal Event `Payment Received` |
| **Prueba de concurrencia** | Dos apartados simultáneos de la última paca. Una tiene que perder limpio |
| Recoger el resultado de la prueba de OXXO | Se lanzó en la semana 1 con la validación 4. Acredita en hasta 72 h hábiles |
| Cargar precios, piezas y stock inicial | **Sólo si ya llegó el Excel** |

**El Excel bloquea el contenido, no la plomería.** Los 9 workflows, los 5 flujos de
n8n y el agente se construyen igual sin él. Lo que no se puede sin precios es que el
bot cotice y genere liga, y eso se prueba de verdad hasta la semana 4.

---

## 5. Semana 3 · 6 – 12 oct — Conversación y logística

| Qué | Nota |
|---|---|
| **Agente de Agent Studio, 19 nodos** | A mano: los bots no tienen API. Es el bloque más lento de la semana |
| Knowledge Base: subir **y asociar** al agente | Son dos pasos. Subir no es asociar |
| Campo de texto gemelo + workflow normalizador | Un bot no escribe en listas desplegables (`SINGLE_OPTIONS`) |
| `LS01` entrada de lead · `SP01` handoff y bot on/off · `AP02` escalamiento a humano | 26 nodos entre los tres |
| `N3` buscar sucursal por código postal | Consulta a tabla contra Envia, nunca IA |
| `N4` generar guía · `N5` rastrear | Paquete Express a ocurre |
| `SP05` despacho: guía + PDF al almacén + correo a los dueños | **Sin el monto.** El almacén nunca ve dinero |
| `AP01` rastreo hasta "llegó a tu sucursal" | |
| Enganchar el canal de WhatsApp al agente | El alta del número ya ocurrió en la semana 1. Aquí sólo se conecta al bot, y es trabajo de interfaz |
| Cargar fotos y videos al catálogo del bot | Miguel: *"quieren ver un video a través del WhatsApp"* |

**Ojo con el Transfer Bot.** Una condición agresiva se roba el primer turno y las
capturas nunca corren. Se prueba turno por turno, no se da por bueno porque se guardó.

---

## 6. Semana 4 · 13 – 20 oct — Punta a punta, capacitación y entrega

| Qué | Nota |
|---|---|
| **Recorrido completo, 3 pedidos de prueba** | Uno con tarjeta, uno con OXXO, uno con SPEI |
| Probar que el apartado se extiende con efectivo | El choque conocido: OXXO 72 h contra apartado de 24 h |
| Probar que el aviso al almacén **no lleva monto** | Regla de diseño de Miguel: *"ellos no tienen por qué enterarse"* |
| Probar que el bot avisa que **no hay devoluciones antes de cobrar** | Nunca después |
| `AP03` registro manual de pagos por transferencia | 7 nodos. El último |
| Confirmar las plantillas aprobadas por Meta | Si alguna se rechazó, hay que rehacerla ya |
| **Capacitación a Pamela, Miguel y Mauricio** | Dónde ven ventas, dónde editan stock, cómo apagan el bot |
| Entrega | Arranca el mes de gracia |

Lo que se prueba aquí no es que los nodos existan: es que **corren**. GHL guarda y
muestra nodos mal formados que después no ejecutan, sin dar ningún error.

---

## 7. Lo que tiene que llegar del cliente, y cuándo

| Qué | Límite | Qué se cae si llega tarde |
|---|---|---|
| Meta Business Manager verificado | 29 sep | Sin esto no hay WABA, y sin WABA no salen las plantillas |
| Verificación de Mercado Pago iniciada | 29 sep | Retiene fondos al go-live |
| **Excel lleno: precios, piezas y stock** | **5 oct** | Después de esta fecha, la entrega del 20 se mueve |
| Las 6 descripciones que faltan | 5 oct | `CORSE VERANO BOUTIQUE`, `CORSE VERANO PREMIUM`, `PLAYERA COMERCIAL`, `CHAMARRA BOUTIQUE`, `CHAMARRA PREMIUM`, `SUÉTER NAVIDEÑO` |
| Cuenta de Envia.com con saldo | 5 oct | `N4` no puede generar guías |
| Fotos y videos de los 30 artículos | 12 oct | El catálogo del bot llega vacío al go-live |

Nada de esto mueve el precio. Todo mueve la fecha.

---

## 8. Puntos de no retorno

**Las plantillas no salieron a Meta en la semana 1.** No hay go-live el 20. Es el
único plazo que no controlamos y no se puede comprimir.

**La validación 1 falló.** Se cae el apartado de 24 h y entra el Plan B. Hay que
decírselo al cliente **la misma semana**, no en la entrega: el apartado es una de las
cosas que compró.

**El Excel llegó después del 5 de octubre.** La entrega se recorre día por día. No se
absorbe: la semana 4 son pruebas de punta a punta, y sin precios no hay qué probar.

**Mercado Pago sigue sin verificar al 13 de octubre.** Se puede entregar, pero el
dinero se queda retenido y el cliente lo va a sentir como una falla del sistema.
Conviene avisarlo por escrito antes.

---

## 9. Qué no está aquí

Fuera de alcance y ya cotizado aparte si lo quieren: reportes y dashboards,
post-venta con reseñas y recompra, campañas de Meta y TikTok, el segundo pipeline, la
venta de piezas sueltas, la facturación CFDI y la pauta publicitaria.

Tampoco está el **mayoreo**, que sigue manual y aparte por decisión del cliente.

Y queda pendiente de nosotros, sin fecha dura porque ya no bloquea: el **logo de 786
Marketing** en la propuesta.
