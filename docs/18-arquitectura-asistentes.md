# Arquitectura de asistentes y workflows — adaptada de la plantilla GALK

> De dónde sale: *Plantilla · Ecosistema de ventas con IA en GoHighLevel* (Profit
> Technology / GHL Team Latam, 14 oct 2026), el ecosistema que corre en producción para
> **Grupo GALK**, un instituto técnico en Perú: 11 cursos en 3 familias, ~90 leads al día,
> 6 asesores. Oliver la pasó el 14 oct para replicar el patrón aquí.
>
> **Esto no es una copia.** GALK vende información y entrega el lead a un humano; nosotros
> vendemos inventario y cerramos la venta en la conversación. Abajo está qué se toma tal
> cual, qué se adapta y qué no aplica — con el porqué en cada caso.

---

## 1. Lo que hay que llevarse, aunque duela

**«La IA detecta, los workflows ejecutan.»** Es el principio rector de GALK y es, de todo
el documento, lo que más nos sirve: **los bots sólo escriben campos del contacto**; cada
campo que cambia dispara el workflow que depende de él, y los workflows hacen todo lo que
tiene efecto hacia afuera — mandar la ficha, calificar, avisar.

La razón no es estética. Textual de la plantilla:

> *«la ejecución de acciones de Conversation AI es intermitente del lado de GHL»*

**Y ahí está el hueco de nuestro diseño actual.** `docs/01-mapa-ghl.md` §3 pone al bot a
hacer casi todo: califica, resuelve dudas, ayuda a elegir, manda foto y video, junta los
datos, llama **cinco acciones Custom API**, da el resumen, avisa que no hay devoluciones,
pide confirmación, aparta y manda la liga. Si una de esas acciones no ejecuta ese turno
—y la plantilla dice que pasa—, el cliente se queda esperando algo que nunca llega.

GALK pagó ese error con leads reales y lo resolvió con **dos capas redundantes**: el bot
escribe el campo, y si falla, un workflow de palabras clave escribe el mismo campo 30
segundos después. **Eso hay que traerlo.**

---

## 2. Qué se toma, qué se adapta, qué no aplica

| De la plantilla | Aquí |
|---|---|
| «La IA detecta, los workflows ejecutan» | **Tal cual.** Es el cambio de fondo |
| Respaldo determinístico por palabras clave | **Tal cual**, pero en **un** workflow generado, no tres. Ver §5bis |
| Campos gemelos `(bot)` + normalizadores | **No aplica.** Ver §5bis |
| La ficha la manda un workflow, no el bot | **Tal cual**, y resuelve qué hacer con los 25 videos de Pamela |
| Marcador `ficha-enviada` + guarda contra reenvío | **Tal cual** |
| El conmutador (cambia de producto → limpia y reenvía) | **Tal cual** |
| Árbol de ramas por producto | **Se adapta**: 30 ramas, pero generadas por script desde `data/catalogo.csv` |
| 4 bots (router + 3 especialistas) | **Se adapta a 2.** Ver §3 |
| Redes de rescate | **Se adapta**: la nuestra es «recibió la ficha y no apartó» |
| Auto Followup en el bot (3 toques) en vez de workflow | **Tal cual.** Un workflow dormiría al bot |
| SP06 calificación + round robin a 6 asesores | **No aplica.** Aquí no se entrega el lead: se cobra |
| Cadena de pago SP09–SP12 | **Parcial.** Ya tenemos `SP04` y `AP03`; sirve la disciplina de cerrar en un solo lugar |
| Las 3 reglas de método (molde antes que invento, «se guardó» no es «funciona», scripts idempotentes) | **Ya las vivimos.** `armar-workflows.py` y los de ramas ya traen `--dry-run` y respaldo |

---

## 3. Dos bots, no ocho

Oliver preguntó si conviene derivar a un asistente por tipo de paca. **La respuesta es no,
y el motivo está en la plantilla misma**: GALK tiene 3 especialistas porque sus 3 familias
terminan en **preguntas finales distintas** — sede en talleres, modalidad en software y
gestión. Son conversaciones diferentes.

