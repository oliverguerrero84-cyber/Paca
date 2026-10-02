# Proyecto Paca — instrucciones para Claude Code

Automatización del **menudeo** de un negocio de **pacas de ropa americana** de 100 lb
(Pamela, Miguel y Mauricio Hernández — McAllen TX, almacén en Nuevo Laredo,
Tamaulipas). Lo construye **786 Marketing** sobre GoHighLevel. El **mayoreo queda
aparte y manual**, textual del cliente: *"mi mayoreo yo lo trabajo aparte, no se
entromete con mi menudeo"*.

**Si te acabas de incorporar:** `docs/10-contexto-completo.md` es el proyecto
entero en una sola lectura y `docs/14-estado.md` dice en qué va hoy. Lee los dos
antes de tocar nada.

**Si te dicen «continuemos»:** retoma desde `docs/14-estado.md` §0 «Continuar desde
aquí». Ahí están el siguiente paso exacto, los accesos que hacen falta y las decisiones
que siguen pendientes. Al cerrar la sesión, **deja §0 al día** para el siguiente.

**Herramientas que ya existen, antes de escribir otra:**
- `scripts/subir-n8n.py` sube los flujos del repo a n8n por la API, con las credenciales reales.
- `scripts/probar-n1.sh` prende `N1`, le hace un pedido de prueba con «Prueba Paca» y lo apaga. Los flujos de
  n8n viven **apagados**; prenderlos lo corre una persona con `!`, igual que escribir workflows.
- **Para probar un workflow sin esperar horas**, las esperas se adelantan a mano en *Enrollment history*.
- `scripts/crear-esqueleto-menudeo.py` crea pipeline, campos (de contacto y de oportunidad) y custom values.
- `scripts/probar-factura.py` y `scripts/probar-envia.py` prueban la API de facturas y la de Envia.
- `scripts/armar-workflows.py` crea los workflows de GHL por la API interna, **en línea recta**.
  ⚠️ No correrlo con `--aplicar` sobre `SP02`, `SP05` ni `AP01`: reescribe el workflow entero y borra sus ramas.
- `scripts/ramas-sp02.py`, `ramas-sp05.py`, `ramas-ap01.py` y `aviso-pago-sin-pedido.py` les pusieron condiciones y avisos. Se corren **una vez**:
  verifican la forma de antes y guardan respaldo.

**Escribir un workflow vivo lo corre Germán**, con `!` en el prompt: el clasificador de Claude Code
bloquea esa escritura. Leer workflows, y editarlos en el navegador, sí lo hace Claude. El canje del
token de la API interna da **429** si se repite en menos de un minuto; se espera y se reintenta.

Todos leen sus credenciales del entorno.

---

## Reglas duras

### Rama

Se trabaja y se empuja a **`claude/cool-dirac-4sht9y`**. Nunca a otra sin permiso
explícito.

### La cuenta de GoHighLevel

Todo lo que se construya va a la subcuenta del cliente:

| | |
|---|---|
| Subcuenta | **Greentex Clothing LLC** — McAllen, Texas |
| `GHL_LOCATION_ID` | `c9jj5uu1WZOIkwi6Vfj5` |
| Zona horaria | `America/Chicago` |
| Moneda | **MXN** — desde el 25 sep 2026. **GHL no convierte**: la liga sale en la moneda de la subcuenta |

El id no es un secreto —GHL lo muestra en la URL y sin token no sirve de nada— y cada
corrida del CLI lo necesita. **El token sí lo es**: va en `GHL_API_KEY`, se lee del
entorno y nunca se escribe a un archivo. **Ninguna credencial entra al repo**, y
`docs/09-conversacion.md` **no se regenera** hasta filtrar los tokens que pasaron por
el chat: tal como está, ese export se llevaría tres PIT y dos tokens de Firebase a
GitHub.

**El PIT es por subcuenta.** Si la API contesta *"The token does not have access to
this location"*, el token se creó en la subcuenta equivocada — no le faltan permisos.
Averiguarlo ya costó una vuelta entera.

**Korvance ya no es la cuenta de trabajo.** Fue el ambiente donde se armó el
formulario de alta y ahí se queda; nada nuevo va ahí.

### Precios cerrados (18 sep 2026)

| | Esencial | Completo |
|---|---:|---:|
| Implementación | **$2,899** | **$4,497** |
| Mensualidad | **$437** | **$637** |

### Lo interno nunca sale al documento del cliente

`propuesta/propuesta-paca.html` es lo único que ve el cliente. **Jamás** puede
contener:

