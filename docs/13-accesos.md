# Altas y accesos — la cadena, en orden

> **Interno.** Qué hay que dar de alta, en qué orden y quién lo hace, para que ninguna
> tarea arranque antes que la que la habilita. Cubre lo del cliente, lo de los
> proveedores y lo nuestro.
>
> `docs/11-cronograma.md` dice **cuándo**; este documento dice **en qué orden**. Si se
> contradicen, gana éste.

---

## 1. Cómo se lee

Una sola regla: **nada arranca antes que su dependencia.**

De ahí sale la forma del documento. Primero el **eslabón 0**, que es la raíz y no
depende de nadie. Después cuatro **carriles** —Meta, cobro, envíos y el agente— que
corren en paralelo porque no se estorban entre sí.

Que dos carriles avancen al mismo tiempo no es un problema: es lo que permite entregar
en cuatro semanas. El problema es cuando una tarea **espera** a otra y se programa
antes. Eso es lo que este documento evita, y el §9 dice qué se rompe cuando pasa.

Dentro de cada carril, los eslabones van numerados y **cada uno espera al anterior**.

---

## 2. Eslabón 0 — la raíz, antes que todo lo demás

La subcuenta ya existe y el esqueleto está dentro (ver tabla), verificado el 24 de
sep. Lo que sigue en pie de este eslabón es de 786, ninguna parte depende del cliente,
y el resto del proyecto cuelga de ello.

> **Dos cosas más que salieron el 24 de sep al revisarla:** la subcuenta quedó con la
> moneda en **USD**, y tiene un producto de prueba (`test 1`, $1.00 USD) y un workflow
> en borrador sin nombre.

| # | Qué | Quién | Qué desbloquea |
|---|---|---|---|
| **0.1** | **Rotar el PIT de Korvance** | 786 | Va primero por higiene: todo lo demás usa ese token |
| ~~**0.2a**~~ | ~~**Crear la subcuenta**~~ — **HECHA el 24 sep**: **Greentex Clothing LLC** (`c9jj5uu1WZOIkwi6Vfj5`) — McAllen, Texas, zona horaria `America/Chicago` | 786 | — |
| ~~**0.2b**~~ | ~~**Levantar el esqueleto dentro**~~ — **HECHO el 24 sep**: pipeline de 8 etapas, 4 carpetas con sus 19 campos y los 8 custom values, verificados releyendo la cuenta | 786 | — |
| **0.2c** | **Cambiar la moneda de la subcuenta a MXN** antes de cargar un solo precio real | 786 | Que las ligas salgan en pesos. Mercado Pago México no cobra en dólares |
| **0.2d** | **Generar un PIT de la subcuenta Greentex** | 786 | El MCP de GHL hoy sólo ve Korvance: todo lo de Greentex por API da `403` |
| **0.3** | **Levantar la instancia de n8n** y **volver a llenar las 5 URLs**, que hoy están en `PENDIENTE` | 786 | Los 5 flujos `N1`–`N5`, y con ellos la validación 3 |

**La instancia de n8n ya tiene dueño.** Corre en la de Germán, prestada al proyecto.
Eso destraba `0.3` de inmediato y es lo más rápido para arrancar.

Lo que conviene dejar escrito ahora y no en la entrega: **el apartado del cliente va a
correr sobre una instancia que no es del cliente.** Si algún día hay que moverla, se
mueve con su negocio encima. Falta definir quién la opera en el día a día y qué pasa
con ella en el traspaso.

⚠️ **El PIT de 0.1 se compartió en texto plano por chat** (`docs/12-alta-subcuenta.md`).
Hay que revocarlo y generar uno nuevo. El token **no quedó en el repo** —ni en el árbol
ni en el historial—, así que basta con revocarlo en GHL.

Los 23 campos del formulario de alta ya existen en Korvance y ahí se quedan. **`0.2b`
arranca de cero**: los 19 campos del proyecto son otros —apartado, pago, envío y
atribución— y están especificados en `docs/01-mapa-ghl.md` §4.

> **Corrección.** Una versión anterior de esta nota decía que esos 23 campos había
> que replicarlos en la subcuenta del cliente. **Es falso.** Son el formulario con
> el que la agencia le pide sus datos al cliente *para poder crear la subcuenta*, y
> ya cumplieron. Viven en el ambiente de la agencia y **no se copian a Greentex**:
> sería meter un formulario de onboarding dentro del CRM del cliente. El script
> sirve para el siguiente cliente, no para éste.

