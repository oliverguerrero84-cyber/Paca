# Contexto completo del proyecto Paca

> **Para qué sirve este documento.** Es el proyecto entero en una sola lectura, del
> 14 al 22 de septiembre de 2026. Se lee solo: no hace falta abrir los demás
> documentos para entender qué se está construyendo, por qué, y en qué estado está.
> Los otros documentos son el detalle de cada pieza; éste es el mapa.
>
> Si vas a trabajar en el repo, salta al **§10 — Trabajar desde tu computadora**.

---

## 1. El negocio

Venden **pacas de ropa americana**: fardos cerrados de **100 lb / 45 kg**, 30
artículos distintos. Los dueños son **Pamela, Miguel y Mauricio Hernández**.

- Están en **McAllen, Texas**. El almacén que despacha está en **Nuevo Laredo,
  Tamaulipas** y distribuye a toda la República Mexicana.
- La mercancía **ya está importada y liberada** en México. No pasa aduana dentro del
  flujo de venta, así que eso no toca al sistema.
- Hoy hacen **sólo mayoreo**, y lo hacen a mano.
- No tienen redes: apagaron Facebook y borraron Instagram y TikTok. Hoy los leads
  sólo pueden llegar por WhatsApp.

Se vende la **paca completa, de una en una**. No se venden piezas sueltas — eso
obligaría a llevar inventario por prenda, talla y foto, y sería otro proyecto.

---

## 2. El problema que vienen a resolver

El menudeo lo tuvieron encendido y **lo apagaron**. No por falta de demanda: les iba
bien. Lo apagaron por desorden operativo.

> *"Llegamos a un punto en el que, pues también era como mucho, era mucho desorden,
> en el sentido de que cuando eran las direcciones y no había control."*

Cuatro cosas los desbordaron:

1. **Desorden y falta de control.** Direcciones y seguimiento a mano, sin registro.
2. **Pedidos que nunca cerraban.** El "te pago al rato" que se volvía nunca.
3. **Riesgo de sobrevender.** Textual de ellos: *"tengo tantas de esta y no tengo
   más."* Es la preocupación central del proyecto.
4. **Todo dependía de personas.** Cuatro vendedoras contestando mensajes uno por uno,
   y aun así no se daban abasto.

Sobre las direcciones, Miguel lo explicó así:

> *"En México la gente tiene unas direcciones un poco extrañas, de pronto nos decían
> 'no, yo estoy en el kilómetro 3 pasando el rancho Fulanito', o sea, no lo puedes
> decir así a la paquetería, entonces era un show."*

Por eso históricamente manejan **únicamente Paquete Express** y **sólo servicio a
ocurre** — el cliente recoge en sucursal. Eso simplifica mucho el alcance: no hay que
validar domicilios, sólo saber en qué sucursal recoge.

**El mayoreo queda fuera y sigue manual.** Es explícito y no se negocia:

> *"Mi mayoreo yo lo trabajo aparte. Lo que yo no se entromete con mi menudeo."*

---

## 3. Qué compraron

El paquete **Completo**, pagado y arrancando.

| | |
|---|---|
| Implementación | **USD 4,497** — pago completo, una sola exhibición |
| Mensualidad | **USD 637**, con **un mes de gracia después de entregado** |
| Entrega | 3 a 4 semanas desde la sesión de mapeo |

> ⚠️ **La propuesta HTML todavía dice "dos pagos" y "anticipo del 50 %".** Las
> condiciones cambiaron después de cerrarla. Hay que corregir esas tres líneas antes
> de incrustar la liga de pago — está detallado en `docs/08-traspaso.md` §2.

**Qué cubre la mensualidad:** soporte, el agente de IA activo, monitoreo, ajustes al
bot conforme se aprende qué pregunta la gente, los cambios de catálogo entre
temporadas, el reloj del apartado y la conexión con la paquetería.

**Qué paga el cliente aparte, directo al proveedor:** la conexión de WhatsApp con
Meta y su cobro por conversación, los correos, los mensajes automáticos del pedido,
la comisión de Mercado Pago, las guías de paquetería y la licencia de Google
Workspace. Y las fotos y videos de producto, que los produce él.

