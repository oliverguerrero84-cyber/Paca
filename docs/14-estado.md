# Estado del proyecto

> **Corte: 2 de octubre de 2026.** En qué va todo. Los demás documentos dicen qué
> se va a hacer y en qué orden; éste dice **qué está hecho y qué no**.
>
> Cuando algo se termine, se mueve de una tabla a otra aquí mismo. Si este documento
> contradice a `docs/11-cronograma.md` o a `docs/13-accesos.md`, ellos mandan en el
> plan y éste sólo en el avance.

---

## 0. Continuar desde aquí

> **Si te dicen «continuemos», esto es lo que sigue.** Se actualiza al cerrar cada sesión.

**Dónde quedó (2 oct):**
- Los 5 flujos de n8n están en el n8n de Germán.
  - Probados en vivo con los datos en la oportunidad: `N1` y `N2`.
  - `N3` probado. `N4` y `N5`, probados antes del cambio a la oportunidad.
  - **`N5` cambió el 2 oct**, sin probar todavía: avisa a `AP01` una sola vez por estado (guarda el último en `opportunity.estado_envio`, campo creado ese día) y, al entregarse, pasa la oportunidad a «Entregado» con status **won**. Antes avisaba cada hora y nunca cerraba el pedido.
- **Los 7 workflows de GHL están creados por API en Greentex** (`scripts/armar-workflows.py`), con **74 nodos**. El detalle está en `docs/16-guias-workflows.md` §4.9.
- ⚠️ **Los 10 workflows están PUBLICADOS, no en borrador** — verificado leyendo la cuenta el 2 oct. Es el efecto de rebote que avisa el playbook: **crear un trigger publica el workflow**, y el 2 oct se crearon seis. Ninguno se publicó a propósito.
  - **Hoy no hace daño**: hay 3 contactos de prueba y 1 oportunidad, no hay WhatsApp ni Stripe, y los nodos de mensaje son SMS sin número, así que fallan en ejecución sin mandar nada.
  - **Lo que sí importa**: `LS01` dispara con *Contact Created* **sin filtro**, así que en cuanto entren contactos de verdad —una importación, un formulario— a cada uno se le crea una oportunidad. Está bien por diseño (`N1` reutiliza la del lead y sólo contesta `pedido_en_curso` si hay **otra** que no sea de lead), pero conviene decidirlo, no heredarlo.
  - **Decisión pendiente:** o se regresan los 7 a borrador hasta que estén WhatsApp y Stripe, o se deja así a sabiendas. Regresar a borrador apaga sus triggers solo.
  - **Triggers puestos** (verificados por API el 2 oct): `LS01` *Contact Created*, `SP02` etapa → «Liga de Pago Enviada», `SP04` *Payment Received*, `SP05` etapa → «Pago Confirmado», `AP01` Inbound Webhook (URL ya en `N5`), `AP02` tag `escalar-humano`. Falta `AP03`: espera su formulario.
  - **`AP01` terminado** (2 oct, 11 nodos, revisado en la interfaz): *Find contact* por Contact ID → If por `estado`: `en_sucursal` → SMS; `incidencia` y `cancelado` → tag `escalar-humano`; lo demás, nada.
  - Los mensajes al cliente son nodos **«TEMPORAL · SMS»**, porque la cuenta todavía no acepta `whatsapp_v2`: no hay número conectado. Se cambian cuando haya WhatsApp y plantillas aprobadas (§4.8).
  - **`SP02` ya tiene sus If** (2 oct, 26 nodos), sobre `opportunity.estado_apartado`.
  - **`SP05` ya tiene su If** (2 oct, 12 nodos, revisado en la interfaz): si `opportunity.etiqueta_pdf` está vacía tras la espera, `N4` falló → tag `escalar-humano`; si no, correo, SMS y «Orden en Almacén».
  - ⚠️ No volver a correr `armar-workflows.py SP02`, `SP05` ni `AP01` con `--aplicar`: borraría las ramas. Las ramas se escribieron con `scripts/ramas-sp02.py`, `scripts/ramas-ap01.py` y `scripts/ramas-sp05.py`, que se corren una sola vez (verifican la forma de antes y guardan respaldo).
  - El nodo de `AP02` que apaga el bot lo rechaza la cuenta, porque Conversation AI todavía no está provisionado (§4.3).