- el piso de negociación (**$2,599** y **$4,300**) ni la holgura
- ninguna cifra en **pesos mexicanos**, ni el reparto con 786
- el **primer año** ($8,143 y $12,141) — se quitó a propósito para que la cifra anual
  no opaque la mensualidad
- datos de contacto de ningún tipo

Todo eso vive en `docs/04-precotizacion.md` y ahí se queda.

### Checklist del HTML

Está también en el comentario del `<style>` de la página, y no se negocia:

- **sin emojis** — los iconos son glifos CSS (`.gl`)
- **sin `transition: all`**
- **colores sólo desde `:root`** — cero hex, `rgb()` o `hsl()` sueltos
- estados de **`:focus-visible`**, **`:active`** y **`[disabled]`**
- **`prefers-reduced-motion`** respetado
- sin `{{marcadores}}` sin resolver
- la marca es **786 Marketing**; cero menciones a Omnia

### Verificar significa medir

No supongas que el responsivo está bien. Ábrelo en Chromium
(`/opt/pw-browsers/chromium`, Playwright ya está en `/opt/node22/lib/node_modules`) a
**320, 400, 560, 768 y 1280 px**, haz un `window.scrollTo(500, 0)` **de verdad** y
comprueba que `window.scrollX === 0`. Medir `scrollWidth` a secas da falsos positivos:
ya pasó una vez con la tabla comparativa y se coló un desbordamiento a 320 px.

### Lo que falla en silencio

Ninguna de éstas da error. Se guardan, se ven bien y después no funcionan:

- **`expira_en` va en ISO 8601 con offset**, siempre — `2026-09-25T18:30:00.000Z`. Es
  un contrato entre `N1`, `N2` y `SP02`. Si alguien lo escribe «25/09 6:30 pm», `N2` no
  puede compararlo y **el apartado no se libera nunca**: la paca queda muerta y nadie se
  entera. Por eso el campo es `TEXT` y no `DATE` — los `DATE` de GHL no guardan hora.
- **`N1` corre con concurrencia 1.** No se ve en el JSON: es configuración de la
  instancia (*Settings → Concurrency*). Sin eso, dos clientes apartando la última paca
  en el mismo segundo dejan el stock en negativo.
- **Al almacén nunca le va el monto.** Textual de Miguel sobre el almacén: *"ellos no
  tienen por qué enterarse"*. Ni `monto_apartado`, ni el precio, ni nada que se le
  parezca.
- **Las acciones Custom API tienen 10 segundos.** Si `N1` tarda más, el asistente no
  recibe nada y le contesta al cliente sin la liga.
- **GHL guarda y muestra nodos malformados que después no ejecutan**, sin avisar. Que
  un workflow se vea armado en la interfaz no quiere decir que corra.
- **`GET /products/` no trae precios.** Un flujo que busque el `sku` ahí contesta
  «agotado» con stock de sobra, sin error. El stock se lee con `GET /products/inventory`
  (una llamada: `sku`, cantidad, price y product) y se escribe reescribiendo el price
  **completo**, porque el `PUT` parcial da 422. Pasó el 25 sep en la primera prueba de `N1`.
- **La instancia de n8n bloquea `$env`.** Los flujos leen su configuración de un nodo
  `Config` al inicio de cada uno, no de variables de entorno. Si alguien vuelve a poner
  `$env.…`, el nodo falla con *«access to env vars denied»*.
- **El Webhook de un workflow de GHL no manda el body plano.** Los campos de *Custom
  Data* llegan dentro de `body.customData` y el contacto como `contact_id`; la acción
  Custom API del bot sí los manda planos. Un flujo que lea sólo `body.sku` recibe vacío y
  contesta `sku_no_existe` con stock de sobra. Los cinco flujos ya aceptan las dos formas.
- **Los custom fields no vienen con su clave.** `GET /contacts/{id}` los trae sólo como
  `{ id, value }`; las oportunidades, como `fieldValue` al leerlas por id y como
  `fieldValueString` / `fieldValueNumber` en la búsqueda. Buscar por `fieldKey` da `null`
  siempre, y así `N2` no liberaba nada. Se traduce clave → id con
  `GET /locations/{id}/customFields?model=…` y se escribe por id.
- **Una oportunidad por pedido depende de un ajuste de la subcuenta.** *Settings → Objects →
  Opportunities → «Allow multiple opportunities per contact»*, activado en Greentex el 29 sep
  (`allowDuplicateOpportunity: true`). Si alguien lo apaga, crear la oportunidad del segundo
  pedido da 400 `OPPORTUNITY_NO_DUPLICATE` aunque la anterior esté cerrada. `N1` la crea
  **antes** de tocar stock, así que falla sin descontar nada, pero el cliente no puede comprar.
  No se ve en el repo: el token de la subcuenta no puede cambiarlo (401), sólo la UI.