---

## 3. Carril A — Meta y WhatsApp

**El más largo del proyecto, y el único cuyo plazo no controlamos.** Arranca el día 1
aunque no haya pasado nada más.

```
A1  El cliente verifica su Meta Business Manager           CLIENTE
A2  El cliente agrega a 786 como socio del portafolio      CLIENTE
A3  Confirmar que +1 (956) 820-2011 recibe SMS o voz       786     <- no espera a nadie
A4  Alta del número en Meta  ->  nace la WABA              786
A5  Redactar las 6 plantillas                              786     <- no espera a nadie
A6  Mandar las 4 a aprobación de Meta                      786
       |   24 a 48 horas de espera, y puede rechazarlas
A7  Aprobadas  ->  ya se pueden usar en SP02, SP04 y SP05
```

**A3 y A5 no dependen de nadie.** Se adelantan mientras el cliente hace A1 y A2, y
conviene hacerlo: son las dos únicas cosas de este carril que podemos mover solos.

**A3 va temprano a propósito.** Meta manda el código de verificación por SMS o llamada.
Si el número resulta ser VoIP, A4 falla y hay que conseguir otro — mejor descubrirlo el
primer día que la tercera semana.

**A6 es el cuello de botella real.** Las cuatro plantillas que necesitan aprobación son
el recordatorio de apartado, la confirmación de pago, la orden enviada con guía y la
recuperación de apartado vencido. Existen porque el apartado de 24 h empuja esos
mensajes fuera de la ventana de WhatsApp, y fuera de ella sólo pasan plantillas
aprobadas.

> **El orden A4 → A6 no se invierte.** Las plantillas viven dentro de una WhatsApp
> Business Account, y la WABA no existe hasta que el número está dado de alta. Mandar
> plantillas antes de A4 no es que salga mal: es que no hay a dónde mandarlas.

---

## 4. Carril B — Cobro con Mercado Pago

786 tiene cuenta propia, y eso cambia el proyecto: **las tres validaciones que sostienen
el diseño se corren desde el día 1**, sin esperar la verificación fiscal del cliente.

Van en **Greentex**, que ya existe: es donde el sistema va a correr de verdad, y una
liga que cobra en otra subcuenta no prueba que cobre en ésta. La contra es que dejan
rastro —producto de prueba, factura, cobro mínimo—, así que **hay que limpiarlo al
terminar cada validación**.

Korvance —la subcuenta de trabajo de 786, en Argentina y con Stripe, donde entró el
pago del cliente por la implementación— **no se toca**.

```
B1  Public Key + Access Token de la cuenta de 786          786      HECHO (modo test)
B2  Conectar en Pagos -> Integraciones                     786      HECHO (proveedor por defecto)
B3  VALIDACIÓN 1 — la liga de pago cobra de verdad         786      A MEDIAS, ver abajo
B4  VALIDACIÓN 2 — pagar la liga no descuenta stock solo   786
B5  VALIDACIÓN 4 — Payment Received con los tres métodos   786      BLOQUEADA, ver abajo
─────────── todo lo de arriba corre en Greentex, día 1 ───────────
B6  El cliente abre y verifica Mercado Pago                CLIENTE  <- tarda
B7  Sus credenciales sustituyen a las de 786               786      <- antes del go-live
```

**Lo que se probó el 24 de septiembre.** Se creó la liga
`link.korvance.com/payment-link/6ab58d404ae1d456728396ec` sobre `test 1`, en modo Test.
Abierta como cliente, **sí levanta el checkout de Mercado Pago** con la marca `TEST
MODE`: la mitad mecánica de la validación 1 está. Falta pagarla con una tarjeta de
prueba de Mercado Pago y ver la transacción en GHL —eso lo hace Germán, no el
asistente— y falta repetirla con credenciales de México, por lo que sigue.