- Hay un borrador suelto, «New Workflow : 1790282449589» (`f66b0701-…`), que parece una prueba. Se borra en la limpieza.

**Siguiente paso, en orden:**
0. ~~`SP04` y `AP03` sólo movían la etapa~~ — corregido el 2 oct en la interfaz:
   - Los dos tienen ahora **Find opportunity** (pipeline SP · Menudeo, etapa «Liga de Pago Enviada», status open, la más reciente). Sin él, la acción de oportunidad **no hacía nada**: el trigger de pago y el de formulario no traen oportunidad.
   - La acción escribe `estado_apartado = pagado` y `fecha_pago = {{right_now.little_endian_date}}`. `SP04` además `orden_id = {{payment.invoice.number}}`.
   - **Falta en `AP03`:** `orden_id`, que saldrá de la referencia del formulario cuando exista. Sin él, `N4` contesta `faltan_datos` en los pagos por transferencia.
   - **Pago que llega tarde** (el apartado ya venció y la oportunidad está `abandoned`): la rama *Not Found* de `SP04` y `AP03` manda un correo a los 3 dueños con el cliente y la factura, para que decidan si entregan o devuelven (`scripts/aviso-pago-sin-pedido.py`, 2 oct).
   - Se creó la etiqueta `apartado-vencido`: no existía, y el nodo de `SP04` que la quita salía con aviso de error.
1. **Germán, a mano en la interfaz:**
   1. ~~If de `SP05` y triggers~~ — hechos el 2 oct.
   2. El formulario «Registrar Pago Manual» y el trigger de `AP03`.
2. **Probar `N5` + `AP01` de punta a punta**: hace falta una oportunidad de prueba en «Enviado» con `numero_guia` de una guía real de Envia (sandbox). Correr `N5` a mano dos veces: la segunda **no** debe volver a avisar. Con una guía entregada, verificar por la API que la oportunidad quede **won**.
3. ~~Probar la rama de `N1` que crea la oportunidad~~ — **pasó el 2 oct**. Con «Prueba Paca» creó una oportunidad nueva (`u0LqSbCow6Kp6HMKAfKM`) en «Liga de Pago Enviada», `open`, con sus 8 campos y `monetaryValue` 100; dejó intacta la vieja (`abandoned`); el stock bajó de 3 a 2 y la factura 000006 salió `sent` en MXN.
   - **Efecto: `SP02` corriendo en vivo** sobre esa oportunidad (los workflows están publicados). Entró el 2 oct a las 12:39 p.m. (CDT) y está en «Espera 12 h»; la siguiente acción es el **3 oct a las 12:39 a.m.** Revisar en *Enrollment history* / *Execution logs* de `SP02`: el If de las 12 h debe ir por «No» (sigue `apartado`), el SMS falla porque el contacto no tiene teléfono, y a las 24 h 20 min (3 oct ~12:59 p.m. CDT) el If de «¿Venció?» va por «No» porque `N2` está apagado. Para probar la rama de vencido, `N2` tiene que estar prendido entre las 12:39 p.m. (vence) y las 12:59 p.m. del 3 oct, y después devolver la pieza a `test 1` lo hace él solo.
   - Los 5 flujos de n8n están **apagados**. Para probar, se prende el flujo, se llama y se apaga; prenderlo lo corre Germán con `!` (el clasificador lo bloquea). Script de esta prueba: prende `N1`, llama `/webhook/apartar` y lo apaga con un `trap`.
4. **`SP02`:** crear el campo de oportunidad `expira_texto` y que `N1` lo escriba (`docs/16-guias-workflows.md` §1.4). Después, una copia de prueba con waits de minutos y sus dos corridas: el que paga y el que no.
5. **`SP04`:** probar si «registrar pago» manual sobre una factura de prueba dispara el pago recibido.
6. **Repetir `N4` y `N5`** con los datos en la oportunidad.

