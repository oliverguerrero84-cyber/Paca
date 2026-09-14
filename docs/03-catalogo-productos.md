# Catálogo de productos — 30 pacas

**Fuentes:** `Lista_Productos.pdf` (los 30 SKUs y su agrupación por temporada) +
transcripts 3 y 4 (tallas, contenido, calidades, peso).

**Unidad de venta en menudeo:** paca completa cerrada de **100 lb / 45 kg**, de 1 en 1.
No se venden piezas sueltas.

---

## Las tres calidades

El cliente maneja tres niveles. Textual del transcript 4:

> "Tenemos desde la mejor calidad, una calidad bajo y una calidad económica. No la
> llamamos económica como tal, porque pues luego la gente ahí con esas palabras…
> nosotros la llamamos como **especial**."

| Nivel | Nombre comercial | Nota |
|---|---|---|
| Alta | **Boutique** | La mejor |
| Media | **Premium** | Intermedia |
| Baja | **Especial** | Es la económica. **Nunca llamarla "económica" ante el cliente final** — regla explícita del cliente, debe ir al Global Prompt del agente. |

Algunos artículos son **unicalidad** (calidad estándar, sin los tres niveles):
disfraz, ropa de hospital, vestido de fiesta, ropa de casa, playera comercial,
suéter navideño y las mixtas plus.

---

## Verano — 17 artículos

| SKU | Artículo | Tallas | Contenido |
|---|---|---|---|
| `PV-MUJ-BOU/PRE/ESP` | Mujer verano ×3 calidades | CH, M, G, XL | Shorts, faldas, pantalones, blusas (manga corta, tres cuartos, tirantes), vestidos |
| `PV-HOM-BOU/PRE/ESP` | Hombre verano ×3 calidades | CH, M, G, XL | Shorts, pantalones, camisas con y sin mangas, camisas de vestir, deportivo |
| `PV-NIN-BOU/PRE/ESP` | Niño verano ×3 calidades | 0 a 16 años | Mamelucos, enterizos, blusitas, shorts, pantalones. Niño y niña en la misma paca |
| `PV-COR-BOU/PRE` | Corsé verano ×2 calidades | ⚠️ pendiente | ⚠️ No descrito en ningún transcript |
| `PV-PLA-EST` | Playera comercial | ⚠️ pendiente | ⚠️ No descrito |
| `PV-VES-EST` | Vestido de fiesta | CH, M, G, XL | Sólo mujer adulta. Calidad estándar |
| `PV-HOS-EST` | Ropa de hospital | CH, M, G, XL | Scrubs, sólo adultos. A veces juego completo, a veces sólo playera o sólo pantalón |
| `PV-CAS-EST` | Ropa de casa | N/A | Sábanas, cortinas, cortinas de baño, a veces cojines |
| `PV-MIX-PLU` | Mixta verano plus | 1X, 2X, 3X | Mujer y hombre juntos |
| `PV-DIS-EST` | Disfraz | Revueltas | Niño y adulto mezclados. Calidad estándar |

## Invierno — 13 artículos

| SKU | Artículo | Tallas | Contenido |
|---|---|---|---|
| `PI-MUJ-BOU/PRE/ESP` | Mujer invierno ×3 calidades | CH, M, G, XL | Calcetines, mallas, medias, suéteres, sudaderas, manga larga, mezclilla, pantalón de vestir |
| `PI-HOM-BOU/PRE/ESP` | Hombre invierno ×3 calidades | CH, M, G, XL | Gorritos, calcetas, pantalones largos, pants, suéteres, sudaderas |
| `PI-NIN-BOU/PRE/ESP` | Niño invierno ×3 calidades | 0 a 16 años | Ropa de frío, niño y niña en la misma paca |
| `PI-CHA-BOU/PRE` | Chamarra ×2 calidades | ⚠️ pendiente | ⚠️ No descrito |
| `PI-MIX-PLU` | Mixta invierno plus | 1X, 2X, 3X | Mujer y hombre juntos |
| `PI-SUE-NAV` | Suéter navideño | ⚠️ pendiente | ⚠️ No descrito |

---

## Dato faltante que afecta directamente al bot

**Piezas por paca.** Todas pesan lo mismo (100 lb), pero **la cantidad de prendas
varía** — y es la pregunta que más hacen los clientes. Del transcript 4:

> "Las pacas de calor no traen la misma cantidad de ropa que las pacas de frío.
> Porque obviamente las de frío, como son un poco más sustentosas, un poco más
> voluminosas, pues obviamente alcanzan menor cantidad de piezas. Todas son de 100
> libras, que son 45 kilos. […] en una de tal mujer calor te puedo decir que son 220
> y en una trajo 225. […] O en una trajo 185. Así va variando. **Te puedo sacar los
> estándares.**"

Rango conocido de verano: **~185 a 225 piezas**. Invierno: menos, sin cifra.
El cliente ya se ofreció a mandar los estándares por SKU — hay que pedírselos.
En `data/catalogo.csv` la columna `piezas_aprox` está marcada `PENDIENTE` en las 30 filas.

Mientras no llegue ese dato, el agente debe responder con un rango y aclarar que
varía por paca, nunca con una cifra inventada.

---

## Cómo se usan estos archivos

| Archivo | Uso |
|---|---|
| `data/catalogo.csv` | Fuente de la **Knowledge Base** del agente de Agent Studio |
| `data/plantilla-stock.csv` | Pestaña `STOCK` del Google Sheet — el cliente llena `precio_menudeo_mxn`, `piezas_aprox` y `disponible` |
| `data/plantilla-apartados.csv` | Pestaña `APARTADOS` — la escribe n8n, nadie a mano |
| `data/plantilla-ordenes.csv` | Pestaña `ORDENES` — la escribe n8n; el almacén sólo toca `guia` vía formulario |
| `data/plantilla-config.csv` | Pestaña `CONFIG` — parámetros del sistema |