> ⚠️ **Las credenciales conectadas son de una cuenta de Mercado Pago de Argentina, no
> de México.** El checkout pide *Cardholder ID* con las opciones **DNI, Cédula, L.C.,
> L.E., Otro** —documentos argentinos— y **sólo ofrece tarjeta**. No aparecen OXXO ni
> SPEI, porque esos métodos existen únicamente en cuentas de México. Consecuencias:
>
> - La **validación 4** (los tres métodos) **no se puede correr** con esta cuenta. Ni en
>   test ni en live.
> - Una cuenta argentina cobra en pesos argentinos; el producto está en USD y el
>   catálogo real va en MXN. Aunque el pago de prueba pase, no prueba el caso real.
> - **Hace falta una cuenta de Mercado Pago México**, y basta con sus credenciales de
>   **test**: no requiere verificación fiscal. Puede ser la del cliente —sin esperar
>   `B6` completo— o una de 786 dada de alta en México. Sustituye a `B1`.

B3 necesita un producto con precio dentro de la subcuenta, así que va después del
eslabón 0 — pero con **un producto de prueba**, no con el catálogo real. El Excel del
cliente no bloquea esto. `test 1` ya existe, pero **sin inventario activado**: para la
validación 2 hay que prenderle *Track inventory* y darle cantidad.

**La validación 4 es nueva aquí.** Estaba sólo en `docs/02-arquitectura-inventario.md` y
no había llegado al cronograma: hay que comprobar que `Payment Received` dispare igual
con los tres métodos, **incluido el efectivo**. Es la que amarra la rama de OXXO, y
OXXO acredita en hasta 72 horas hábiles — si se lanza un jueves, el resultado llega la
semana siguiente. Se arranca temprano o no da tiempo.

**B6 ya no bloquea el diseño, pero sí el dinero.** Sin verificación de identidad y
fiscal, Mercado Pago retiene fondos. Se puede entregar igual, pero el cliente lo va a
sentir como una falla del sistema: conviene avisarlo por escrito antes.

> **Si B3 falla**, entra el Plan B: cobrar por el checkout de la tienda y **renunciar al
> apartado de 24 h**, porque ahí sí chocan. Hay que decírselo al cliente la misma
> semana, no en la entrega — el apartado es una de las cosas que compró.

---

## 5. Carril C — Envíos con Envia.com

```
C1  El cliente abre cuenta en Envia.com                    CLIENTE
C2  El cliente la fondea — prepago, sin mensualidad        CLIENTE
C3  Obtener las credenciales de API                        SIN DUEÑO  <- ver §8
C4  N3 · buscar sucursal por código postal                 786     <- NO necesita saldo
C5  N4 · generar guía  ·  N5 · rastrear                    786     <- SÍ necesitan saldo
C6  Pedir tarifas para 500–800 guías al mes                786
```

**El corte entre C4 y C5 es lo que permite adelantar trabajo.** `validate-zip-code` y
`carrier-branches` son consulta de catálogo: se prueban con la cuenta recién abierta,
antes de que tenga un peso. Generar guías sí descuenta saldo, así que `N4` y `N5`
esperan a C2.

C6 no bloquea nada — se puede pedir en cualquier momento — pero conviene hacerlo
temprano porque el envío va incluido en el precio y la tarifa real afecta el margen del
cliente.

---

## 6. Carril D — El agente de WhatsApp

**Aquí converge todo.** Es el único punto donde los tres carriles anteriores se juntan, y
es trabajo manual de principio a fin: los bots de GHL no tienen API.

| Necesita | Viene de | Si falta |
|---|---|---|
| Canal de WhatsApp enganchado | **A4** | El agente existe pero nadie le escribe |
| `N1` vivo — nodo 11, consulta de stock | **0.3** | El nodo 11 no responde y la conversación se traba |
| `N3` vivo — nodo 16, sucursales | **C4** | No puede ofrecer dónde recoger |
| Knowledge Base subida **y asociada** | Catálogo + las 6 descripciones que faltan | Contesta de memoria, inventando |
| Productos con precio | Excel del cliente, límite **5 oct** | No cotiza ni genera liga |
| Fotos y videos — nodo 9 | Cliente, límite **12 oct** | Manda texto donde iba un video |

Y en orden, una vez que esas piezas existen:

```
D1  VALIDACIÓN 5 — Agent Studio soporta los nodos diseñados 786  <- va en la semana 1
D2  VALIDACIÓN 3 — el nodo API Call responde a tiempo       786  <- necesita N1 vivo
D3  Construir los 19 nodos del agente                       786  <- a mano, sin API
D4  Enganchar el canal de WhatsApp al agente                786
D5  Subir la Knowledge Base y asociarla                     786
```

