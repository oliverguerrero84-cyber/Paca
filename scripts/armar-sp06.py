# SP06 · Ficha de la paca — el árbol, generado desde el catálogo
#
# QUÉ ES. El equivalente al SP05 «Envío de ficha» de GALK (build_sp05_v2.py): cuando se
# sabe qué paca quiere el cliente, un workflow —no el bot— le manda la ficha completa, en
# el mismo orden siempre, y le pasa la conversación al bot de pedido. Aquí se llama SP06
# porque SP05 ya es nuestra orden al almacén. Diseño completo: docs/20-sp06-ficha.md.
#
#   [Trigger: Contact Changed → sku_elegido]  (lo escriben BOT-00 o RP-SKU, da igual cuál)
#     → Guarda: sku_elegido vacío → sale          (BOT01 lo vacía al apartar: eso no es un cambio de paca)
#     → árbol, una rama por SKU: «sku_elegido es PV-MUJ-BOU»
#         → If ficha_sku es este SKU → sale        (ya vio esta ficha: no se reenvía)
#         → Pausar BOT-00
#         → Apertura → [3 s] → Video → [3 s] → Precio y condiciones → [3 s] → Pregunta final
#         → ficha_sku = este SKU · vaciar sku_elegido · tag ficha-enviada
#         → Activar BOT-01 · Pedido
#
# POR QUÉ SE VACÍA sku_elegido. «Contact Info» del bot sólo llena campos vacíos. Si el campo
# se queda lleno, el bot no puede escribir otra paca cuando el cliente cambia de opinión, ni
# la clave al confirmar el pedido (que es lo que lee `BOT01 · Apartar paca`). La memoria de
# qué ficha ya vio queda en ficha_sku. Vaciarlo vuelve a disparar el workflow, y la guarda
# de «vacío» lo saca sin hacer nada.
#
# ESTRUCTURA FIJA, COMO GALK. Lo que el cliente ve son 3 o 4 mensajes (3 si la paca todavía
# no tiene video). Lo demás es interno: la pausa del bot, las esperas, el campo, el tag y la
# activación del bot de pedido.
#
# LA PREGUNTA FINAL PIDE EL CAMPO QUE LE FALTA AL PEDIDO. Es la regla de GALK: en talleres
# falta la sede, en software la modalidad. Aquí la paca ya se sabe y lo que falta es
# cuántas: `cantidad_elegida`, lo que BOT01 necesita para apartar. El nombre se pide en la
# apertura, igual que GALK, para que el cliente conteste los dos en un solo mensaje.
#
# ⚠️ LOS TEXTOS SON UN BORRADOR NUESTRO. En GALK cada ficha es el texto del cliente,
# transcrito tal cual. Aquí el cliente no mandó textos: se arman del catálogo con una sola
# plantilla, y Pamela tiene que aprobarlos antes de escribir nada en la cuenta.
#
# ⚠️ SIN MOLDE NO SE ESCRIBE. Igual que RP-SKU: los nodos se clonan de una rama armada a
# mano en la UI (docs/20-sp06-ficha.md §5). Este script hoy sólo imprime el árbol.
#
# Uso (desde la raíz del repo):
#   python scripts/armar-sp06.py --dry-run          resumen del árbol y validaciones
#   python scripts/armar-sp06.py --fichas           además, el texto completo de las 30 fichas
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOGO = "data/catalogo.csv"
NOMBRE = "SP06 · Ficha de la paca"
ESPERA_SEG = 3
MIN_MENSAJES, MAX_MENSAJES = 3, 7      # el rango real de GALK (no «6 a 8»)

# Video de cada SKU en el media store de la subcuenta: «sku»: (media_id, nombre, bytes).
# Vacío hasta subirlos. Una paca sin video manda su ficha igual, con un mensaje menos.
# ⚠️ WhatsApp no acepta videos de más de 16 MB, y los de Pamela pesan de 12 a 50 MB:
# hay que comprimirlos antes de subirlos (docs/20-sp06-ficha.md §4).
VIDEOS = {}
LIMITE_VIDEO = 16 * 1024 * 1024

# Pacas en 0 por decisión del cliente al cargar el inventario (15 oct). Su rama no manda
# la ficha: avisa que por ahora no hay, deja a BOT-00 encendido y vacía sku_elegido para
# que pueda ofrecer otra. ⚠️ Propuesta, sin confirmar: docs/20-sp06-ficha.md §6.
NO_DISPONIBLES = {"PV-PLA-EST", "PV-HOS-EST", "PI-CHA-BOU"}


def nombre_bonito(r):
    """«MUJER VERANO BOUTIQUE» → «Mujer Verano Boutique». En el chat, las mayúsculas gritan."""
    t = r["nombre_display"].title().replace(" De ", " de ")
    return t.replace("Corse", "Corsé")




