# SP06 · Ficha de la paca — el árbol, generado desde el catálogo
#
# QUÉ ES. El equivalente al SP05 «Envío de ficha» de GALK (build_sp05_v2.py): cuando se
# sabe qué paca quiere el cliente, un workflow —no el bot— le manda la ficha completa, en
# el mismo orden siempre, y le pasa la conversación al bot de pedido. Aquí se llama SP06
# porque SP05 ya es nuestra orden al almacén. Diseño completo: docs/20-sp06-ficha.md.
#
#   [Trigger: Contact Changed → sku_elegido]   ← lo pone una persona en la UI
#     → If, una rama por SKU, y antes que todas «Sin paca»: sku_elegido vacío → no hace nada
#         (BOT-01 o la propia ficha lo vacían, y vaciar también dispara)
#     → rama «PV-MUJ-BOU»: If ficha_sku es PV-MUJ-BOU → no hace nada (ya vio esta ficha)
#         si no: Pausar bot → Apertura → [3 s] → Video → [3 s] → Precio → [3 s] → Pregunta final
#                → ficha_sku = PV-MUJ-BOU → vaciar sku_elegido → tag ficha-enviada
#                → Activar BOT-01 · Pedido
#
# POR QUÉ SE VACÍA sku_elegido. «Contact Info» del bot sólo llena campos vacíos. Si el campo
# se queda lleno, el bot no puede escribir otra paca cuando el cliente cambia de opinión, ni
# la clave al confirmar el pedido (que es lo que lee `AC01 · Apartar paca`). La memoria de
# qué ficha ya vio queda en ficha_sku.
#
# LA PREGUNTA FINAL PIDE EL CAMPO QUE LE FALTA AL PEDIDO. Es la regla de GALK: en talleres
# falta la sede, en software la modalidad. Aquí falta cuántas: `cantidad_elegida`. El nombre
# se pide en la apertura, igual que GALK, para que el cliente conteste los dos juntos.
#
# LAS FORMAS DE LOS NODOS SALEN DEL KIT (wf_toolkit.py, $GHL_KIT), validadas en producción en
# GALK: WhatsApp de texto, pausar/activar bot, espera, campo, vaciar campo, tag e If.
# ⚠️ La ÚNICA sin validar es WhatsApp con VIDEO: el kit probó imagen y PDF con la misma forma
# (media_type "image" | "document"); "video" es la apuesta. Por eso la primera corrida se
# prueba con un contacto de prueba antes de publicar (docs/20-sp06-ficha.md §5).
#
# ⚠️ LOS TEXTOS SON UN BORRADOR NUESTRO, no del cliente: Pamela tiene que aprobarlos.
#
# Uso (desde la raíz del repo):
#   python scripts/armar-sp06.py --dry-run                    resumen y validaciones del catálogo
#   python scripts/armar-sp06.py --fichas                     el texto de las 30 fichas
#   GHL_KIT=… python scripts/armar-sp06.py --construir        arma los nodos con el kit y valida el grafo,
#                                                             sin credenciales ni red
#   python scripts/armar-sp06.py --aplicar <carpeta-respaldo> [--reescribir]
#       escribe SP06 en BORRADOR y SIN trigger. Necesita en el entorno GHL_KIT, GHL_API_KEY,
#       GHL_LOCATION_ID, GHL_FIREBASE_REFRESH_TOKEN, SP06_WA_PHONE (el id del número de
#       WhatsApp, el `from_phone_number` de un nodo WhatsApp hecho en la UI) y SP06_BOT_PEDIDO
#       (el id del bot BOT-01 · Pedido). Lo corre Germán con `!`.
import csv
import importlib.util
import json
import os
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOGO = "data/catalogo.csv"
VIDEOS_JSON = pathlib.Path("data/videos-sp06.json")     # lo escribe subir-videos-sp06.py
NOMBRE = "SP06 · Ficha de la paca"
TAG = "ficha-enviada"
ESPERA_SEG = 3
MIN_MENSAJES, MAX_MENSAJES = 3, 7      # el rango real de GALK (no «6 a 8»)
LIMITE_VIDEO = 16 * 1024 * 1024        # WhatsApp no acepta videos más pesados

# Pacas en 0 por decisión del cliente al cargar el inventario (15 oct). Su rama no manda
# la ficha: avisa que por ahora no hay y vacía sku_elegido para que el bot ofrezca otra.
NO_DISPONIBLES = {"PV-PLA-EST", "PV-HOS-EST", "PI-CHA-BOU"}


