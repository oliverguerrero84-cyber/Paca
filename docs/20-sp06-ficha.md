# SP06 · Ficha de la paca — el árbol

> **15 oct 2026.** Diseño del workflow que le manda al cliente la ficha de la paca que
> eligió. Es el `SP05` «Envío de ficha» de GALK adaptado. Se sacó de dos fuentes: la sección
> *«Cómo se envían los mensajes»* de la plantilla (*Plantilla · Ecosistema de ventas con
> IA en GoHighLevel*) y el script que armó ese workflow, `build_sp05_v2.py`, rama por
> rama. Ninguna de las dos está en este repo.
>
> **Se llama `SP06` y no `SP05`** porque `SP05` ya es nuestra orden al almacén, que está
> publicada (`docs/18-arquitectura-asistentes.md` §4).
>
> El generador es `scripts/armar-sp06.py`: arma el workflow con las formas de nodo del kit y
> lo escribe en borrador (§5).

---

## 1. Lo que se copia de GALK tal cual

- **La ficha la manda un workflow, no el bot.** El contenido es siempre el mismo, llega
  completo y en orden, y para cambiarlo se edita un nodo, no se reentrena un prompt.
- **Estructura fija de cada rama:** pausar el bot → los mensajes de la paca, con **3 s**
  entre uno y otro → marcador → activar el bot que sigue.
- **Lo que ve el cliente son de 3 a 7 mensajes**, no «6 a 8». La plantilla de GALK lo dice
  mal: los demás nodos son internos (pausa, esperas, tag, activación).
- **El marcador va después del envío, nunca antes.** Sirve de guarda contra el reenvío y
  de señal para el rescate (`RP-RESCATE`).
- **La pregunta final no la inventa el bot.** Es un texto fijo por rama y pide
  **exactamente el campo que le falta** al siguiente paso. En GALK, la sede en talleres y
  la modalidad en software. Si no falta nada, se cierra ofreciendo el siguiente paso.
- **El nombre se pide en la apertura**, no en la pregunta final, para que el cliente
  conteste el nombre y el dato final en un solo mensaje.
- **Los nodos se clonan de uno vivo**, nunca se inventan. El script es idempotente, tiene
  `--dry-run` y guarda respaldo.

## 2. Lo que cambia aquí, y por qué

| GALK | Paca | Por qué |
|---|---|---|
| 9 ramas a mano en `RAMAS` | **30 ramas generadas** de `data/catalogo.csv` | Treinta a mano no se mantienen; generadas son un `for` |
| Condición «Curso **contiene** melamina»; el orden de las ramas importa | Condición contra la **clave** (`PV-MUJ-BOU`) | Ninguna clave contiene a otra (el script lo valida), así que el orden no importa |
| 3 bots especialistas, uno por familia | **Un solo destino: BOT-01 · Pedido** | Las 30 pacas terminan en la misma conversación (`docs/18` §3) |
| 4 imágenes o un PDF | **Un video** por paca | Es lo que mandó Pamela: 26 de los 30 |
| Texto del cliente, transcrito tal cual | **Plantilla nuestra con los datos del catálogo** | Greentex no mandó textos. **Pamela tiene que aprobarlos** |
| Guarda por tag `ficha-enviada` | Guarda por **`ficha_sku`** (campo nuevo) | Ver §3: el tag solo no aguanta que el cliente vuelva por otra paca |
| La pregunta final pide sede o modalidad | **Pide cuántas pacas** | Es lo único que le falta a `AC01 · Apartar paca` (`cantidad_elegida`) |

## 3. Disparador, guarda y cambio de paca

**Disparador:** *Contact Changed* → `sku_elegido`. Puede escribirlo BOT-00 o el respaldo
`RP-SKU`: el workflow no sabe ni le importa quién fue.

**La guarda tiene dos pisos:**

1. **Si `sku_elegido` está vacío, sale.** Vaciar un campo también cuenta como cambio y
   dispara el workflow.
2. **Cada rama pregunta «¿`ficha_sku` es este SKU?».** Si sí, el cliente ya vio esa ficha y
   sale. Si no, la manda y escribe `ficha_sku`.