Aquí no. Las 30 pacas terminan en **la misma conversación**: cuántas quieres → tus datos →
sucursal o domicilio → confirmas → apartas y pagas. Lo que cambia entre una paca y otra es
**el contenido de la ficha**, no el flujo. Y los bots de Conversation AI **se configuran
sólo desde la UI, no hay API**: ocho bots son ocho ediciones a mano cada vez que cambie una
frase.

| Bot | Cuándo habla | Objetivo único | Qué escribe |
|---|---|---|---|
| **BOT-00 · Recepción** | Primer contacto, lo enciende `LS01` | Averiguar **qué paca**. No da precios ni stock ni piezas | `temporada`, `categoria`, `calidad`, `sku_elegido` (gemelos `(bot)`) |
| **BOT-01 · Pedido** | Después de la ficha, lo enciende `SP05` | Cerrar: cantidad, datos, envío, apartado y liga | Los datos del pedido; aquí viven las 5 acciones Custom API |

**Por qué igual son dos y no uno.** La lección más dura de la plantilla es la **división de
turnos**: el router promete y el workflow entrega; el especialista **arranca desde la
respuesta** y tiene prohibido re-presentar el producto. Meterlo todo en un prompt es
exactamente lo que la plantilla señala que falla — *«prompts largos desobedecen: unas 500
palabras con prohibiciones claras rinden más que 1.200»*.

> **Opcional, no ahora:** un tercer bot de **postventa/rastreo**. Hoy `N5` y `AP01` empujan
> el rastreo solos, así que no urge. Si se agrega, es para que el prompt de Pedido no
> cargue lógica que usa una de cada veinte veces.

---

## 4. Las capas, con lo nuestro dentro

```
Cliente escribe por WhatsApp
      │
      ▼
LS01 · Entrada ......................... atribución UTM, enciende BOT-00, oportunidad
      │
      ▼
BOT-00 · Recepción ◄──── respaldo RP01..RP0n (palabras clave, sin IA, 30 s)
      │                   las dos capas escriben LO MISMO
      ▼
  sku_elegido ......................... EL CAMPO QUE DISPARA TODO
      │
      ▼
SP06 · Ficha de la paca ................ apaga el bot · video + descripción + precio
      │                                  pregunta final · tag ficha-enviada
      │                                  enciende BOT-01
      ▼
BOT-01 · Pedido ........................ cantidad, correo, teléfono
      │                                  ├─ apartar (N1) → liga de pago
      │                                  ├─ sucursal (N3) / domicilio (N6)
      │                                  └─ guardar envío (N6)
      ▼
N1 crea la oportunidad ................. de aquí en adelante los datos viven AHÍ
      │
      ▼
SP02 · Reloj del apartado (ya existe) .. 24 h, recordatorios, vence y libera
      │
      ▼
SP04 pago · SP05 almacén · AP04 envío · N5 rastreo · AP01 aviso   (ya existen)

           RP-RESCATE · recibió ficha y no apartó a las 2 h → avisa a los dueños
```

**Cambia la numeración.** Lo que la plantilla llama `SP05` (envío de ficha) aquí **no puede
llamarse `SP05`**: ese nombre ya es nuestro workflow de orden al almacén. Propuesta: la
ficha es **`SP06`** y los respaldos por palabra clave son **`RP01…`** (*respaldo*), para no
pisar la numeración viva de `docs/01-mapa-ghl.md`.

---

## 5. El árbol de fichas: 30 ramas, generadas

GALK arma su árbol a mano en un script con una lista `RAMAS`. Nosotros tenemos algo que
ellos no: **un catálogo estructurado**. `data/catalogo.csv` ya trae los 30 SKUs con
temporada, categoría, calidad, tallas, público, contenido y peso; y el Drive de Pamela trae
**25 videos, uno por SKU**.

Entonces el árbol **no se escribe, se genera**: un script lee el CSV, y por cada SKU emite
una rama con su video, su descripción y su precio. Treinta ramas a mano son inmantenibles;
treinta ramas generadas son un `for`.