def cargar_videos():
    """{sku: {"url", "nombre", "bytes"}}. Vacío hasta correr subir-videos-sp06.py: una paca
    sin video manda su ficha igual, con un mensaje menos."""
    if not VIDEOS_JSON.exists():
        return {}
    return json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))


def nombre_bonito(r):
    """«MUJER VERANO BOUTIQUE» → «Mujer Verano Boutique». En el chat, las mayúsculas gritan."""
    t = r["nombre_display"].title().replace(" De ", " de ")
    return t.replace("Corse", "Corsé")


def ficha(r, videos):
    """Los mensajes que ve el cliente, en orden: [(tipo, contenido)]."""
    nombre = nombre_bonito(r)
    calidad = "" if r["calidad"] == "Estándar" else f", calidad {r['calidad']}"
    contenido = r["contenido_resumen"][:1].lower() + r["contenido_resumen"][1:]
    video = videos.get(r["sku"])
    cierre = "\n\nTe comparto el video para que veas cómo viene 👇" if video else ""
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
    if video:
        mensajes.append(("video", video))
    mensajes += [("texto", precio), ("texto", pregunta)]
    return mensajes


def no_disponible(r):
    return [("texto", f"Por ahora no tenemos disponible la paca *{nombre_bonito(r)}*. "
                      f"¿Te muestro otra parecida? 😊")]


def validar(filas, ramas, videos):
    errores = []
    claves = [r["sku"] for r in filas]
    if len(set(claves)) != len(claves):
        errores.append("hay claves repetidas en el catálogo")
    # La condición es «contiene la clave». Si una clave contuviera a otra, se llevaría la
    # ficha equivocada (el problema de Supervisión/Melamina en GALK).
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
    for sku, v in videos.items():
        if sku not in claves:
            errores.append(f"video {v['nombre']}: la clave {sku} no está en el catálogo")
        if v["bytes"] > LIMITE_VIDEO:
            errores.append(f"{sku}: el video pesa {v['bytes'] / 2**20:.1f} MB; WhatsApp acepta 16")
        if not str(v.get("url", "")).startswith("https://"):
            errores.append(f"{sku}: el video no tiene URL del media store")
    return errores


# ── Construcción de los nodos con el kit ─────────────────────────────────────

def nodos_de_rama(tk, sku, mensajes, cfg, disponible):
    """nodos_def de la cadena de una rama: [(attrs, nombre, tipo, workflowsActionType)]."""
    vaciar_sku = (tk.n_vaciar_campos([{"id": cfg["id_sku"], "title": "SKU de interés",
                                       "dataType": "TEXT"}]),
                  "Vaciar sku_elegido", "update_contact_field", None)
    defs = []
    if disponible:
        defs.append((tk.n_ai_status_apagar(), "Pausar bot", "update_conversation_ai_status",
                     "INTERNAL"))
    for j, (tipo, contenido) in enumerate(mensajes):
        if j:
            defs.append((tk.n_wait_segundos(ESPERA_SEG), f"Espera {ESPERA_SEG} s", "wait", None))
        if tipo == "video":
            defs.append((tk.n_whatsapp_media(contenido["url"], contenido["nombre"],
                                             contenido["bytes"], cfg["wa"], media_type="video"),
                         f"Video {sku}", "whatsapp_media", "INTERNAL"))
        else:
            defs.append((tk.n_whatsapp_texto(contenido, cfg["wa"]),
                         f"Ficha {sku} · {j + 1}", "whatsapp_v2", "INTERNAL"))
    if not disponible:
        return defs + [vaciar_sku]
    return defs + [
        (tk.n_campo(cfg["id_ficha"], "Ficha enviada (clave)", sku),
         f"ficha_sku = {sku}", "update_contact_field", None),
        vaciar_sku,
        (tk.n_tag(TAG), f"Marcar {TAG}", "add_contact_tag", None),
        (tk.n_ai_status_activar(cfg["bot"]), "Activar BOT-01 · Pedido",
         "update_conversation_ai_status", "INTERNAL"),
    ]