**No se construye flujo de devoluciones**, porque su política es que no hay:

> *"Tratamos que la venta sea sincera y directa: es esto y trae esto y no hay
> devolución."*

El bot lo dice **antes** de mandar a pagar, nunca después de cobrar.

> Los números internos —piso de negociación, holgura y reparto con 786— están en
> `docs/04-precotizacion.md` y **no salen nunca al documento del cliente**.

---

## 4. Cómo funciona el sistema, de punta a punta

La idea de fondo: **la venta vive en la conversación de WhatsApp.** El cliente sale
de ahí una sola vez, para pagar, y regresa solo.

```
 1. Llega un mensaje por WhatsApp
 2. El agente atiende: calidades, tallas, qué trae, peso, fotos y videos
 3. Detecta intención de compra → captura artículo y cantidad
 4. Pregunta a n8n si hay existencia                    ── n8n
 5. Pide el CÓDIGO POSTAL, 5 dígitos
 6. n8n devuelve 2 o 3 sucursales cercanas              ── n8n + Envia
 7. El cliente elige de la lista
 8. n8n APARTA: descuenta 1 y arranca el reloj de 24 h  ── n8n
 9. GHL crea la liga de pago                            ── GHL + Mercado Pago
10. El cliente paga: tarjeta, OXXO en efectivo o SPEI
11. Pago acreditado → se confirma la venta sola
12. n8n genera la guía y programa la recolección        ── n8n + Envia
13. Al almacén le llega la etiqueta lista para imprimir
14. n8n rastrea → "ya llegó a tu sucursal"              ── n8n + Envia
```

### El apartado, como un boleto de concierto

Lo pidieron así: eliges, se abre un reloj, y si no pagas se libera para el siguiente.
**24 horas.** Con recordatorios automáticos antes de vencer y liberación sola si no
paga.

**Choque conocido con el efectivo:** OXXO acredita en hasta **72 horas hábiles**, más
que el apartado. Cuando el cliente elige efectivo, el apartado se extiende hasta que
venza la referencia de Mercado Pago.

### Regla dura: el almacén nunca ve dinero

Miguel fue explícito: *"ellos no tienen por qué enterarse."* El aviso al almacén
lleva **sólo** nombre, cantidad, destino y código postal. Nunca el monto. Es una
regla de diseño, no una preferencia.

---

## 5. Quién hace qué

| Pieza | Responsabilidad |
|---|---|
| **Agent Studio de GHL** | Toda la conversación. Es el único que le habla al cliente |
| **Workflows de GHL** | El tablero, el apartado, crear la liga de pago, avisar al almacén |
| **Mercado Pago** | Cobra. Es pasarela **nativa** de HighLevel |
| **n8n** | Valida y aparta stock · busca sucursal por código postal · genera guías y rastrea |
| **Envia.com** | Guías de Paquete Express, recolección y rastreo |

**n8n nunca habla con el cliente y nunca toca Mercado Pago.** Es un servicio que el
agente consulta, no un participante de la conversación.

### Dónde vive cada dato

| Dato | Dónde | Quién lo escribe |
|---|---|---|
| Los 30 artículos y sus precios | Productos de GHL | Se carga una vez; los dueños editan |
| **Stock disponible** | `availableQuantity` del producto en GHL | Los dueños al reponer; **n8n** al apartar y liberar |
| Apartados vigentes | Oportunidades del pipeline + campos custom | Los workflows |
| Pagos | Mercado Pago, dentro de GHL | Mercado Pago |
| Guías y rastreo | Envia.com, reflejado en campos custom | n8n |

**No hay Google Sheet.** El cliente ve y edita su stock en la misma pantalla donde ve
sus ventas: una herramienta menos que aprender y una fuente de verdad menos que
sincronizar. `availableQuantity` es sólo la porción asignada a menudeo; cuando muevan
pacas entre mayoreo y menudeo, ajustan la cantidad en el producto.

---

## 6. Qué hay que construir

Nada de esto está hecho todavía. **No se ha tocado la cuenta de GoHighLevel.**