**Dos decisiones que lo hacen robusto:**

1. **La condición se compara contra la clave, no contra el nombre.** GALK tiene que ordenar
   sus ramas con cuidado porque *«Supervisión de Melamina» contiene «Melamina»* y gana la
   primera que coincide. Nosotros comparamos contra **`PV-MUJ-BOU`**, que no colisiona con
   nada. Es una ventaja que ellos no tenían, y conviene no desperdiciarla usando el nombre.
2. **El respaldo también se genera, y del mismo catálogo.** Ver §5bis.

---

## 5bis. Dos correcciones al construir — 14 oct

Al medir el catálogo antes de escribir el primer script salieron dos cosas que **desmienten
lo que este mismo documento proponía** un par de horas antes. Quedan corregidas aquí, y la
versión de arriba ya no es la que se va a construir.

### El respaldo no puede ser «por dimensión»

Decía: tres workflows (temporada / categoría / calidad) y un cuarto que compone el SKU. **No
sirve.** Medido sobre `data/catalogo.csv`:

| | SKUs |
|---|---:|
| Se identifican con **la pura categoría** (disfraz, suéter navideño, hospital, casa, vestido, playera) | **6** |
| Necesitan **dos** dimensiones (corsé y chamarra piden calidad; mixta pide temporada) | **6** |
| Necesitan **las tres** | **18** |

Componer el grid de 18 con condiciones de GHL es un árbol inmanejable. Y no hace falta: ésos
son justo los casos donde el cliente va y viene con el bot, y si ahí falla una acción **el
cliente vuelve a contestar y se corrige solo**. Donde el respaldo sí salva la venta es en el
mensaje suelto —«quiero una de disfraces»— que espera ficha y nunca la recibe.

**Queda como un solo workflow, `RP-SKU`, generado desde el catálogo**, que baja sólo el nivel
que cada rama necesita: categoría → temporada (si hay dos) → calidad (si hay varias). Lo
genera `scripts/armar-rp-sku.py`, que **se niega a escribir** si una palabra clave está en dos
categorías o si una categoría del catálogo se quedó sin palabras.

### Se caen los gemelos `(bot)` y sus normalizadores

GALK los necesita porque **sus campos son desplegables** y los bots de Conversation AI no
pueden escribir desplegables. Aquí nada aguas abajo necesita un desplegable: `sku_elegido` es
`TEXT` y es lo único que dispara. Copiar el gemelo sería copiar la solución de un problema que
no tenemos — cuatro campos y cuatro workflows que no le sirven a nadie.

Los cuatro campos de interés (`sku_elegido`, `temporada_interes`, `categoria_interes`,
`calidad_interes`) van **TEXT y directos**, ya en `scripts/crear-esqueleto-menudeo.py`.

---

## 6. La fricción real: contacto vs oportunidad

**Esto es lo que no se puede copiar sin pensar, y es lo más importante del documento.**

Toda la arquitectura de GALK cuelga de **campos del contacto**: un campo cambia, un workflow
dispara. Limpio y predecible.

Pero nuestra decisión #6 (28 sep) dice que **los datos de cada pedido viven en la
oportunidad, no en el contacto** — porque un cliente puede comprar varias veces y el
apartado, el pago y la guía son de *ese* pedido. Y ya tenemos documentado que **un `If`
sobre un campo de oportunidad necesita un `Find opportunity` antes**, y que *Update
opportunity* no hace nada si el workflow no arranca por una oportunidad.

Las dos cosas son correctas. La frontera:

| | Dónde vive | Por qué |
|---|---|---|
| **Antes de apartar** — temporada, categoría, calidad, SKU de interés, atribución | **Contacto** | Es interés, no pedido. Y es lo que tiene que disparar workflows al cambiar |
| **Desde que se aparta** — cantidad, monto, expira, pago, envío, guía | **Oportunidad** | Es *ese* pedido. La crea `N1` |

**El corte es exacto: el momento en que `N1` crea la oportunidad.** Antes de eso, el patrón
de GALK aplica tal cual. Después, manda lo nuestro.

