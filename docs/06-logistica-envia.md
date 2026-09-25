# Logística — Envia.com y el buscador de sucursal

Cómo se resuelven las guías, la recolección, el rastreo y —la parte difícil— darle
al cliente la sucursal correcta sin que tenga que escribir una dirección.

---

## 1. Por qué Envia.com

Paquete Express no expone una API propia utilizable. Envia.com es un agregador que
sí lo hace, y cubre de un golpe todo lo que el proyecto necesita.

| Endpoint | Para qué sirve aquí |
|---|---|
| `GET /carrier-branches` | **Catálogo de sucursales** por paquetería y país |
| `GET /validate-zip-code` | Valida el código postal, devuelve ciudad y estado |
| `POST /ship/rate/` | Cotiza en tiempo real entre paqueterías |
| `POST /ship/generate/` | **Genera la guía con número de rastreo** |
| `POST /ship/pickup/` | Programa la recolección en el almacén |
| `GET /ship/track/` | Estatus y eventos del paquete |
| `POST /ship/cancel/` | Cancela la guía y pide reembolso |
| `GET /guide/{tracking}` | Detalle completo de un envío |

**Costo: prepago, sin mensualidad y sin comisión.** Se carga saldo a la cuenta y se
paga por guía generada. Es un costo del cliente y va en la lista de terceros, junto
con WhatsApp API y las comisiones de Stripe.

> Se evaluó también **pkge.net**, que sólo rastrea. Envia hace eso y además genera
> guías y programa recolecciones, así que lo reemplaza por completo.

---

## 2. Lo que cambia en el almacén

**Antes** — tal como lo describió Pamela:

> "Ellos se encargaban de hacer las recolecciones con Paquete Express y ellos nos
> retornaban a nosotros las guías. Paquete Express les daba las guías y ya nada más
> ellos nos las colocaban en un Excel y nosotros del Excel las bajábamos y las
> compartíamos manualmente."

**Después:**

```
  Pago confirmado en GHL
        │
        ▼
  n8n → POST /ship/generate/     la guía nace con su número de rastreo
        │
        ├──► PDF de la etiqueta al WhatsApp del almacén
        │    con nombre, cantidad, destino y código postal
        │
        ├──► POST /ship/pickup/   se programa la recolección
        │
        └──► GET /ship/track/     el estatus alimenta los avisos al cliente
```

El almacén **imprime y pega**. Nada más. Ya no van por guías, ya no capturan
números, ya no hay Excel intermedio.

> **Con esto se cae el único paso manual del sistema.** Las revisiones anteriores de
> la propuesta decían que capturar el número de guía era inevitable. Ya no lo es.

Miguel pidió que fuera simple: *"no sé si a través de, inclusive hasta una impresora
podemos comprar, o un email, o un WhatsApp, así muy sencillo: Juan González García,
tal paquete, a Campeche, código postal. Ya ellos se encargan de lo demás."*
El PDF por WhatsApp cumple exactamente eso.

Y la regla dura: **el almacén no ve dinero.** *"Ellos no tienen por qué enterarse."*

---

## 3. El buscador de sucursal — el problema de verdad

Esta es la razón por la que apagaron el menudeo. Pamela:

> "Cuando llegamos a la parte de las direcciones… me lo mandaban como querían. Bueno,
> ya me iba al Google Maps y buscábamos, de verdad. Era muy, muy complicado."

Y Mauricio explicó por qué no se arregla pidiendo mejor los datos:

> "Es mucho cliente que se dedica toda su vida al negocio informal; muchas veces no
> saben cómo escribir bien, no saben cómo usar muy bien el teléfono, las redes."

### La regla: nunca por IA

Oliver lo intuyó en la junta y tiene razón. Un modelo de lenguaje adivinando
coordenadas se equivoca, y equivocarse aquí significa mandar el paquete a una
sucursal a tres horas del cliente. **Esto es una consulta a tabla, determinista.**

### El flujo

```
  1. El cliente escribe su CÓDIGO POSTAL — 5 dígitos
         │        (lo único que esa gente sí sabe dar sin equivocarse)
         ▼
  2. GET /validate-zip-code      ¿existe? ¿qué ciudad y estado?
         │
         ▼
  3. GET /carrier-branches       sucursales de Paquete Express
         │                        (cacheadas, se refrescan cada tanto)
         ▼
  4. Se filtran por ciudad y estado; si no hay, por distancia
         │
         ▼
  5. Se le devuelven 2 o 3 OPCIONES con dirección y liga de Google Maps
         │
         ▼
  6. El cliente ELIGE DE UNA LISTA.  Nunca escribe la sucursal.
```