**Cómo se trabaja con Germán:**
- Los workflows se arman **por API** con `scripts/armar-workflows.py`. Lo que la API no puede (moldes que faltan, formularios) lo hace Germán en la interfaz, y después se lee por API.
- **Escribir un workflow vivo lo corre Germán** con `!` en el prompt: el clasificador de Claude Code bloquea esa escritura. Leer sí lo hace Claude.
- El canje del token de Firebase da **429** si se repite en menos de un minuto: es un límite de Google, se espera y se reintenta.
- Antes de escribir un workflow, leer `docs/16-guias-workflows.md` §4.2: hay que releerlo antes de cada PUT, el PUT es todo o nada y crear un trigger lo publica.
- La API interna pide el token de la extensión de Chrome **canjeado por un JWT**, que dura una hora (§4.1).
- Los flujos de n8n se cambian en el repo y se suben con `scripts/subir-n8n.py`, sin reimportar.

**Accesos para trabajar desde Claude Code** (nunca por chat, nunca en el repo):
- **API de Greentex:** `GHL_API_KEY` (el PIT de Greentex) y `GHL_LOCATION_ID`. En la máquina de Germán viven en `C:\Users\germa\gohighlevel-cli\.env.greentex`.
- **API de n8n:** `N8N_API_URL` y `N8N_API_KEY`. En la máquina de Germán viven en `C:\Users\germa\.n8n-korvance.env`. Es la key de *Settings → n8n API*, no el token del MCP.
- **En otra máquina:** pedírselos a Germán por un gestor de contraseñas y cargarlos como variables de entorno.

**Decisiones pendientes de Germán:**
- **Borrar los 14 campos viejos del contacto** (`contact.articulo_apartado`, `contact.estado_apartado`, `contact.expira_en`…), duplicados de los de la oportunidad desde el cambio del 28 sep. Nadie los escribe y están vacíos, pero en el selector de la UI se llaman igual que los buenos: escoger uno deja el mensaje vacío o el If siempre en falso, **sin error**. Es la trampa de `docs/16-guias-workflows.md` §1.2.
- **10 flujos de n8n archivados pero activos**, de otros proyectos, sin borrar. La mayoría son subflujos; «Servir Páginas de Propiedades» tiene un webhook que podría estar en uso. Los otros 57 archivados ya se borraron.

**Datos de prueba en Greentex hoy:**
- Contacto «Prueba Paca» (`1IzcksRfvxpnEohAZSg5`) con dos oportunidades en «Liga de Pago Enviada»: la vieja (`ZMTFf0hvLxNkwQJn6tRw`), `abandoned` y `vencido`; y la del 2 oct (`u0LqSbCow6Kp6HMKAfKM`), **`open` y `apartado`, expira el 3 oct 17:39 UTC**. Con `N2` apagado no se libera sola: sirve para probar `SP04` y `SP02`, y si no, se cierra en la limpieza devolviendo la pieza.
- Producto `test 1` (SKU `PV-MUJ-BOU`) con **stock 2** (una pieza apartada por la oportunidad del 2 oct; otra la descontó una corrida fallida de `N1` y no se devolvió).
- 6 facturas de prueba de $100 (000001 a 000006; la 000006 es la del apartado abierto).
- Los workflows «PRUEBA N1», «PRUEBA N3» y «PRUEBA N5», y el borrador «New Workflow : 1790282449589».
- Todo esto se limpia al final (ver §3).

## 1. Dónde estamos, en una línea

**El cliente aceptó y pagó el Completo, su subcuenta existe —Greentex Clothing LLC— y
ya tiene el esqueleto de GHL de pie**: pipeline, campos y custom values. Falta el
motor —n8n, workflows y el agente— y los datos que el cliente todavía no manda. **El 25
de sep cambió la pasarela: se cobra con el Stripe del cliente, no con Mercado Pago**, y
la primera pieza que hace falta es que él lo conecte en Greentex. Mientras, el 25 de sep se probaron
las dos piezas del cobro que no dependen de él: la factura por API ya se crea y su liga abre
el checkout, y el asistente ya llama a la API a mitad de turno y manda la liga. **El 28 de sep
`N1` corrió de punta a punta en Greentex**: aparta, descuenta stock y crea y envía la factura.
Ese mismo día **los datos del pedido pasaron del contacto a la oportunidad** (un cliente puede
hacer varios pedidos), y `N1` y `N2` ya se probaron en vivo así: `N1` escribe el apartado en la
oportunidad y `N2` libera el vencido y la cierra como `abandoned`. `N3` también quedó probado.