- **El `version` del workflow es control de concurrencia.** Sube con cada PUT, y hay que
  **releer el workflow justo antes de cada escritura**. Con uno viejo, el API contesta
  *«Your version is outdated, please refresh your page»* — que suena a problema del
  navegador y **se confunde con que el nodo es inválido**. Pasó el 1 oct: siete tipos de
  nodo parecían rechazados y en realidad sólo el primer PUT fue real.
- **El PUT de un workflow es todo o nada, y sí dice qué falla.** Un error de grafo no
  guarda ni un nodo, ni los buenos; pero el motivo viene en el **cuerpo** de la
  respuesta (*«action has a corrupted type»*, *«parentKey points to X…»*), no como
  excepción. Buena parte de la fama de que GHL falla en silencio, aquí, es código que no
  lee la respuesta.
- **Crear un trigger PUBLICA el workflow**, aunque el body diga `active: false`. El
  `status` del workflow y el `active` del trigger son el mismo interruptor. Y la
  **etiqueta tiene que existir antes** de escribir un trigger de tag, o queda en
  «Selecciona una etiqueta» y no dispara.
- **Un If sobre un campo de oportunidad necesita antes un nodo *Find opportunity*.** Sin él, en un
  workflow que no arranca por la oportunidad, la condición no tiene de dónde leer y se va siempre por
  el *else*. Y en el selector hay **dos** «Etiqueta PDF», «Estado del apartado»…: la de *Contact
  details* es la vieja y vacía. Hay que escoger la de *Opportunities*.
- **El Inbound Webhook nuevo (premium) no mapea el contacto.** No hay dónde poner `contactId`; un
  *Create contact* busca por email y teléfono y **duplica** al cliente. Se resuelve con *Find contact*
  por Contact ID como primer nodo (`AP01`).
- **La acción *Update opportunity* no hace nada si el workflow no arranca por una oportunidad**
  y no hay un *Find opportunity* antes (lo dice su propia ayuda). `SP04` (pago recibido) y `AP03`
  (formulario) lo tenían así hasta el 2 oct: el pago entraba y el pedido no se movía.
- **«Allow re-entry» apagado deja entrar a cada cliente una sola vez en su vida.** Es
  `allowMultiple` en *Settings* del workflow. Sin él, el segundo pedido de un cliente no dispara
  `SP02`, `SP04` ni `SP05`, y `AP01` sólo recibe el primer aviso de rastreo. Todos lo llevan
  prendido menos `LS01`. `armar-workflows.py` lo forzaba a `false` hasta el 2 oct; ahora lo copia.
- **Una etiqueta que no existe en la cuenta deja el nodo con aviso de error**, y los triggers de
  tag no disparan. Hay que crearla antes (`POST /locations/{id}/tags`). Le pasó a `apartado-vencido`.
- **El Custom Data de un Webhook de workflow va en `customData`**, no en `data`. Por API, `data`
  se guarda sin error y el webhook sale vacío (le pasó a `SP05` el 1 oct).
- **`N5` avisa una sola vez por estado** porque guarda el último en `opportunity.estado_envio`. Si
  alguien borra ese campo, `N5` se detiene con error; sin él, mandaría el mismo SMS cada hora.
- **Un solo pedido abierto por cliente a la vez**, por diseño: si tiene uno sin cerrar, `N1`
  contesta `pedido_en_curso`. Por eso el pedido tiene que cerrarse (`abandoned` al vencer,
  `won` al entregarse), o el cliente ya no puede volver a comprar.

---

## Dónde está cada cosa