**Si no hay ninguna sucursal en cobertura** → se descalifica amablemente. Paquete
Express llega a unas 146 sucursales en ciudades principales, y para el cliente esa
descalificación es una ventaja. Miguel:

> "Quien le quede, perfecto, y quien no, pues adelante, que le busque por otro lado.
> Ya nos evitamos [el problema]."

### Por qué el código postal y no la dirección

| | Dirección escrita | Código postal |
|---|---|---|
| Cuánto hay que teclear | Calle, número, colonia, entre calles, referencias | 5 dígitos |
| Se puede validar | No | Sí, contra el catálogo oficial |
| Falla porque… | La gente escribe como quiere; hay calles mal mapeadas | Casi nunca |

Miguel ya lo había propuesto en la junta: *"pon tu código postal y en automático el
sistema le va a decir cuál es la sucursal más cercana."* Es la solución correcta.

---

## 4. Dónde se pide el código postal

**Conversando.** El bot pide el código postal y con la acción «Sucursal por código
postal» consulta a n8n `N3`, que devuelve 2 o 3 sucursales para que el cliente elija.

> ⚠️ **Esta sección decía lo contrario hasta hoy.** Decía "en el checkout, no
> conversando", con el argumento de obligar a llenar el formulario antes de activar el
> botón de pagar. **Quedó obsoleta el 16 de septiembre**, cuando el checkout de la
> tienda salió del camino de venta: el cobro va por liga y ya no hay formulario donde
> forzar nada. Ver `docs/07-decision-checkout.md`.

La preocupación de fondo seguía siendo correcta —el dato tiene que estar validado
antes de generar la guía— y se resuelve igual, sólo que antes: `validate-zip-code`
corre cuando el cliente da el CP, y si no hay sucursal cerca se le dice en ese momento,
no después de cobrarle.

---

## 5. Lo que se validó contra la API real — 25 sep 2026

Se corrió `scripts/probar-envia.py` contra el **sandbox** de Envia (ambiente de prueba
con llaves propias, sin cargos). Resultado, punto por punto de lo que estaba pendiente:

1. **Sucursales con coordenadas: sí.** `branches/paquetexpress/MX?zipcode=…` devuelve
   las sucursales **ya ordenadas por distancia en kilómetros**, con latitud, longitud,
   dirección, si admiten paquetes y sus límites (peso máximo 50 kg por sucursal, y la
   paca de 100 lb pesa 45). Ya no hay que calcular distancias ni filtrar por ciudad.
2. **El código postal sí trae coordenadas**, más ciudad, estado y colonias. No hace
   falta el dataset de Correos.
3. **Costo por guía**, cotizado en el sandbox de Nuevo Laredo a Monterrey con 45 kg:
   a sucursal **~600 MXN**, a domicilio **~770 MXN**, entrega en 1 a 3 días. Son
   tarifas de prueba; las reales dependen del contrato de la cuenta.
4. **Filtrar paqueterías: sí.** Todo se pide por paquetería en la propia URL, así que
   sólo aparece Paquete Express. Se llama `paquetexpress` en Envia.

Y tres cosas que no se sabían:

- Hay **dos formas de entregar**: a domicilio (`ground`) y **a sucursal para que el
  cliente lo recoja** (`ground_do`), que es la que pidió el cliente. La segunda
  necesita el código de la sucursal elegida, que es justo lo que devuelve la búsqueda
  por código postal.
- **Se generó una guía de cada tipo en el sandbox**: sale el PDF de la etiqueta, el
  número de rastreo y la liga de rastreo de Paquete Express. El rastreo devuelve el
  estatus de un catálogo fijo de 28 estados y la fecha estimada de entrega, y acepta
  varias guías en una sola consulta.
- Envia responde los errores con código 200 y un aviso adentro, así que los flujos
  tienen que leer la respuesta, no sólo el código.

Un límite que sí cambia el diseño: **cada sucursal acepta máximo 50 kg por paquete**, y
una paca pesa 45. Un pedido de dos o más pacas a sucursal lleva **una guía por paca**;
a domicilio no hay ese tope. `N4` todavía manda una sola caja: queda anotado en el
README de n8n como pendiente.

Lo único que sigue pendiente es del lado del cliente: **su cuenta de producción con
saldo** y los datos exactos del almacén de Nuevo Laredo.