## 2. Hecho

**Cómo se lee la columna «Quién».** **Germán** es lo que hizo él —en la cuenta de GHL,
en su instancia de n8n y contra las APIs de Stripe, Mercado Pago y Envia—. **Claude /
786** es lo que salió de las sesiones de Claude Code: documentos, scripts, la propuesta
y los flujos escritos. **786** a secas es trabajo a mano de la agencia, y **Cliente** es
lo que él decidió o mandó. Si hay duda, el `git log` del repo tiene el autor y la fecha
de cada cosa.

| Qué | Quién | Cuándo |
|---|---|---|
| Alcance, arquitectura y las decisiones de diseño | Claude / 786 | 14 – 19 sep |
| **Propuesta cerrada, aceptada y cobrada** — Completo, USD 4,497 + 637 al mes | Claude / 786 | 18 – 22 sep |
| Paquete de traspaso para trabajar el repo desde otra cuenta | Claude / 786 | 19 sep |
| **Excel del catálogo mandado al cliente** para que capture precio, piezas y stock | Claude / 786 | 22 sep |
| Mensaje de arranque al cliente con todo lo que hay que pedirle | Claude / 786 | 22 sep |
| **Los 23 campos del formulario de alta**, en la carpeta «Alta de subcuenta» | Claude / 786 | 23 sep |
| Cronograma de las 4 semanas al go-live | Germán | 23 sep |
| **La cadena de altas y accesos**, ordenada por dependencias | Germán | 23 sep |
| Mapa de desarrollo en una página para el equipo | Germán | 23 sep |
| Condiciones de pago corregidas en la propuesta | Claude / 786 | 23 sep |
| **Subcuenta del cliente creada** — Greentex Clothing LLC, y es donde se trabaja de aquí en adelante | Germán | 24 sep |
| **Esqueleto de GHL levantado** en Greentex: pipeline `SP · Menudeo` de 8 etapas, **25** campos custom en 4 carpetas y los 8 custom values | Claude / 786 | 24 sep |
| **Los 3 usuarios del cliente**, dados de alta a mano | 786 | 24 sep |
| **Las 6 plantillas de mensaje redactadas** (`A5`), listas para mandar a Meta | Claude / 786 | 24 sep |
| **Los 5 flujos de n8n escritos** como JSON importable — **sin probar**, no hay instancia donde correrlos | Claude / 786 | 24 sep |
| Validación 1 con Mercado Pago **cerrada sin resultado**: la cuenta argentina de 786 tiene las llaves revocadas. Queda anotado en `docs/13-accesos.md` §4 por si vuelve | Germán | 24 – 25 sep |
| **Ensayo del asistente con Custom API de Conversation AI**: con un endpoint falso, el bot recogió los datos, llamó una vez y mandó la liga. Mecanismo probado sin n8n | Germán | 25 sep |
| **Ensayo de la factura por API en Korvance**: 201, queda enviada con Stripe, liga `{dominio}/invoice/{id}` confirmada. `N1` corregido con lo que la API exige | Germán | 25 sep |
| **Primera prueba de `N1` en el n8n de Germán**: llegó hasta «¿Alcanza?» y contestó agotado con stock de 3, porque `GET /products/` no trae precios. Corregido: `N1` y `N2` leen `/products/inventory` | Germán | 25 sep |
| **Los 5 flujos sin `$env`**: la instancia lo bloquea, así que cada flujo trae un nodo `Config` con sus valores. Sin tocar Portainer | Germán | 25 sep |
| **4 URLs de n8n en los custom values de Greentex**, en modo prueba (`webhook-test`) | Germán | 25 sep |
| **`N5` con webhook `rastrear`** para la acción del bot; antes sólo tenía cron | Germán | 25 sep |
| **PIT de Greentex creado (`0.2d`) y los 5 campos nuevos en la subcuenta**: `invoice_id`, `servicio_envio`, `branch_code`, `etiqueta_pdf`, `track_url`; `mp_preference_id` borrado. 25 campos en total | Germán | 25 sep |
| **Los 5 flujos importados en el n8n de Germán** (`0.3` a medias: faltan variables, credenciales y las URLs en los custom values) | Germán | 25 sep |
| **Envia probado en su sandbox**: cotización, guía a domicilio y a sucursal, y rastreo. `N3`, `N4` y `N5` corregidos con la API real; supuestos 3 a 6 de n8n cerrados | Germán | 25 sep |
| **El asistente vive en Conversation AI**, con acciones Custom API, en vez de Agent Studio. Decidido tras el ensayo del mismo día | Germán | 25 sep |
| **Greentex en MXN** (`0.2c`) | Germán | 25 sep |
| **`N1` probado de punta a punta en Greentex**, disparado por un Webhook de un workflow de GHL: encuentra el SKU, descuenta stock, crea y envía la factura. Salieron tres cosas: el `N1` de la instancia era una versión vieja (se reimportó), el Webhook de GHL manda los datos en `customData` y `contact_id` (`N1` ya acepta las dos formas), y `/send` da 422 con `autoPayment: false` (quitado) | Germán | 28 sep |
| **Validación 3 cerrada**: `N1` completo tarda **4 s**, dentro del límite de 10 s de la acción Custom API | Germán | 28 sep |
| **Liga de pago dada por buena**: en Greentex abre la factura en MXN con los datos del negocio; el botón de pago con Stripe ya se vio funcionar en Korvance, así que en Greentex aparece al conectar Stripe | Germán | 28 sep |
| **`N3` probado desde un Webhook de GHL en Greentex**: CP 20126 → Aguascalientes y las 3 sucursales de Paquete Express más cercanas, con `branch_code` y distancia | Germán | 28 sep |
| **`N4` probado desde un Webhook de GHL en Greentex**, contra el sandbox de Envia: genera la guía a sucursal y la etiqueta en PDF. Con un almacén de prueba en `Config`, porque el real sigue en `PENDIENTE`. La liga de rastreo del sandbox (`test.envia.com`) no abre; en producción Envia la devuelve en `envia.com` | Germán | 28 sep |
| **`N5` por webhook probado**: responde el estatus de la guía del contacto | Germán | 28 sep |
| **`N2` y el reloj de `N5` corregidos, sin probar en vivo**: buscaban los campos en la oportunidad, pero viven en el contacto, y `GET /contacts/{id}` los devuelve sin clave, sólo con id. Así `N2` nunca habría liberado un apartado vencido, sin dar error. Ahora leen el contacto de cada oportunidad y traducen clave → id; `N2` además marcaba vencido a un contacto vacío | Claude / 786 | 28 sep |
| **`N2` probado en vivo**: liberó la paca vencida y la devolvió al stock | Germán | 28 sep |
| **Los datos del pedido pasan a la oportunidad** (decisión de Germán: un contacto puede tener varios pedidos). Apartado, Pago y Guía son campos de oportunidad; Envío y Atribución se quedan en el contacto porque el bot sólo escribe ahí. `N1` escribe el apartado en la oportunidad del lead (o crea una) y la pasa a «Liga de Pago Enviada»; `N2` revisa las etapas 3 y 4 y deja el vencido en `abandoned`; `N4` guarda la guía en la oportunidad; `N5` rastrea desde ella. **En el repo y probado con datos simulados; falta crear los campos y probar en vivo** | Claude / 786 | 28 sep |
| **Campos de oportunidad creados en Greentex** (14, carpetas Apartado, Pago y Guía) con el script. **Sin la opción de duplicados** (no se encontró en Greentex), GHL deja una sola oportunidad abierta por contacto: `N1` ahora lo revisa antes de tocar stock y contesta `pedido_en_curso` si ya hay otro pedido abierto | Claude / 786 | 28 sep |
| **Varias oportunidades por contacto activadas en Greentex** (*Settings → Objects → Opportunities → «Allow multiple opportunities per contact»*), verificado por la API (`allowDuplicateOpportunity: true`). Cada pedido queda en su oportunidad; se descartó el cambio de `N1` que reabría la existente | Germán | 29 sep |
| **`N1` nuevo probado en vivo**: reutilizó la oportunidad del lead, la pasó a «Liga de Pago Enviada» y le escribió los 8 campos del apartado (`expira_en` en ISO). GHL devuelve los valores de oportunidad como `fieldValueString` / `fieldValueNumber` | Germán | 28 sep |
| **`N2` nuevo probado en vivo**: encontró el apartado vencido en la etapa 4 leyendo los campos de la oportunidad, devolvió la paca (stock 3 → 4), puso `estado_apartado = vencido` y dejó la oportunidad en `abandoned` | Germán | 28 sep |
| **Los 7 workflows de GHL creados por API** en borrador, con nodos «TEMPORAL · SMS» donde irá WhatsApp. Probado que la API interna crea workflows, nodos y triggers (`scripts/armar-workflows.py`, `docs/16-guias-workflows.md` §4) | Oliver | 1 oct |
| **Triggers de `LS01`, `SP02`, `SP04` y `SP05`** puestos en la UI y verificados por API | Germán | 2 oct |
| **If sobre campos de oportunidad**: moldes leídos de la UI (`find_opportunity` + `conditionType: opportunities`, «está vacío» = `has_no_value`). `SP02` (26 nodos) y `SP05` (12) con sus ramas, escritas por API | Germán / Claude | 2 oct |
| **`AP01` terminado**: Inbound Webhook (URL en `N5`), *Find contact* por Contact ID y ramas por `estado` (sucursal → SMS; incidencia o cancelado → `escalar-humano`) | Germán / Claude | 2 oct |
| **`N5` corregido**: avisaba a `AP01` cada hora y nunca cerraba el pedido entregado. Ahora guarda el último estado en `opportunity.estado_envio` (campo nuevo) y pasa el entregado a «Entregado» con status `won`. Subido a n8n, **sin probar** | Claude / 786 | 2 oct |
| **Cambio de pasarela a Stripe**, por decisión del cliente. La liga la crea `N1` con la API de Invoices y se la devuelve al agente; `SP03` desaparece; la subcuenta va en MXN | Cliente / Germán | 25 sep |