def construir(tk, filas, ramas, cfg):
    """El workflow entero. Un If con «Sin paca» primero y una rama por SKU; dentro de cada
    rama disponible, un If anidado «ya vio esta ficha» que sale sin hacer nada."""
    def cond_sku(valor):
        if valor is None:
            return tk.cond_campo(cfg["id_sku"], None, "has_no_value")
        return tk.cond_campo(cfg["id_sku"], valor, "contains")

    defs_externas = [("Sin paca", None, [])]
    for r in filas:
        sku = r["sku"]
        cadena = [] if sku not in NO_DISPONIBLES else nodos_de_rama(tk, sku, ramas[sku], cfg, False)
        defs_externas.append((sku, sku, cadena))
    nodos = tk.if_ramas(defs_externas, [], cond=cond_sku)

    # If anidado en cada rama disponible: se cuelga por el `next` de la rama, sin `parent`
    # propio, y con `parentKey` = la rama (la regla de wf_toolkit, §2.8 del playbook).
    por_nombre = {n["name"]: n for n in nodos if n.get("nodeType") == "branch-yes"}
    for r in filas:
        sku = r["sku"]
        if sku in NO_DISPONIBLES:
            continue
        interno = tk.if_ramas(
            [("Ya vio esta ficha", sku, [])],
            nodos_de_rama(tk, sku, ramas[sku], cfg, True),
            cond=lambda v: tk.cond_campo(cfg["id_ficha"], v, "contains"))
        rama = por_nombre[sku]
        rama["next"] = interno[0]["id"]
        interno[0]["parentKey"] = rama["id"]
        nodos += interno
    return nodos


def cargar_kit():
    kit = os.environ.get("GHL_KIT")
    if not kit:
        sys.exit("Falta GHL_KIT: la ruta al ghl-kit (el que trae cli_anything/.../wf_toolkit.py).")
    sys.path.insert(0, kit)
    from cli_anything.gohighlevel.utils import wf_toolkit as tk
    return tk


def resumen_nodos(nodos):
    tipos = {}
    for n in nodos:
        tipos[n["type"]] = tipos.get(n["type"], 0) + 1
    return ", ".join(f"{v} {k}" for k, v in sorted(tipos.items(), key=lambda x: -x[1]))


# ── Escritura en la cuenta ───────────────────────────────────────────────────