**Al terminar, la rama vacía `sku_elegido`.** Es lo que hace que todo lo demás funcione,
por una regla de GHL: *Contact Info* del bot **sólo llena campos vacíos**. Si el campo se
quedara lleno:

- el bot no podría escribir otra paca cuando el cliente cambia de opinión;
- tampoco podría escribir la clave al confirmar el pedido, que es lo que lee
  `AC01 · Apartar paca` (`docs/19-bot-acciones-ghl.md`).

La memoria de qué ficha vio queda en `ficha_sku`.

Con eso, **el cambio de paca sale solo**: el cliente pide otra, el bot escribe el SKU nuevo y
llega la ficha nueva. No hacen falta el conmutador ni `WF-SWITCH` de GALK. Y cuando BOT-01
vuelve a escribir la misma clave para apartar, `SP06` arranca, ve que `ficha_sku` ya es ése y
sale sin reenviar nada.

> **`RP-SKU` actúa sólo antes de la primera ficha:** sale si el contacto ya tiene la
> etiqueta `ficha-enviada`. Si no, una palabra suelta en mitad del pedido («y de mujer
> también tienen?») le mandaría al cliente una ficha que no pidió. El cambio de paca ya
> dentro del pedido lo hace el bot, que entiende el contexto.

> Hace falta **un campo nuevo en el contacto, `ficha_sku` (TEXT)**. Se agrega en
> `scripts/crear-esqueleto-menudeo.py` junto con los otros cuatro de interés.

## 4. La rama de cada paca

| # | Nodo | Lo ve el cliente | Contenido |
|---|---|---|---|
| — | If `ficha_sku` es este SKU | | Si sí, sale |
| 1 | Conversation AI status | | Pausa al bot que esté hablando, para que no interrumpa |
| 2 | WhatsApp texto | **sí** | **Apertura:** pide el nombre, presenta la paca (temporada, calidad, para quién, qué trae, tallas) |
| 3 | Wait 3 s + WhatsApp media | **sí** | **Video** de la paca, si ya está subido |
| 4 | Wait 3 s + WhatsApp texto | **sí** | **Precio y condiciones:** precio por paca, 100 lb, piezas **aproximadas**, sin piezas sueltas, apartado de 24 h |
| 5 | Wait 3 s + WhatsApp texto | **sí** | **Pregunta final:** «¿Cuántas pacas de *Mujer Verano Boutique* te aparto?» |
| 6 | Update contact field | | `ficha_sku` = este SKU |
| 7 | Update contact field | | Vacía `sku_elegido` |
| 8 | Add tag | | `ficha-enviada` |
| 9 | Conversation AI status | | Activa BOT-01 · Pedido |

**4 mensajes con video, 3 sin video.** Las dos cuentas caen en el rango de GALK.

Lo que **no** va en la ficha, a propósito:
- **«No hay devoluciones».** La regla 7 lo pide antes de mandar la liga, y eso ya lo hace
  BOT-01 con la política de venta. Decirlo antes de que el cliente diga cuántas quiere sólo
  frena la venta.
- **Una firma.** Decidido el 15 oct: por ahora sin firma.

**Las piezas van como número aproximado** («aprox. 220 piezas; puede variar un poco»), sale
directo de `piezas_aprox`. Decidido el 15 oct. Sigue cumpliendo la regla 4: no se promete la
cifra exacta.

Un ejemplo completo, tal como sale de `python scripts/armar-sp06.py --fichas`:

```
[1] Antes que nada, ¿cómo te llamas? 😊
Te paso la información de la paca *Mujer Verano Boutique* (verano, calidad Boutique).

Es ropa americana para mujer adulta. Trae: shorts, faldas, pantalones, blusas (manga
corta/tres cuartos/tirantes), vestidos.
Tallas: CH, M, G, XL.

Te comparto el video para que veas cómo viene 👇

[2] (video)

[3] 💰 *$8,900 MXN* por paca.
📦 Pesa 100 lb (45 kg) y trae aprox. 220 piezas; puede variar un poco de una paca a otra.
Se vende la paca completa, no piezas sueltas. Al apartarla te la guardamos 24 horas
mientras pagas.

[4] ¿Cuántas pacas de Mujer Verano Boutique te aparto? 😊
```