**Pipeline `SP · Menudeo`, 8 etapas:** Lead Nuevo → En Conversación (Bot) → Pedido
Apartado (24 h) → Liga de Pago Enviada → Pago Confirmado → Orden en Almacén →
Enviado, Guía Generada → Entregado.

**9 workflows:**

| Código | Qué hace | Nodos |
|---|---|---:|
| `LS01` | Entrada de lead de menudeo | 10 |
| `SP01` | Handoff al agente + control del bot on/off | 8 |
| `SP02` | Apartado de 24 h, recordatorios y liberación | 16 |
| `SP03` | **Crea la liga de pago** por la API de Invoices | 12 |
| `SP04` | Pago confirmado → número de orden (Goal Event `Payment Received`) | 10 |
| `SP05` | Despacho: guía de Envia + PDF al almacén + correo a los dueños | 12 |
| `AP01` | Rastreo hasta "llegó a tu sucursal" | 10 |
| `AP02` | Escalamiento a un humano | 8 |
| `AP03` | Registro manual de pagos por transferencia | 7 |

**Agente de Agent Studio, 19 nodos.** Saluda y califica (menudeo o mayoreo), resuelve
dudas contra la Knowledge Base, captura temporada, categoría y calidad, **manda foto
y video**, consulta stock a n8n, pide el código postal, ofrece las sucursales, y
cierra dejando el pedido armado con el aviso de que no hay devoluciones.

**5 flujos de n8n:** `N1` apartar (serializado, concurrencia 1) · `N2` liberar
vencidos (cron cada 15 min) · `N3` buscar sucursal · `N4` generar guía · `N5`
rastrear.

**6 plantillas de mensaje**, 4 de ellas con trámite de aprobación ante Meta.

---

## 7. Decisiones cerradas — y por qué

No las reabras sin una razón nueva. Cada una costó investigación.

**La venta vive en la conversación; el cobro sale por liga, no por la tienda.**
Mandar a un carrito es fricción para un público que —según Mauricio— *"no sabe
escribir bien, no sabe usar muy bien el teléfono"*. Además el carrito abandonado
nativo manda **una sola** notificación y exige que el cliente haya escrito su correo,
así que no sirve para la cadencia del apartado. → `docs/07-decision-checkout.md`

**Un solo asistente, en Agent Studio.** Su nodo `API Call` le permite preguntarle a
n8n *dentro del mismo turno*: el cliente pregunta si hay existencia y le contestan al
momento. Conversation AI clásico no tiene ese nodo e iría por webhook asíncrono. Y
dos bots en el mismo WhatsApp se pelean el primer turno.

**El inventario vive en los productos de GHL, con n8n como dueño único del
contador.** Como el cobro no pasa por el checkout de la tienda, GHL nunca descuenta
por su cuenta. Eso eliminó dos errores de diseño: el doble descuento, y uno peor —
que quien apartaba la última paca no podía pagarla, porque la tienda ya se la
mostraba agotada.

**El buscador de sucursal es consulta a tabla, nunca IA.** Envia `validate-zip-code`
+ `carrier-branches`, y se le devuelven 2 o 3 opciones para que elija. Un modelo
inventando sucursales es una guía perdida. → `docs/06-logistica-envia.md`

**La paquetería y el envío ya están cerrados.** Paquete Express a ocurre, vía
Envia.com, y **el envío va incluido en el precio**, igual a toda la República:
*"yo pongo una paca de seis mil trescientos pesos, es a cualquier parte, ya incluido
el envío."* Paquete Express llega a unas 146 sucursales en ciudades principales, y
esa limitación **les sirve de filtro**: quien no tenga sucursal cerca se descalifica
solo, y para ellos eso es ventaja.

### Dos afirmaciones de revisiones viejas eran falsas

Están corregidas, pero si te las encuentras repetidas en algún lado, es un resto que
se escapó:

- **Mercado Pago sí es pasarela nativa de HighLevel**, desde el 27 de abril de 2026,
  con México entre los países soportados. Cubre tarjeta, OXXO y SPEI.