> Los 23 campos del formulario de alta viven en **Korvance, la cuenta de trabajo de
> Germán**, y ahí se quedan: son el formulario con el que se le piden los datos al
> cliente, y ya cumplieron. **No se copian a Greentex.** El script sirve para el
> siguiente cliente.

## 3. Lo siguiente, y nada de esto espera a nadie

Lo de hoy primero; después, los eslabones raíz de `docs/13-accesos.md` §2.

| # | Qué | Quién |
|---|---|---|
| `0.1` | **Rotar el PIT de Korvance.** Volvió a pasar por chat el 25 sep | 786 |
| — | **Terminar las pruebas con la oportunidad**: la rama de `N1` que **crea** la oportunidad (el contacto de prueba ya no tiene una abierta), `N4` con `opportunityId` en el Custom Data, y `N5` por webhook y por reloj | Germán y Claude |
| — | **Borrar los 14 campos viejos del contacto** (Apartado, Pago y los 4 de la guía) una vez probado lo nuevo, para que nadie los llene por error | Germán, tras la prueba |
| — | Prompt del bot: qué decir cuando `N1` contesta `pedido_en_curso` (terminar o cancelar el pedido actual antes de apartar otro) | 786 |
| — | **`AP03`: `orden_id` desde el formulario** (cuando exista) | Germán / Claude |
| `0.3` | `N1`, `N2` y `N3` reimportados y probados. Falta **reimportar `N4` y `N5`** con la versión de la oportunidad y asignarles credenciales | Germán |
| — | **OXXO y SPEI en el checkout** (resto de la validación 4): se mira el día que el cliente conecte Stripe (`B1`) | Germán, tras `B1` |
| — | **Limpiar lo de la prueba en Greentex**: los workflows `PRUEBA N1 - webhook apartar` y el de N3 (quedó como «New Workflow : 1790609975341»), las facturas de prueba, la oportunidad «Prueba Paca» y el producto `test 1` (SKU `PV-MUJ-BOU`, marcado como Digital) | 786 |
| `A3` | Confirmar que **+1 (956) 820-2011 recibe SMS o llamada**. Si es VoIP, el alta en Meta puede fallar y hay que conseguir otro número | 786 |
| — | **Agendar la sesión de mapeo** con el cliente, y en ella pedirle que conecte su Stripe en Greentex (`B1`) | 786 |
| — | El **logo de 786**: la propuesta todavía lleva el wordmark provisional en CSS | 786 |

