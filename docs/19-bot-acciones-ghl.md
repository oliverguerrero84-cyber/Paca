# Acciones del bot de GHL («Trigger a workflow»)

> **Corte: 15 de octubre de 2026.** Cómo el bot de Conversation AI llama a los workflows
> de GHL, que a su vez llaman a n8n. Origen: repo Cortex, `agente/acciones-bot.md`.

**Qué cambió en la subcuenta el 15 oct (ya aplicado):**
- **`PRUEBA N1` pasó a `BOT01 · Apartar paca`** (5 nodos, publicado, mismo trigger `prueba-n1`): si el contacto
  tiene `sku_elegido`, manda `sku` y `cantidad` del contacto al webhook `{{custom_values.url_n8n_crear_apartado}}`
  y **vacía** ambos campos. Probado de punta a punta con la oportunidad «Prueba BOT01»: N1 respondió, quedó
  liga, vencimiento y estado «apartado», y el stock bajó.
- **Campos de contacto nuevos (texto):** `sku_elegido` y `cantidad_elegida`. Los bots no escriben menús
  desplegables y «Contact Info» solo llena campos vacíos, por eso el workflow los vacía al terminar.
- **`url_n8n_crear_apartado`** = `https://devn8n.korvance.com/webhook/apartar`. El host que muestra el nodo
  Webhook de n8n (`devwebhookn8n.korvance.com`) **no enruta**: revisar `WEBHOOK_URL` del servidor.
- **Inventario:** 8 SKUs de calidad única renombrados (`-UNI` → `-EST`/`-PLU`/`PI-SUE-NAV`) y existencias de la
  hoja del cliente cargadas (133 pacas; `PV-PLA-EST`, `PV-HOS-EST`, `PI-CHA-BOU` en 0 por decisión del cliente).
- **Quedó en vivo:** una factura de $9,900 y 1 paca (`PI-NIN-BOU`) apartada de esa prueba; N2 la libera al vencer.

**Pendiente (n8n):** N1 descuenta el stock antes de crear la factura; N2 devuelve de menos si dos vencidos son
del mismo SKU; key de Google Maps; URLs de Envia a producción.

**Pendiente (workflows GHL):** corregir `PRUEBA N3` (llama a `generar-guia`) y `PRUEBA N5` (trigger `prueba-n3`,
`webhook-test`); construir confirmar domicilio, guardar envío y el que devuelve las sucursales al cliente.

---

## Reglas comunes
- **Solo aparecen workflows publicados** en el selector de la acción.
- **Los datos viajan por el contacto.** El bot los guarda en campos del contacto y el workflow los lee con
  `{{contact.campo}}`. La acción no pasa parámetros ni devuelve respuesta.
- **Contact Info solo llena campos vacíos**: cada workflow debe **vaciar** los campos que usó al terminar.
- **Los bots no escriben menús desplegables**: los campos del puente son de texto.
- **Límite de 500 caracteres** en el *When to trigger* de cada acción.
- **Cada workflow debe tener «Allow re-entry»**.

## Las seis acciones

| # | Acción | Workflow | n8n | Estado |
|---|---|---|---|---|
| 1 | Apartar paca | `BOT01 · Apartar paca` | N1 `/apartar` | **Corregido y probado** |
| 2 | Buscar sucursales | `PRUEBA N3 - webhook buscar sucursal` | N3 `/buscar-sucursal` | **Roto**: llama a `generar-guia`; ningún workflow manda las opciones al cliente (hace falta uno con Inbound Webhook, como `AP01`) |
| 3 | Confirmar domicilio | no existe | N6 `/geocodificar-domicilio` | **Por construir** (y falta la key de Google Maps) |
| 4 | Guardar envío | no existe | N6 `/guardar-envio` | **Por construir**; requiere pedido abierto |
| 5 | Rastrear envío | `PRUEBA N5 - webhook` + `AP01` | N5 `/rastrear` | **Corregir**: trigger `prueba-n3`, `webhook-test`, falta que el estatus llegue al cliente |
| 6 | Escalar a una persona | `AP02 · Escalamiento a humano` | — | **Listo** (correo a dueños) |

### *When to trigger* (≤500 caracteres, listos para pegar)

**1 · Apartar paca**
```
Cuando el cliente ya dijo qué paca quiere y cuántas, aceptó la política de venta, confirmó el resumen del pedido y quiere apartarla. Antes de disparar, el contacto debe tener guardados correo, teléfono, la clave de la paca y la cantidad. Apártala antes de preguntar por el envío.
```

**2 · Buscar sucursales**
```
Cuando el cliente ya apartó su paca, eligió envío a ocurre y te dio su código postal de 5 dígitos, y ya lo guardaste en su contacto. Nunca adivines la sucursal.
```

**3 · Confirmar domicilio**
```
Cuando el cliente quiere envío a domicilio y ya dictó su dirección completa, con número, y ya la guardaste en su contacto. Nunca des por buena una dirección sin que el cliente la confirme.
```

**4 · Guardar envío**
```
Cuando el cliente ya tiene su paca apartada y eligió una sucursal de la lista, o confirmó con un sí su dirección. Antes de disparar, guarda en su contacto la modalidad y la sucursal elegida o la dirección confirmada.
```

**5 · Rastrear envío**
```
Cuando el cliente pregunta dónde va su paquete o cuándo llega, y ya tiene una guía.
```

**6 · Escalar a una persona**
```
Cuando el cliente pide hablar con una persona, tiene un reclamo o un paquete que no llega, quiere cambiar la dirección después de pagar, está molesto, pide mayoreo o descuento, tiene un problema con el pago o pide factura fiscal con RFC.
```

## Campos de contacto que el bot llena (texto)

| Dato | Campo | Nota |
|---|---|---|
| Clave de la paca | `sku_elegido` | Creado el 15 oct; BOT01 lo vacía al terminar |
| Cantidad | `cantidad_elegida` | Ídem |
| Código postal | `codigo_postal` | Existe |
| Sucursal elegida | `sucursal_ocurre` y `branch_code` | Existen |
| Dirección completa | — | **Falta crear** (texto) |
| Modalidad (sucursal o domicilio) | — | **Falta crear** (texto) |

Hay dos juegos de campos con el mismo nombre (contacto y oportunidad). En el selector de GHL se llaman igual:
escoger el equivocado deja el mensaje vacío o el If siempre en falso, sin error. Los de oportunidad los escribe
n8n; los de contacto, el bot.

## Lo que no resuelve esto solo
- Los mensajes al cliente son **SMS `[TEMPORAL]`**, no WhatsApp, hasta que haya plantillas aprobadas por Meta.
- Ningún workflow saca al contacto del bot al pagar o despachar.
- La acción *Trigger a workflow* se configura **a mano** en la interfaz del bot; no hay API.