- **GHL sí lleva inventario** en sus productos, con `availableQuantity`.

### Lo que se retiró del alcance

Reportes y dashboards, post-venta con reseñas y recompra, el workflow de campañas de
Meta y TikTok, el segundo pipeline, la venta de piezas sueltas, la facturación CFDI y
la pauta publicitaria. Si los quieren, se cotizan aparte.

**No quieren reseñas de Google**, por el hate de la competencia.

---

## 8. Lo que falta

### Del cliente — mueve la fecha de arranque, no el precio

| Falta | Bloquea |
|---|---|
| **Precios de venta por SKU** | Sin esto el bot no cotiza ni genera liga. Es el dato que más falta |
| **Fotos y videos** de los 30 artículos | El catálogo del bot. Miguel: *"quieren ver un video a través del WhatsApp"* |
| **Descripciones** — faltan 6 de 30 | El agente no puede describir lo que no sabe |
| **Piezas por paca** | De lo que más preguntan los compradores |
| **Stock inicial** al menudeo | La carga inicial de `availableQuantity` |
| **Número de WhatsApp** para el bot | Conviene uno nuevo: el que se conecte deja de funcionar en la app normal |
| **Mercado Pago verificado** | Sin verificación de identidad y fiscal, retiene fondos |
| **Cuenta de Envia.com** con saldo | Prepago, sin mensualidad ni comisión |

Los seis sin descripción: `CORSE VERANO BOUTIQUE`, `CORSE VERANO PREMIUM`,
`PLAYERA COMERCIAL`, `CHAMARRA BOUTIQUE`, `CHAMARRA PREMIUM` y `SUÉTER NAVIDEÑO`.

Ya se les mandó `entregables/catalogo-menudeo-para-llenar.xlsx` con los 30 artículos
cargados, para que capturen precio, piezas y stock en un solo archivo.

### De nosotros

El **logo de 786 Marketing**. La propuesta lleva un wordmark provisional hecho en
CSS; la clase `.logo-img` ya está lista para cambiarlo.

### Por validar en cuenta antes de prometerlo

Regla del toolkit: *"se guardó" no es "funciona"*.

| # | Qué probar | Por qué importa |
|---|---|---|
| 1 | Que la API de Invoices / Payment Links **cobre con Mercado Pago** | Sostiene todo el diseño |
| 2 | Que **pagar una liga no descuente stock solo** | Si lo hiciera, vuelve el doble descuento |
| 3 | Que el nodo **`API Call` responda a tiempo** | Si tarda, la conversación se siente trabada |

**Plan B si falla la 1:** cobrar por el checkout de la tienda y renunciar al apartado
de 24 h, porque ahí sí chocan.

### Riesgos vivos

Templates de Meta sin aprobar al go-live (redactarlos y mandarlos en la semana 1) ·
dos clientes apartando la última paca a la vez (`N1` serializado lo resuelve) ·
Mercado Pago sin verificar reteniendo fondos.

---

## 9. Gotchas del toolkit de GHL — leer antes de construir

Salen del CLI que ya usamos en otros proyectos. Ahorran días:

- **Los workflows se pueden construir por API**, pero los **bots de Conversation AI
  son sólo de interfaz**: no hay API para crearlos.
- **Un bot no puede escribir en campos de lista desplegable** (`SINGLE_OPTIONS`). La
  solución es un campo de texto gemelo más un workflow que normaliza.
- **El texto de una acción tiene tope de 500 caracteres.**
- **Un Transfer Bot con condición agresiva se roba el primer turno** y las capturas
  nunca se ejecutan.
- **Subir un documento a la Knowledge Base no es asociarlo** al agente. Son dos pasos.
- Y la regla de oro: **GHL guarda y muestra nodos mal formados que después no
  ejecutan, sin dar ningún error.** Por eso nada se da por bueno hasta verlo correr.

---

## 10. Trabajar desde tu computadora

El repo es **sólo texto**: documentos en markdown, un HTML de una sola pieza y unos
CSV. **No hay build, no hay `package.json`, no hay dependencias que instalar** para
leerlo o editarlo. Pesa 364 KB.