**Los videos.** WhatsApp no acepta videos de más de 16 MB y los originales de Pamela pesan
de 12 a 50 MB; además vienen en HEVC, que WhatsApp tampoco reproduce bien. Se convirtieron
el 15 oct a **H.264, 720p y menos de 14 MB** con `ffmpeg`. Las cuatro pacas que todavía no
tienen video mandan su ficha sin él: Niño Verano Premium, Playera Comercial, Hombre Invierno
Boutique y Mixta Invierno Plus.

## 5. Cómo se escribe en la cuenta

**El problema del molde.** Para escribir por API, cada nodo tiene que ir con el formato
**exacto** que GHL usa por dentro. Si se inventa, GHL lo guarda sin error, se ve bien y
**después no ejecuta** (pasó el 1 oct). Por eso la regla es clonar nodos hechos en la UI.

**Lo resolvió el kit (15 oct).** `ghl-kit-2.5.1` trae `wf_toolkit.py`, con la forma
**validada en producción** (GALK) de casi todos los nodos de la rama: WhatsApp de texto,
pausar y activar el bot, espera, actualizar y vaciar campo, tag y el If con varias ramas.
`scripts/armar-sp06.py` arma el workflow entero con esas formas:

```
GHL_KIT=<ruta al kit> python scripts/armar-sp06.py --construir
→ 438 nodos (114 if_else, 84 whatsapp_v2, 78 wait, 57 update_contact_field,
  54 update_conversation_ai_status, 27 add_contact_tag, 24 whatsapp_media)
✓ grafo válido (wf_toolkit.validar_grafo)
```

**Lo que sigue sin probar, y se prueba antes de publicar:**

1. **WhatsApp con video.** El kit validó imagen y PDF con esa misma forma; `video` es la
   apuesta. Si no ejecuta, Germán arma **un** nodo de WhatsApp con video en la UI, se lee y
   se corrige la forma.
2. **El If anidado** («ya vio esta ficha») colgado de cada rama: sigue la regla del kit,
   pero GALK no lo usó.
3. **El tamaño.** Un If de 32 ramas y 438 nodos; GALK tenía 9 ramas. Si el editor no lo
   aguanta, se parte en dos workflows: verano e invierno.

**Pasos, en orden:**

1. `python scripts/crear-esqueleto-menudeo.py` crea el campo `ficha_sku`.
2. `python scripts/subir-videos-sp06.py <carpeta-con-los-mp4>` sube los 26 videos al media
   store y escribe `data/videos-sp06.json` (URL, nombre y peso; sin credenciales).
3. Crear `BOT-00 · Recepción` en la UI y anotar dos ids: el del bot `BOT-01 · Pedido` y el
   del número de WhatsApp (`from_phone_number` de cualquier nodo WhatsApp hecho en la UI).
   Van al entorno como `SP06_BOT_PEDIDO` y `SP06_WA_PHONE`.
4. `python scripts/armar-sp06.py --aplicar <carpeta-respaldo>` escribe `SP06` en
   **borrador y sin trigger**, con «Allow re-entry» prendido.
5. En la UI: trigger *Contact Changed* → `sku_elegido`, «Guardar trigger», probar con un
   contacto de prueba (*Add to workflow*) y **publicar con el toggle**.

Los pasos 1, 2 y 4 escriben en la cuenta: los corre Germán con `!`, con sus credenciales.

**Hecho el 15 oct (sesión de Oliver):**
- Paso 1: campo `ficha_sku` creado (`kMAgZh3gket966NXI5fY`), en la carpeta de `sku_elegido`. Leído de vuelta.
  Sólo ése: los otros tres de interés del esqueleto siguen sin crear porque nadie los usa.