def aplicar(tk, filas, ramas):
    pedidos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not pedidos:
        sys.exit("Falta la carpeta de respaldo: --aplicar <carpeta-respaldo>")
    respaldo = pathlib.Path(pedidos[0])
    faltan = [v for v in ("GHL_API_KEY", "GHL_LOCATION_ID", "GHL_FIREBASE_REFRESH_TOKEN",
                          "SP06_WA_PHONE", "SP06_BOT_PEDIDO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Faltan en el entorno: {', '.join(faltan)}")
    import requests

    loc = os.environ["GHL_LOCATION_ID"]
    H = {"Authorization": f"Bearer {os.environ['GHL_API_KEY']}", "Version": "2021-07-28",
         "Accept": "application/json"}
    r = requests.get(f"https://services.leadconnectorhq.com/locations/{loc}/customFields",
                     headers=H, params={"model": "contact"}, timeout=30)
    if not r.ok:
        sys.exit(f"No se pudieron leer los campos: {r.status_code} {r.text[:200]}")
    # Los custom fields se escriben y se comparan por ID, nunca por clave (CLAUDE.md).
    ids = {c.get("fieldKey"): c.get("id") for c in r.json().get("customFields", [])}
    cfg = {"id_sku": ids.get("contact.sku_elegido"), "id_ficha": ids.get("contact.ficha_sku"),
           "wa": os.environ["SP06_WA_PHONE"], "bot": os.environ["SP06_BOT_PEDIDO"]}
    if not cfg["id_sku"] or not cfg["id_ficha"]:
        sys.exit("Falta el campo sku_elegido o ficha_sku. Correr antes "
                 "scripts/crear-esqueleto-menudeo.py.")

    nodos = construir(tk, filas, ramas, cfg)
    problemas = tk.validar_grafo(nodos)
    if problemas:
        sys.exit("Grafo roto, no se escribe:\n  " + "\n  ".join(problemas))

    s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
    aw = importlib.util.module_from_spec(s)
    s.loader.exec_module(aw)
    C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), loc)

    wid = C.buscar(NOMBRE)
    if wid:
        vivos = C.nodos_vivos(wid)
        if vivos and "--reescribir" not in sys.argv:
            sys.exit(f"«{NOMBRE}» ya existe con {len(vivos)} nodos. Para reemplazarlo: --reescribir")
        respaldo.mkdir(parents=True, exist_ok=True)
        (respaldo / "sp06-antes.json").write_text(json.dumps(vivos, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
        print(f"respaldo: {len(vivos)} nodos → {respaldo / 'sp06-antes.json'}")
    else:
        wid = C.crear(NOMBRE)
        print(f"creado «{NOMBRE}»: {wid}")

    # La etiqueta tiene que existir antes, o el nodo queda con aviso de error (CLAUDE.md).
    C.crear_etiqueta(TAG)

    # PUT propio y no Interna.escribir(): ése copia allowMultiple del vivo, y un workflow
    # recién creado lo trae apagado. Sin «Allow re-entry», un cliente recibe UNA ficha en
    # su vida. Se relee la versión justo antes (es control de concurrencia).
    d = C.leer(wid)
    r = requests.put(f"{aw.BASE}/workflow/{loc}/{wid}", headers=C.H, timeout=60,
                     json={"name": d.get("name"), "version": d.get("version"),
                           "parentId": d.get("parentId"), "status": "draft",
                           "allowMultiple": True, "allowMultipleOpportunity": False,
                           "stopOnResponse": False, "workflowData": {"templates": nodos}})
    if not r.ok:
        j = C._j(r)
        sys.exit(f"El PUT falló: {j.get('errorMessage') or j.get('msg') or r.text[:300]}")

    vivos = C.nodos_vivos(wid)
    d = C.leer(wid)
    print(f"escrito: {len(vivos)} de {len(nodos)} nodos · allowMultiple={d.get('allowMultiple')} "
          f"· status={d.get('status')}")
    if len(vivos) != len(nodos):
        sys.exit("⚠️ La cuenta no guardó todos los nodos: revisar antes de seguir.")
    print("\nFalta, en la UI y en este orden:")
    print("  1. Trigger «Contact Changed» → sku_elegido, y pulsar «Guardar trigger».")
    print("  2. Probar con un contacto de prueba (Add to workflow) ANTES de publicar:")
    print("     que lleguen texto, video y pregunta, y que se activen bot, tag y ficha_sku.")
    print("  3. Publicar con el toggle de la UI. Por API es ruleta.")


def main():
    with open(CATALOGO, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    videos = cargar_videos()
    ramas = {r["sku"]: (no_disponible(r) if r["sku"] in NO_DISPONIBLES else ficha(r, videos))
             for r in filas}

    print(f"{NOMBRE} — {len(ramas)} ramas desde {CATALOGO}\n")
    for r in filas:
        m = ramas[r["sku"]]
        if r["sku"] in NO_DISPONIBLES:
            forma = "no disponible: 1 aviso, el bot sigue"
        else:
            forma = " → ".join("video" if t == "video" else "texto" for t, _ in m)
            forma = f"{len(m)} mensajes ({forma})"
        print(f"  {r['sku']:<11} {nombre_bonito(r):<26} ${int(r['precio_mxn']):>6,}  {forma}")
    disponibles = len(ramas) - len(NO_DISPONIBLES)
    con_video = sum(1 for s in videos if s in ramas and s not in NO_DISPONIBLES)
    print(f"\n  videos: {con_video} de {disponibles} pacas disponibles"
          + ("" if videos else f" (falta correr subir-videos-sp06.py: {VIDEOS_JSON} no existe)"))

    if "--fichas" in sys.argv:
        for r in filas:
            print(f"\n{'─' * 72}\n{r['sku']} · {nombre_bonito(r)}\n{'─' * 72}")
            for i, (tipo, contenido) in enumerate(ramas[r["sku"]], 1):
                if tipo == "video":
                    print(f"[{i}] (video {contenido['nombre']})")
                else:
                    print(f"[{i}] {contenido}\n")

    errores = validar(filas, ramas, videos)
    print()
    if errores:
        for e in errores:
            print(f"✗ {e}")
        sys.exit(1)
    print("✓ claves sin colisión, catálogo completo, 3 a 7 mensajes por ficha, sin «económica»")

    if "--construir" in sys.argv or "--aplicar" in sys.argv:
        tk = cargar_kit()
        if "--aplicar" in sys.argv:
            aplicar(tk, filas, ramas)
            return
        cfg = {"id_sku": "ID_SKU_ELEGIDO", "id_ficha": "ID_FICHA_SKU",
               "wa": "ID_NUMERO_WHATSAPP", "bot": "ID_BOT_PEDIDO"}
        nodos = construir(tk, filas, ramas, cfg)
        problemas = tk.validar_grafo(nodos)
        print(f"\n{len(nodos)} nodos: {resumen_nodos(nodos)}")
        if problemas:
            for p in problemas:
                print(f"✗ {p}")
            sys.exit(1)
        print("✓ grafo válido (wf_toolkit.validar_grafo). Con IDs de mentira: no se escribió nada.")
        return
    print("\nPara armar los nodos: --construir. Para escribir en la cuenta: --aplicar.")


if __name__ == "__main__":
    main()