def ficha(r):
    """Los mensajes que ve el cliente, en orden: [(tipo, contenido)]."""
    nombre = nombre_bonito(r)
    calidad = "" if r["calidad"] == "Estándar" else f", calidad {r['calidad']}"
    contenido = r["contenido_resumen"][:1].lower() + r["contenido_resumen"][1:]
    tiene_video = r["sku"] in VIDEOS
    cierre = "\n\nTe comparto el video para que veas cómo viene 👇" if tiene_video else ""
    apertura = (
        f"Antes que nada, ¿cómo te llamas? 😊\n"
        f"Te paso la información de la paca *{nombre}* ({r['temporada'].lower()}{calidad}).\n\n"
        f"Es ropa americana para {r['publico'].lower()}. Trae: {contenido}.\n"
        f"Tallas: {r['tallas']}.{cierre}"
    )
    precio = (
        f"💰 *${int(r['precio_mxn']):,} MXN* por paca.\n"
        f"📦 Pesa {r['peso_lb']} lb ({r['peso_kg']} kg) y trae aprox. {r['piezas_aprox']} piezas; "
        f"puede variar un poco de una paca a otra.\n"
        f"Se vende la paca completa, no piezas sueltas. Al apartarla te la guardamos 24 horas "
        f"mientras pagas."
    )
    pregunta = f"¿Cuántas pacas de {nombre} te aparto? 😊"

    mensajes = [("texto", apertura)]
    if tiene_video:
        mensajes.append(("video", VIDEOS[r["sku"]]))
    mensajes += [("texto", precio), ("texto", pregunta)]
    return mensajes


def no_disponible(r):
    return [("texto", f"Por ahora no tenemos disponible la paca *{nombre_bonito(r)}*. "
                      f"¿Te muestro otra parecida? 😊")]


def nodos_internos(r):
    """Lo que el cliente no ve, para el conteo del resumen."""
    if r["sku"] in NO_DISPONIBLES:
        return ["If ficha_sku", "Vaciar sku_elegido"]
    return ["If ficha_sku", "Pausar bot", "ficha_sku = SKU", "Vaciar sku_elegido",
            "tag ficha-enviada", "Activar BOT-01"]


def validar(filas, ramas):
    errores = []
    claves = [r["sku"] for r in filas]
    if len(set(claves)) != len(claves):
        errores.append("hay claves repetidas en el catálogo")
    # La condición compara contra la clave. Si una clave contuviera a otra, un «contiene»
    # se llevaría la ficha equivocada (el problema de Supervisión/Melamina en GALK).
    for a in claves:
        for b in claves:
            if a != b and a in b:
                errores.append(f"la clave {a} está contenida en {b}")
    for r in filas:
        for col in ("precio_mxn", "piezas_aprox", "tallas", "contenido_resumen"):
            v = (r.get(col) or "").strip()
            if not v or "PENDIENTE" in v.upper():
                if col == "contenido_resumen" and r["sku"] in NO_DISPONIBLES:
                    continue   # no se manda su ficha: el hueco no llega al cliente
                errores.append(f"{r['sku']}: falta {col}")
    for sku, mensajes in ramas.items():
        texto = " ".join(m[1] for m in mensajes if m[0] == "texto").lower()
        if "económic" in texto or "economic" in texto:
            errores.append(f"{sku}: dice «económica» (regla 2: la calidad baja es Especial)")
        if "{" in texto or "}" in texto:
            errores.append(f"{sku}: quedó un marcador sin resolver")
        if sku not in NO_DISPONIBLES and not MIN_MENSAJES <= len(mensajes) <= MAX_MENSAJES:
            errores.append(f"{sku}: {len(mensajes)} mensajes, fuera de {MIN_MENSAJES}–{MAX_MENSAJES}")
    for sku, (_, nombre, size) in VIDEOS.items():
        if size > LIMITE_VIDEO:
            errores.append(f"{sku}: el video {nombre} pesa {size / 2**20:.1f} MB; WhatsApp acepta 16")
    return errores


def main():
    with open(CATALOGO, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    ramas = {r["sku"]: (no_disponible(r) if r["sku"] in NO_DISPONIBLES else ficha(r))
             for r in filas}

    print(f"{NOMBRE} — {len(ramas)} ramas desde {CATALOGO}\n")
    for r in filas:
        m = ramas[r["sku"]]
        if r["sku"] in NO_DISPONIBLES:
            forma = "no disponible: 1 aviso, BOT-00 sigue"
        else:
            forma = " → ".join("video" if t == "video" else "texto" for t, _ in m)
            forma = f"{len(m)} mensajes ({forma})"
        print(f"  {r['sku']:<11} {nombre_bonito(r):<26} ${int(r['precio_mxn']):>6,}  {forma}")

    con_video = sum(1 for s in ramas if s in VIDEOS)
    print(f"\n  videos: {con_video} de {len(ramas) - len(NO_DISPONIBLES)} "
          f"(las demás mandan la ficha sin video)")
    print(f"  nodos internos por rama: {', '.join(nodos_internos(filas[0]))}, "
          f"más una espera de {ESPERA_SEG} s entre mensajes")

    if "--fichas" in sys.argv:
        for r in filas:
            print(f"\n{'─' * 72}\n{r['sku']} · {nombre_bonito(r)}\n{'─' * 72}")
            for i, (tipo, contenido) in enumerate(ramas[r["sku"]], 1):
                if tipo == "video":
                    print(f"[{i}] (video {contenido[1]})")
                else:
                    print(f"[{i}] {contenido}\n")

    errores = validar(filas, ramas)
    print()
    if errores:
        for e in errores:
            print(f"✗ {e}")
        sys.exit(1)
    print("✓ claves sin colisión, catálogo completo, 3 a 7 mensajes por ficha, sin «económica»")
    print("\nSólo imprime. Escribir en la cuenta espera el molde (docs/20-sp06-ficha.md §5).")


if __name__ == "__main__":
    main()
