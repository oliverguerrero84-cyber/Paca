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
| 4 imágenes o un PDF | **Un video** por paca | Es lo que mandó Pamela: 25 de los 30 |
| Texto del cliente, transcrito tal cual | **Plantilla nuestra con los datos del catálogo** | Greentex no mandó textos. **Pamela tiene que aprobarlos** |
| Guarda por tag `ficha-enviada` | Guarda por **`ficha_sku`** (campo nuevo) | Ver §3: el tag solo no aguanta que `BOT01` vacíe `sku_elegido` |
| La pregunta final pide sede o modalidad | **Pide cuántas pacas** | Es lo único que le falta a `BOT01` para apartar (`cantidad_elegida`) |

## 3. Disparador, guarda y cambio de paca

**Disparador:** *Contact Changed* → `sku_elegido`. Puede escribirlo BOT-00 o el respaldo
`RP-SKU`: el workflow no sabe ni le importa quién fue. Si el bot ya lo escribió y `RP-SKU`
escribe el mismo valor, el campo no cambia y no se dispara dos veces.

**Por qué la guarda no es sólo el tag, como en GALK.** `BOT01 · Apartar paca` **vacía**
`sku_elegido` al terminar (`docs/19-bot-acciones-ghl.md`). Con la guarda de GALK pasan dos
cosas:

1. Vaciar el campo también es un cambio y dispara `SP06`. Se resuelve igual que en GALK:
   **si `sku_elegido` está vacío, sale.**
2. Si el cliente vuelve otro día por otra paca, el tag `ficha-enviada` sigue puesto y la
   guarda **lo bloquea para siempre**. GALK lo resuelve con un conmutador que quita el tag.
   Aquí no hace falta: cada rama pregunta **«¿`ficha_sku` es este SKU?»**. Si sí, ya vio
   esa ficha y sale. Si no, la manda y escribe `ficha_sku`.

Así, **el cambio de paca sale solo**: el cliente pide otra, el bot escribe el SKU nuevo y
llega la ficha nueva. No hacen falta el conmutador ni `WF-SWITCH`. El tag `ficha-enviada` se
queda, pero sólo como señal para `RP-RESCATE`.

> Hace falta **un campo nuevo en el contacto, `ficha_sku` (TEXT)**. Se agrega en
> `scripts/crear-esqueleto-menudeo.py` junto con los otros cuatro de interés.

## 4. La rama de cada paca

| # | Nodo | Lo ve el cliente | Contenido |
|---|---|---|---|
| — | If `ficha_sku` es este SKU | | Si sí, sale |
| 1 | Conversation AI status | | Pausa a BOT-00 para que no interrumpa |
| 2 | WhatsApp texto | **sí** | **Apertura:** pide el nombre, presenta la paca (temporada, calidad, para quién, qué trae, tallas) |
| 3 | Wait 3 s + WhatsApp media | **sí** | **Video** de la paca, si ya está subido |
| 4 | Wait 3 s + WhatsApp texto | **sí** | **Precio y condiciones:** precio por paca, 100 lb, piezas **en rango**, sin piezas sueltas, apartado de 24 h |
| 5 | Wait 3 s + WhatsApp texto | **sí** | **Pregunta final:** «¿Cuántas pacas de *Mujer Verano Boutique* te aparto?» |
| 6 | Update contact field | | `ficha_sku` = este SKU |
| 7 | Add tag | | `ficha-enviada` |
| 8 | Conversation AI status | | Activa BOT-01 · Pedido |

**4 mensajes con video, 3 sin video.** Las dos cuentas caen en el rango de GALK.

Lo que **no** va en la ficha, a propósito: «no hay devoluciones». La regla 7 lo pide antes
de mandar la liga, y eso es en el resumen del pedido de BOT-01, no aquí. Ponerlo antes de
que el cliente diga cuántas quiere sólo frena la venta.

**El video y el límite de WhatsApp.** WhatsApp **no acepta videos de más de 16 MB**, y los
de Pamela pesan de 12 a 50 MB. Hay que comprimirlos antes de subirlos al media store (con
`ffmpeg` a 720p alcanza). El script se niega a armar una rama con un video más pesado.

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
📦 Pesa 100 lb (45 kg) y trae entre 200 y 240 piezas; varía de una paca a otra.
Se vende la paca completa, no piezas sueltas. Al apartarla te la guardamos 24 horas
mientras pagas.

[4] ¿Cuántas pacas de Mujer Verano Boutique te aparto? 😊
```

## 5. Lo que falta para escribirlo en la cuenta

1. **El molde.** Germán arma **a mano en la UI una sola rama completa**, en un workflow
   nuevo cualquiera:
   - If sobre `sku_elegido`;
   - *Conversation AI status* para pausar un bot;
   - WhatsApp de texto;
   - *Wait* de 3 s;
   - WhatsApp con un video;
   - *Update contact field*;
   - *Add tag*;
   - *Conversation AI status* para activar un bot.

   Se guarda, se lee por API y se clona esa forma. **El mismo molde destraba `RP-SKU`**, que
   espera el If con un *Update contact field*.
2. **BOT-00 y BOT-01 tienen que existir en la UI.** El nodo de activar necesita el id del
   bot. Hoy hay un solo bot.
3. **Los videos, comprimidos y subidos al media store.** Faltan 5 en el Drive: Niño Verano
   Premium, Niño Verano Especial, Playera Comercial, Hombre Invierno Boutique y Mixta
   Invierno Plus. Mientras falten, su ficha sale sin video.
4. **Que Pamela apruebe los textos.** Se le manda la salida de `--fichas`.
5. **El campo `ficha_sku`** (§3).

## 6. Decisiones abiertas

| Qué | Propuesta | Quién |
|---|---|---|
| Las 3 pacas en 0 por decisión del cliente (`PV-PLA-EST`, `PV-HOS-EST`, `PI-CHA-BOU`) | Su rama no manda ficha: avisa «por ahora no hay», vacía `sku_elegido` y deja a BOT-00 encendido para ofrecer otra. Si vuelven a tener stock, se quitan de `NO_DISPONIBLES` y se regenera | Oliver / cliente |
| Una paca que se agota **en vivo** | No la resuelve `SP06`: el workflow no ve el stock. La detecta `N1` al apartar (`agotado`) y BOT-01 ofrece otra | — (ya cubierto) |
| Rango de piezas | ±10 % del promedio del Excel, redondeado a 10 (a 5 si son menos de 100): 220 → «entre 200 y 240» | Oliver |
| Emojis y quién firma | Pocos emojis, sin persona inventada. GALK firma como «Valeria»; aquí no hay nombre definido | Oliver / Pamela |
| El video en la ficha o sólo a quien lo pida | **En la ficha**, comprimido. Es lo que más vende y para eso lo filmó Pamela | Oliver |