## 4. Bloqueado, y por quién

### Espera al cliente

| Qué | Bloquea |
|---|---|
| **Precios de venta por SKU** | Sin esto el bot no cotiza ni genera liga. Es lo que más falta |
| **Fotos y videos** de los 30 artículos | El catálogo que el agente manda por WhatsApp |
| **Descripciones** — faltan 6 de 30 | El agente no puede describir lo que no sabe |
| **Piezas por paca** | De lo que más preguntan los compradores |
| **Stock inicial** al menudeo | La carga de `availableQuantity` |
| **Verificar el Meta Business Manager** y agregar a 786 como socio | `A1` y `A2`, el primer eslabón del carril más largo |
| **Conectar su Stripe en Greentex** (`B1`), y activar OXXO y transferencia MX en su dashboard (`B2`) | Las validaciones 1, 2 y 4. Es lo único que hoy detiene el carril del cobro |
| **Cuenta de Envia.com con saldo** | Las guías |

Los primeros cinco se piden con el Excel que ya se les mandó.

### Espera a que exista algo nuestro

| Qué | Espera a |
|---|---|
| **2 de los 7 custom values siguen en `PENDIENTE`**: el WhatsApp del almacén y el correo de los dueños. Las 4 URLs ya apuntan al n8n de Germán, en modo prueba (`webhook-test`); al activar los flujos se quitan el `-test` | A que las mande el cliente |
| Mandar las 4 plantillas a Meta (`A6`) — **ya redactadas** en `docs/15-plantillas.md` | La WhatsApp Business Account (`A4`) |
| **Validaciones 1, 2 y 4** | Que el cliente conecte Stripe (`B1`). La 4 además pregunta si el checkout de GHL muestra OXXO y SPEI; si no, el plan es tarjeta más transferencia manual con `AP03` |
| **La liga de pago del cliente** e incrustarla en la propuesta | Nada: es tarea viva de Germán |