**`D1` no espera a nada y por eso sube a la semana 1.** Es una prueba de humo en
Greentex: armar tres o cuatro nodos sueltos —un `API Call`, un `Single Choice`, un
`Capture`— y ver que existan y corran. Todo el diseño conversacional asume que Agent
Studio puede hacer eso; si no puede, no es un ajuste, es rediseñar el carril entero.
Descubrirlo en la semana 3, con los 19 nodos a medio armar, es el peor momento.

**La validación 3 pertenece a este carril, no al de cobro.** Comprobar que el nodo
`API Call` responde a tiempo exige que `N1` ya exista: es una prueba contra un endpoint
vivo, no contra una idea. Por eso `D1` va antes que `D2`: si el nodo no responde a
tiempo, cambia cómo se arma la conversación.

Cuatro cosas que cuestan un bug si se ignoran al construirlo: los campos de temporada,
categoría y calidad van como **texto gemelo**, porque un bot no escribe en listas
desplegables; las acciones tienen **tope de 500 caracteres**; un **Transfer Bot** con
condición agresiva se roba el primer turno y las capturas nunca corren; y **subir la
Knowledge Base no es asociarla** — son dos pasos.

---

## 7. Tabla de convergencia — qué espera a qué

Para cada cosa que queremos poder hacer, qué tiene que estar cerrado antes. Es el
resumen que contesta directo si algo se está solapando.

| Para poder… | Tienen que estar listos |
|---|---|
| Crear una liga de pago | `0.2` · `B1` · `B2` |
| Probar que el cobro funciona | lo anterior + un producto de prueba con precio |
| Mandar plantillas a Meta | `A1` · `A2` · `A3` · `A4` |
| Probar el apartado de 24 h | `0.2` · `0.3` · `N1` · `B3` |
| Generar una guía real | `C1` · `C2` · `C3` |
| Construir el agente | `A4` · `0.3` con `N1` · `C4` con `N3` · Knowledge Base · productos |
| Probar de punta a punta | todos los carriles + `A7` |
| Entregar | lo anterior + `B7` + fotos y videos |

---

## 8. Los cuatro huecos sin dueño

Nada de esto existe hoy en la documentación, y los cuatro son tareas, no dudas
teóricas. Tres se resuelven preguntando en el onboarding; el segundo es nuestro.

| # | Hueco | Bloquea |
|---|---|---|
| 1 | **Cómo se obtienen las credenciales de API de Envia**, y si hay ambiente de pruebas | `C3`, y con él `N3`, `N4` y `N5` |
| 2 | ~~Dónde corre n8n~~ — **resuelto**: la instancia de Germán, prestada. Falta quién la opera y qué pasa en el traspaso | Ya no bloquea `0.3` |
| ~~3~~ | ~~**Qué es Korvance y de quién es**~~ — **RESUELTO el 23 sep**: es la cuenta de trabajo de Germán, un ambiente de pruebas | — |
| 4 | **Roles y permisos** de Pamela, Miguel y Mauricio dentro de la subcuenta | La capacitación de la última semana |
| 5 | **Credenciales de Mercado Pago México** — las conectadas son de Argentina y no tienen OXXO ni SPEI | `B5`, y la mitad real de `B3` |

---

## 9. Qué se rompe si se invierte el orden

Tres casos concretos, los tres detectados en la primera versión del cronograma:

**Plantillas antes de la WABA.** No hay a dónde mandarlas. La aprobación de Meta se
recorre a donde sí exista la WABA, y como tarda de 24 a 48 horas y puede rechazar, se
lleva el go-live con ella. Es el único plazo que no controlamos.

**Validaciones antes de la subcuenta.** Las validaciones 1, 2 y 4 necesitan un producto
con precio y stock. Sin subcuenta no hay productos, así que la prueba no falla: no se
puede ni empezar. Y si la validación 1 se atrasa, se atrasa también la decisión sobre el
apartado de 24 h, que es lo que hay que avisarle al cliente cuanto antes.

**El `API Call` antes de que n8n exista.** La validación 3 mide cuánto tarda el agente
en recibir respuesta de `N1`. Sin `N1` no hay nada que medir, y darla por buena sin
probarla es justo lo que la regla del toolkit prohíbe: *"se guardó" no es "funciona"*.