### Clonarlo

```bash
git clone https://github.com/oliverguerrero84-cyber/Paca.git
cd Paca
git checkout claude/cool-dirac-4sht9y
```

Necesitas que Oliver te agregue como colaborador antes (Settings → Collaborators).

**Se trabaja y se empuja a `claude/cool-dirac-4sht9y`.** Nunca a otra rama sin
permiso.

### Abrir Claude Code ahí

```bash
npm install -g @anthropic-ai/claude-code
cd Paca
claude
```

Al abrirse lee **`CLAUDE.md` solo**, sin que se lo pidas: ahí están la rama, los
precios, qué cifras no pueden salir al documento del cliente y el checklist del HTML.
Instrucciones de instalación al día en <https://code.claude.com/docs>.

### Ver la propuesta

Es un archivo suelto, sin dependencias. Se abre directo en el navegador:

```bash
open propuesta/propuesta-paca.html      # macOS
xdg-open propuesta/propuesta-paca.html  # Linux
start propuesta\propuesta-paca.html     # Windows
```

### Regenerar el Excel del catálogo

Sólo si cambia el catálogo de 30 artículos:

```bash
pip install openpyxl
python3 entregables/generar-catalogo-xlsx.py
```

### Verificar el responsivo — no lo supongas, mídelo

Antes de dar por buena cualquier edición del HTML, ábrelo en Chromium a **320, 400,
560, 768 y 1280 px**, haz un `window.scrollTo(500, 0)` **de verdad** y comprueba que
`window.scrollX === 0`. Medir `scrollWidth` a secas da falsos positivos: ya pasó una
vez con la tabla comparativa y se coló un desbordamiento a 320 px.

```bash
npm install playwright && npx playwright install chromium
```

### Reglas al editar la propuesta

`propuesta/propuesta-paca.html` es lo único que ve el cliente. El checklist está en
el comentario del `<style>` y no se negocia: sin emojis (los iconos son glifos CSS),
sin `transition: all`, colores **sólo** desde `:root`, estados de `:focus-visible`,
`:active` y `[disabled]`, `prefers-reduced-motion` respetado, y cero menciones a
Omnia — la marca es 786 Marketing.

Y **nunca** pueden aparecer ahí: el piso de negociación, cifras en pesos mexicanos,
el reparto con 786, el total del primer año ni datos de contacto.

---

## 11. Mapa de archivos

| Ruta | Qué es |
|---|---|
| `CLAUDE.md` | Las reglas. Claude Code lo lee solo al abrir el repo |
| `docs/08-traspaso.md` | **Tu tarea concreta** y cómo arrancar |
| `docs/10-contexto-completo.md` | Este documento |
| `docs/00-alcance-tecnico.md` | Qué se puede construir y qué no es nativo en GHL |
| `docs/01-mapa-ghl.md` | Pipeline, workflows, los 19 nodos del agente, plantillas |
| `docs/02-arquitectura-inventario.md` | Inventario, apartado de 24 h, concurrencia |
| `docs/03-catalogo-productos.md` | Los 30 SKUs y las tres calidades |
| `docs/04-precotizacion.md` | Números, margen y piso — **interno, no sale del equipo** |
| `docs/05-preguntas-cliente.md` | Lo que falta preguntarle al cliente |
| `docs/06-logistica-envia.md` | Envia.com, guías y el buscador de sucursal |
| `docs/07-decision-checkout.md` | Por qué el cobro va por liga y no por la tienda |
| `docs/09-conversacion.md` | La conversación completa — **no es fuente de verdad** |
| `propuesta/propuesta-paca.html` | La propuesta que ve el cliente |
| `entregables/` | Lo que se le manda al cliente: el Excel del catálogo |
| `data/catalogo.csv` | 30 SKUs: 17 de verano, 13 de invierno |

---

## 12. Cómo se escribe aquí

Todo en **español de México**, dirigido a gente que no es técnica. Se explica qué
cambia para el negocio, no cómo funciona por dentro. Sin adornos y sin vender de más:
si algo está por validar, se dice que está por validar.