---

## 7. Lo que la plantilla no resuelve, y aquí es obligatorio

Ninguna de estas tiene equivalente en GALK, porque ellos no venden inventario. Hay que
cuidarlas al adoptar el patrón:

1. **El apartado de 24 h con reloj y stock real.** n8n es el **dueño único del contador**, y
   `N1` corre con **concurrencia 1**. Ningún workflow de GHL toca stock.
2. **Un solo pedido abierto por cliente.** Si ya tiene uno sin cerrar, `N1` contesta
   `pedido_en_curso`.
3. **Mayoreo siempre escala a humano.** Es regla del cliente, no preferencia.
4. **No hay devoluciones, y se dice antes de mandar la liga** — nunca después de cobrar.
5. **Las acciones Custom API tienen 10 segundos.** Si `N1` tarda más, el bot contesta sin
   la liga.
6. **Nunca decir «económica»**: la calidad baja se llama **Especial**.
7. **Las piezas por paca van en rango**, nunca cifra exacta. El peso sí es fijo: 100 lb.

Las nueve reglas permanentes de `docs/01-mapa-ghl.md` §3 **siguen vigentes tal cual**. Esta
arquitectura cambia **quién ejecuta**, no **qué se le promete al cliente**.

---

## 8. Qué construir, y en qué orden

El orden de la plantilla es bueno y vale aquí: estructura → bots → workflows → auditoría →
publicar a mano.

| # | Qué | Notas |
|---|---|---|
| 1 | ~~Campos gemelos~~ → **4 campos de interés, TEXT** | **Hecho** (14 oct), en `crear-esqueleto-menudeo.py` |
| 2 | ~~Normalizadores~~ | **Se cayeron.** Ver §5bis |
| 3 | **`RP-SKU`** · respaldo generado del catálogo | **Generador hecho** (`scripts/armar-rp-sku.py`); falta el molde del nodo |
| 4 | **BOT-00 · Recepción**, en la UI | Prompt corto, ~500 palabras, con prohibiciones |
| 5 | **`SP06` ficha**, generado desde `data/catalogo.csv` | **Diseño y generador hechos** (15 oct): `docs/20-sp06-ficha.md`, `scripts/armar-sp06.py`. Falta el molde |
| 6 | **BOT-01 · Pedido**, con las 5 acciones Custom API | Las que ya están especificadas en §3 del mapa |
| 7 | **`RP-RESCATE`**: recibió ficha, no apartó en 2 h → avisa | El hueco que hoy no tenemos |
| 8 | **Auditar y publicar uno por uno desde la UI** | «Publicar por API es ruleta» |

> **Lo que frena el paso 3.** El árbol está correcto y verificado, pero falta el **molde**:
> un nodo `update_contact_field` con un `If` encima no existe todavía en la cuenta para
> clonarlo. Hay que armar **una** rama a mano en la UI, leerla por API y clonar esa forma —
> como se hizo con `AP04`. Inventar el nodo es justo lo que `docs/16-guias-workflows.md`
> dice que no se haga: se guarda, se ve bien y no ejecuta.

~~**Bloqueante antes del paso 4:** precios~~ — **llegaron el 15 oct** en el Excel del catálogo y ya
están en `data/catalogo.csv` (`precio_mxn`, `piezas_aprox`).

---

## 9. Lo que falta decidir

| Qué | Quién |
|---|---|
| Confirmar la renumeración (`SP06` ficha, `RP*` respaldos) para no pisar lo vivo | Oliver y Germán |
| Si el bot de postventa/rastreo entra ahora o después | Oliver |
| ~~Cuántos mensajes lleva la ficha~~ — 3 o 4 que ve el cliente (GALK manda de 3 a 7, no «6 a 8»). Ver `docs/20-sp06-ficha.md` | Hecho, 15 oct |
| Si el video va en la ficha o se manda sólo a quien lo pide | Oliver. Pesan 12–50 MB |
| Las listas de palabras clave reales | **Se sacan de conversaciones de verdad**, no se inventan |
