# Alta de subcuenta — los campos y cómo se arma el formulario

> **Qué es esto.** Los datos que hay que pedirle al cliente para darle de alta su
> subcuenta en GoHighLevel. Los 23 campos ya están creados en la subcuenta de trabajo
> **Korvance**, agrupados en la carpeta **«Alta de subcuenta»**
> (`MZ6vbpBXTkiZRQfNlK6J`), listos para arrastrarlos a un formulario.

## 0. Por qué este formulario vive en Korvance

El proyecto arrancó **sin tener ninguna cuenta** donde alojar al cliente. Se decidió
alojarlo en la agencia de Germán, y el formulario se armó en **Korvance** porque era
el único lugar que existía. No fue un error de diseño: era la única forma de arrancar.

Sobre la marcha salió la limitación: **lo que el cliente captura en la cuenta de la
agencia no se jala solo a su propia subcuenta.** Así que Germán abrió el formulario
desde Korvance, lo llenó, y con esos datos **creó Greentex Clothing LLC a mano**.

De ahí en adelante todo lo de GHL va directo a Greentex. Este formulario se queda en
Korvance y sirve para el siguiente cliente.

> ⚠️ **Rotar el PIT.** El token con el que se crearon estos campos se compartió en
> texto plano por chat. Conviene revocarlo y generar uno nuevo en la subcuenta.

---

## 1. Armar el formulario en la interfaz

**El formulario no se puede construir por API** — en GHL son de interfaz, igual que los
bots de Conversation AI. Pero los campos ya existen y están en una sola carpeta, así
que se arrastran de un jalón.

En el constructor de formularios, los campos aparecen bajo la carpeta «Alta de
subcuenta». Van en este orden, que es el mismo del formulario **Add Sub-Account** de
GHL, para poder copiar de arriba abajo sin saltar.

## 2. Bloque 1 — Datos del negocio

Son los que van tal cual al alta de la subcuenta.

| # | Campo | Tipo | Obligatorio | Equivale a |
|---|---|---|---|---|
| 1 | Nombre del negocio | Texto | **Sí** | Business Name |
| 2 | Giro o nicho del negocio | Texto | No | Business Niche |
| 3 | Teléfono del negocio | Teléfono | **Sí** | Business Phone |
| 4 | Dirección del negocio | Texto | **Sí** | Address |
| 5 | Ciudad del negocio | Texto | **Sí** | City |
| 6 | Estado o provincia | Texto | No | State |
| 7 | País del negocio | Desplegable | **Sí** | Country |
| 8 | Código postal | Texto | **Sí** | Zip |
| 9 | Sitio web | URL | No | Website |
| 10 | Zona horaria | Desplegable | **Sí** | Time Zone |

**País** ofrece: México · Estados Unidos · Otro.

**Zona horaria** ofrece las cinco que aplican, con el nombre técnico dentro de la
etiqueta para que quien dé de alta la subcuenta elija sin adivinar:

- Centro de México — `America/Mexico_City`
- Monterrey y Nuevo Laredo — `America/Monterrey`
- Chihuahua — `America/Chihuahua`
- Tijuana — `America/Tijuana`
- Texas — `America/Chicago`

> **El código postal es de texto, no numérico**, a propósito: los CP mexicanos que
> empiezan en cero perderían el primer dígito.

## 3. Bloque 2 — Administrador de la subcuenta

Los tres primeros campos del formulario de GHL son del **usuario dueño**, que no tiene
por qué ser quien llena el formulario. Por eso son campos propios y no se apoyan en el
nombre y el correo estándar del contacto.

| # | Campo | Tipo | Obligatorio | Equivale a |
|---|---|---|---|---|
| 11 | Nombre del administrador | Texto | **Sí** | First Name |
| 12 | Apellido del administrador | Texto | **Sí** | Last Name |
| 13 | Correo del administrador | Texto | **Sí** | Email |

> El correo va en texto porque **GHL no tiene un tipo de dato `EMAIL`** para campos
> personalizados. Conviene marcar validación de correo en el formulario.

## 4. Bloque 3 — Los tres usuarios

Los que van a trabajar dentro de la subcuenta. Nueve campos planos y no una lista, para
que cada dato se pueda leer y escribir por separado desde un workflow.

| # | Campo | Tipo |
|---|---|---|
| 14 · 15 · 16 | Usuario 1 — Nombre completo · Correo · Teléfono | Texto · Texto · Teléfono |
| 17 · 18 · 19 | Usuario 2 — los mismos tres | |
| 20 · 21 · 22 | Usuario 3 — los mismos tres | |

Conviene dejar al usuario 1 obligatorio y los otros dos opcionales: si sólo van a entrar
dos personas, el formulario no debería trabarse.

## 5. Bloque 4 — Cierre

| # | Campo | Tipo |
|---|---|---|
| 23 | Algo más que debamos saber | Texto largo |

---

## 6. Las claves, por si se citan desde un workflow

Todas llevan el prefijo `contact.` que GHL antepone solo:

```
contact.alta_nombre_negocio      contact.alta_admin_nombre
contact.alta_giro_negocio        contact.alta_admin_apellido
contact.alta_telefono_negocio    contact.alta_admin_correo
contact.alta_direccion_negocio
contact.alta_ciudad_negocio      contact.alta_usuario1_nombre
contact.alta_estado_negocio      contact.alta_usuario1_correo
contact.alta_pais_negocio        contact.alta_usuario1_telefono
contact.alta_codigo_postal       contact.alta_usuario2_nombre
contact.alta_sitio_web           contact.alta_usuario2_correo
contact.alta_zona_horaria        contact.alta_usuario2_telefono
                                 contact.alta_usuario3_nombre
contact.alta_notas               contact.alta_usuario3_correo
                                 contact.alta_usuario3_telefono
```

> **La clave se fija al crear el campo y ya no se puede cambiar.** El PUT la rechaza.
> Si hiciera falta otra, hay que borrar el campo y rehacerlo — y actualizar todo lo que
> la cite.

## 7. Para el siguiente cliente

**Estos campos se quedan en el ambiente de la agencia y no se copian a la subcuenta
del cliente.** Son el formulario con el que se le piden los datos *para poder crear
esa subcuenta*: una vez creada, ya cumplieron. Meterlos en el CRM del cliente sería
dejarle ahí un formulario de onboarding que no es suyo.

`scripts/crear-campos-alta-subcuenta.py` es idempotente: deduplica por clave, así que
correrlo otra vez no duplica nada. Sirve para montar el mismo formulario en otro
ambiente cuando entre el siguiente cliente.

```bash
export GHL_API_KEY='pit-...'
export GHL_LOCATION_ID='...'
python3 scripts/crear-campos-alta-subcuenta.py --dry-run   # ver qué haría
python3 scripts/crear-campos-alta-subcuenta.py             # hacerlo
```

Las credenciales se leen del entorno y **nunca se escriben a disco**.