- Paso 2: los 26 videos subidos al media store; `data/videos-sp06.json` tiene sus URLs (servidas: 200, `video/mp4`).
- Paso 3: ids encontrados por API, sin tocar la UI:
  - `SP06_WA_PHONE` = `1249676184905074` (+1 956-820-2011, Cloud API, TIER_250), de
    `GET backend/phone-system/whatsapp/location/{loc}/phone-numbers`.
  - `SP06_BOT_PEDIDO` = `VYk3iHgASTUXZplxGuJ9`: el bot **«Pacas»** de Germán (apagado, 1 acción), que pasa a
    `BOT-01 · Pedido`. De `GET /conversation-ai/agents/search` (versión `2021-04-15`).
- **Paso 4 hecho:** `SP06 · Ficha de la paca` creado (`76e40d3c-bdce-478e-82e7-737ca57a8ff8`), en **borrador, sin
  trigger**, `allowMultiple: true`. Leído de vuelta: 438 de 438 nodos, el video, el número de WhatsApp y el bot
  destino como se mandaron. Se corrió con el modo de permisos manual y aprobación de Oliver.
- **Paso 5, 16 oct:** trigger *Contact Changed* → «SKU elegido» puesto y publicado. Prueba con «Oliver pruebas»
  (`mYCfS5pytOf4w2eMS4oP`) por *Test Workflow*: quedaron `ficha_sku = PV-MUJ-BOU`, `sku_elegido` vacío y el tag
  `ficha-enviada`; los 4 mensajes (apertura, **video**, precio, pregunta) se intentaron en orden, cada 4–8 s. Fallaron
  por la **ventana de 24 h** («more than 24 hours have passed since the customer last replied»): el contacto nunca le
  escribió al número. Con un cliente real no pasa. Además, la cuenta sigue restringida por Meta (`docs/14` §0).
  - **El filtro de etiqueta en *Contact Changed* no sirve para probar:** se guarda como «se agregó la etiqueta»
    (`add-index-of-true`), así que exige que la etiqueta y el SKU cambien en el mismo evento. Nunca dispara. Se quita.
  - **Falta ver:** que el bot quede activo en la conversación (no se lee por API) y que el video llegue de verdad.

## 6. Los nombres

En la subcuenta van a convivir bots y workflows con prefijos parecidos. Para que no se
confundan:

| Pieza | Nombre | Qué es |
|---|---|---|
| Bot de Conversation AI | **`BOT-00 · Recepción`** | Nuevo. Averigua qué paca y escribe `sku_elegido` |
| Bot de Conversation AI | **`BOT-01 · Pedido`** | **El bot que ya armó Germán**, recortado: de la ficha al envío |
| Workflow | **`SP06 · Ficha de la paca`** | Este documento |
| Workflow | **`RP-SKU · Respaldo de detección`** | `scripts/armar-rp-sku.py` |
| Workflow | **`RP-RESCATE`** | Recibió la ficha y no apartó |
| Workflows de las acciones del bot | **`AC01 · Apartar paca`** … **`AC05 · Rastrear envío`** | Lo que el bot dispara con *Trigger a workflow*. **`BOT01 · Apartar paca` pasa a `AC01`**: con «BOT01» se confunde con el bot BOT-01 |

Los prompts de los dos bots viven en el Cortex: `empresa/clientes/greentex-clothing/agente/`.

## 7. Decisiones

| Qué | Decisión | Cuándo |
|---|---|---|
| Las 3 pacas en 0 por decisión del cliente (`PV-PLA-EST`, `PV-HOS-EST`, `PI-CHA-BOU`) | Su rama no manda ficha: avisa «por ahora no hay», vacía `sku_elegido` y deja al bot encendido para ofrecer otra. Si vuelven a tener stock, se quitan de `NO_DISPONIBLES` y se regenera | 15 oct, Oliver |
| Una paca que se agota **en vivo** | No la resuelve `SP06`: el workflow no ve el stock. La detecta `N1` al apartar (`agotado`) y BOT-01 ofrece otra | Ya cubierto |
| Piezas | Número aproximado, no rango | 15 oct, Oliver |
| Firma | Sin firma por ahora | 15 oct, Oliver |
| El video en la ficha | Sí, comprimido | 15 oct |
| Los textos de las fichas | **Falta que Pamela los apruebe** | Pendiente |