## 5. Sin dueño todavía

De los cinco huecos de `docs/13-accesos.md` §8, **tres ya se cerraron**: Korvance es la
cuenta de trabajo de Germán, n8n corre en la instancia de Germán, prestada, y Envia ya
tiene sandbox probado. Quedan dos:

| # | Hueco | Bloquea |
|---|---|---|
| 4 | Roles y permisos de Pamela, Miguel y Mauricio dentro de la subcuenta | La capacitación de la última semana |
| 5 | Quién activa OXXO y transferencia MX en el Stripe del cliente: él, o 786 con acceso | `B2`, y con él la validación 4 |

## 6. Riesgos vivos

- **La aprobación de las plantillas por Meta es el único plazo que no controlamos.**
  Tarda de 24 a 48 horas y puede rechazar. Si se atrasa, se lleva el go-live con ella.
- **Si la validación 1 falla**, entra el plan B: cobrar por el checkout de la tienda y
  renunciar al apartado de 24 h. Conviene saberlo antes de prometérselo al cliente.
- **La propuesta prometió tarjeta, OXXO y SPEI en una liga.** Con Stripe en GHL sólo
  tarjeta está confirmado; los otros dos dependen de la validación 4. Si no salen, hay
  que avisarle al cliente esa misma semana.
- **El PIT sigue sin rotar.** Es lo primero de la lista de arriba.