| Ruta | Qué es |
|---|---|
| `docs/14-estado.md` | **En qué va todo hoy** — hecho, en curso, bloqueado y por quién |
| `docs/10-contexto-completo.md` | **Empieza aquí.** Todo el proyecto en una lectura, más cómo montarlo en tu computadora |
| `docs/11-cronograma.md` | Las 4 semanas al go-live, con fechas y puntos de no retorno — **interno** |
| `docs/13-accesos.md` | **El orden de las altas.** Qué habilita a qué, y quién lo hace — **interno** |
| `docs/08-traspaso.md` | Tu tarea concreta y cómo arrancar la sesión |
| `docs/00-alcance-tecnico.md` | Qué se puede construir y qué lleva cada paquete |
| `docs/01-mapa-ghl.md` | Pipeline, workflows, bot de Conversation AI y landing |
| `docs/02-arquitectura-inventario.md` | Inventario, apartado de 24 h, concurrencia |
| `docs/03-catalogo-productos.md` | Los 30 SKUs — fuente de la Knowledge Base |
| `docs/04-precotizacion.md` | Números, margen y piso — **interno** |
| `docs/05-preguntas-cliente.md` | Lo que falta preguntarle al cliente |
| `docs/06-logistica-envia.md` | Envia.com: guías, recolección y rastreo |
| `docs/07-decision-checkout.md` | Por qué el cobro va por liga y no por la tienda |
| `docs/09-conversacion.md` | Cómo se llegó a cada decisión — **no es fuente de verdad** |
| `docs/12-alta-subcuenta.md` | Los campos para dar de alta la subcuenta del cliente en GHL |
| `docs/15-plantillas.md` | Las 7 plantillas de mensaje, listas para mandar a Meta |
| `docs/16-guias-workflows.md` | **Cómo se arma cada workflow**, en la UI y por la API interna: moldes de nodos, If y triggers, y lo que la cuenta acepta (§4) |
| `entregables/catalogo-menudeo-para-llenar.xlsx` | El Excel que se le mandó al cliente para capturar precio, piezas y stock de los 30 SKUs |
| `entregables/reporte-avance.html` | El reporte de avance que ve el cliente — mismo checklist que la propuesta |
| `entregables/mapa-paca.html` | El mapa de desarrollo en 3 hojas — **interno**, no se comparte con el cliente |
| `n8n/` | Los 5 flujos de n8n como JSON importable. Probados en vivo en Greentex: `N1`, `N2` y `N3`; `N4` y `N5` probados antes del cambio a la oportunidad, falta repetirlos. `N5` cambió el 2 oct (no repite avisos y cierra el pedido entregado), sin probar |
| `scripts/` | Herramientas internas. Leen credenciales del entorno, nunca de un archivo |
| `propuesta/propuesta-paca.html` | La propuesta que ve el cliente |
| `data/catalogo.csv` | 30 SKUs: 17 de verano, 13 de invierno |

---

## Decisiones cerradas — no las reabras sin razón nueva

1. **La venta vive en la conversación de WhatsApp; el cobro sale por liga de pago.**
   No por el checkout de la tienda. Ver `docs/07-decision-checkout.md`.
2. **El asistente es uno solo, en Conversation AI de GHL, con acciones Custom API.**
   Esas acciones le permiten consultar a n8n dentro del mismo turno (probado el 25 sep
   2026, límite de 10 s por llamada). Se eligió sobre Agent Studio el 25 de septiembre
   porque hace lo mismo con un prompt y tres acciones en vez de 19 nodos. Dos bots en
   el mismo WhatsApp se pelean el primer turno.
3. **n8n nunca habla con el cliente y nunca toca Stripe.** Valida y aparta stock, crea
   la factura en GHL por la API de Invoices y devuelve la liga al agente, busca
   sucursal por código postal, y genera guías y rastrea. Quien cobra es GHL con la
   pasarela que tenga conectada.
4. **El inventario vive en los productos de GHL**, con n8n como dueño único del
   contador.
5. **La pasarela es el Stripe del cliente** (entidad de EE.UU.), conectado por él en
   Greentex; la subcuenta va en **MXN**. Tarjeta está confirmado. OXXO y SPEI existen
   en Stripe para cuentas de EE.UU., pero **falta comprobar que el checkout de GHL los
   muestre** (validación 4). Si no, el plan B es tarjeta por la liga y transferencia
   manual con el formulario `AP03`. Mercado Pago quedó fuera el 25 de septiembre de
   2026 por decisión del cliente; sigue siendo pasarela nativa de GHL, por si vuelve.
6. **Los datos de cada pedido viven en la oportunidad, no en el contacto** (28 sep).
   Apartado, Pago y Guía son campos de oportunidad; Envío y Atribución se quedan en el
   contacto porque el bot de Conversation AI sólo escribe ahí. Ver `docs/01-mapa-ghl.md` §4.

> Dos afirmaciones de revisiones viejas eran **falsas** y están corregidas: que
> Mercado Pago no era nativo, y que GHL no llevaba inventario. Si las encuentras
> repetidas en algún lado, son un error que quedó suelto.

---

## Cómo se escribe aquí

Los documentos y la propuesta están en **español de México**, dirigidos a gente que no
es técnica. Se explica qué cambia para el negocio, no cómo funciona por dentro. Sin
adornos y sin vender de más: si algo está por validar, se dice que está por validar.
