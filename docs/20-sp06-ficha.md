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
> El generador es `scripts/armar-sp06.py`. **Hoy sólo imprime el árbol**: escribir en la
> cuenta necesita el molde del §5.

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

## 5. El molde: qué es y cómo se arma

**El problema.** Para escribir las 30 ramas por API, el script tiene que mandarle a GHL cada
nodo con el formato **exacto** que usa GHL por dentro. Ese formato no está documentado. Si
se inventa, GHL lo guarda sin error, se ve bien en la pantalla y **después no ejecuta**. Ya
nos pasó el 1 oct.

**La solución, la misma de GALK.** Se arma **una sola rama a mano** en la interfaz, con un
nodo de cada tipo. Esa rama es el **molde**. Se lee por API y el script copia esa forma 30
veces, cambiando sólo el texto, el video y la clave. Así, cada nodo que escribe el script es
idéntico a uno que la propia interfaz de GHL creó. `build_sp05_v2.py` hace lo mismo: clona
la pausa del bot de `SP06` y la activación de `LS01`.

**Cómo armarlo (lo hace Germán, unos 10 minutos):**

1. Workflow nuevo, **`MOLDE · SP06`**. **Sin trigger**: así nunca se publica ni corre.
2. *If/Else*: «`sku_elegido` es `PV-MUJ-BOU`».
3. Dentro de la rama «sí», en este orden:
   1. **Conversation AI** → poner el bot en inactivo (la pausa).
   2. **WhatsApp** de texto: «prueba 1».
   3. **Wait** de 3 segundos.
   4. **WhatsApp** con video, adjuntando `PV-MUJ-BOU.mp4` de los comprimidos. Así también
      se prueba que la cuenta lo acepta.
   5. **Update contact field**: `ficha_sku` = `PV-MUJ-BOU`.
   6. **Update contact field**: vaciar `sku_elegido`, igual que ya lo hace `AC01`.
   7. **Add tag**: `ficha-enviada`.
   8. **Conversation AI** → activar un bot (cualquiera, el que haya).
4. Guardar, **no publicar**, y leerlo por API. El JSON va a `data/moldes/sp06.json`: no
   trae credenciales, sólo la forma de los nodos.

**El mismo molde destraba `RP-SKU`**, que espera justo un If con un *Update contact field*.

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
