# AP04 · Envío despachado — lo dispara el formulario «Registrar Envío», que llena depósito
# cuando saca la guía a mano en Paquete Express (decisión del cliente, 11 oct).
#
#   [Trigger: Form Submitted → «Registrar Envío»]        ← lo conecta Germán en la UI
#     → Find opportunity (SP · Menudeo / «Orden en Almacén» / open / la más reciente)
#         ├─ Opportunity Found → mover a «Enviado — Guía Generada» → TEMPORAL · SMS con la liga
#         └─ Opportunity Not Found → correo a los dueños
#
# Todos los nodos se CLONAN de los que ya viven en la cuenta, en vez de armarse a mano: el
# Find opportunity de SP04 (configurado en la UI el 2 oct), el «Mover a …» de SP05, el correo de
# AP02 y el SMS de AP01. Así la forma es una que la cuenta ya aceptó, y no hace falta el kit.
# Lo único que se les cambia son los ids de etapa y los textos.
#
# Lo que queda para la UI, porque sus moldes no existen en el repo:
#   1. El trigger Form Submitted (una condición de trigger mal formada se guarda, sale en
#      blanco y no se ve por API).
#   2. En el nodo «Mover a Enviado», escribir numero_guia, track_url y fecha_envio con los
#      campos del formulario — el token con que un workflow lee un campo de formulario es el
#      mismo hueco que tiene AP03 con orden_id.
#   3. Un nodo Email al cliente con la liga (el tipo `email` está aceptado, pero nunca se usó).
#
# Un trigger de formulario NO trae oportunidad: sin el Find opportunity, «Update opportunity»
# no hace nada y no da error (le pasó a SP04 y AP03 hasta el 2 oct). Y mover a «Enviado» es lo
# que enciende el rastreo: el cron de N5 sólo busca en esa etapa.
#
# Se corre una vez. Guarda los moldes leídos y el resultado en la carpeta de respaldo.
# Uso (desde la raíz del repo): python scripts/armar-ap04.py <carpeta-respaldo> [--dry-run]
import importlib.util, os, json, sys, uuid, copy
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # la consola de Windows (cp1252) se ahoga con «→» y «⚠️»
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
dry = "--dry-run" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.exit("uso: python scripts/armar-ap04.py <carpeta-respaldo> [--dry-run]")
os.makedirs(args[0], exist_ok=True)
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])
NOMBRE = "AP04 · Envío despachado"
U = lambda: str(uuid.uuid4())


def reemplazar(obj, viejo, nuevo):
    """Cambia un id de etapa donde aparezca, sin suponer dónde lo guarda el nodo."""
    if isinstance(obj, dict):
        return {k: reemplazar(v, viejo, nuevo) for k, v in obj.items()}
    if isinstance(obj, list):
        return [reemplazar(v, viejo, nuevo) for v in obj]
    return nuevo if obj == viejo else obj


def molde(workflow, tipo, nombre=None):
    nodos = C.nodos_vivos(C.buscar(workflow))
    c = [n for n in nodos if n["type"] == tipo and (nombre is None or n["name"] == nombre)]
    assert c, f"{workflow} no tiene un nodo {tipo}" + (f" «{nombre}»" if nombre else "")
    n = copy.deepcopy(c[0])
    for k in ("next", "parent", "parentKey", "order", "sibling"):
        n.pop(k, None)
    n["id"] = U()
    return n


# ── moldes vivos
# El Find opportunity de SP04 lo configuró Germán en la UI: pipeline SP · Menudeo, etapa «Liga
# de Pago Enviada», status open, la más reciente. Aquí la etapa es «Orden en Almacén».
find = reemplazar(molde("SP04 · Pago confirmado", "find_opportunity"), aw.ETAPA["liga"], aw.ETAPA["almacen"])
assert aw.ETAPA["almacen"] in json.dumps(find), \
    "el Find opportunity de SP04 no filtra por la etapa «Liga de Pago Enviada»; revisar su forma antes de seguir"
mover = reemplazar(molde("SP05 · Despacho", "internal_update_opportunity"), aw.ETAPA["almacen"], aw.ETAPA["enviado"])
assert aw.ETAPA["enviado"] in json.dumps(mover), "el «Mover a …» de SP05 no apunta a «Orden en Almacén»"
aviso = molde("AP02 · Escalamiento a humano", "internal_notification")
sms = molde("AP01 · Rastreo", "sms")
json.dump({"find": find, "mover": mover, "aviso": aviso, "sms": sms},
          open(os.path.join(args[0], "moldes-leidos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── textos
mover["name"] = "Mover a Enviado — Guía Generada"
sms["name"] = f"{aw.TEMP} · Pedido en camino con liga"
sms["attributes"]["body"] = ("[TEMPORAL] ¡Tu paca ya va en camino! Guía: {{opportunity.numero_guia}} · "
                             "Paquete Express. Síguela aquí: {{opportunity.track_url}}")
aviso["name"] = "Avisar: envío registrado sin pedido en almacén"
aviso["attributes"]["email"]["subject"] = "Envío registrado sin pedido en almacén — {{contact.first_name}} {{contact.last_name}}"
aviso["attributes"]["email"]["html"] = (
    "<p>Depósito registró un envío y no hay pedido de ese cliente en «Orden en Almacén».</p>"
    "<p>Cliente: <b>{{contact.first_name}} {{contact.last_name}}</b> · {{contact.phone}} · {{contact.email}}</p>"
    "<p>Lo más probable: el teléfono del formulario no es el del comprador, o el pedido ya se había "
    "movido. Revisen la tarjeta antes de volver a registrarlo.</p>")

# ── grafo: find → [found, notfound]; found → mover → sms; notfound → aviso
tf, tn = U(), U()
tr = lambda tid, n: {"id": tid, "name": n, "fields": [], "meta": {"__branchKey__": f"predefined_{n}"},
                     "conditionType": "pre-defined"}
find["parentKey"] = None
find["attributes"]["transitions"] = [tr(tf, "Opportunity Found"), tr(tn, "Opportunity Not Found")]
find["next"] = [tf, tn]
find["name"] = "Buscar el pedido en almacén"
found = {"id": tf, "parentKey": find["id"], "parent": find["id"], "type": "transition",
         "name": "Opportunity Found", "attributes": {}, "cat": "transition", "next": mover["id"]}
notfound = {"id": tn, "parentKey": find["id"], "parent": find["id"], "type": "transition",
            "name": "Opportunity Not Found", "attributes": {}, "cat": "transition", "next": aviso["id"]}
mover["parentKey"] = tf; mover["next"] = sms["id"]
sms["parentKey"] = mover["id"]
aviso["parentKey"] = tn
out = [find, found, notfound, mover, sms, aviso]
for k, n in enumerate(out):
    n["order"] = k

print(f"\n{NOMBRE} quedaría así:")
for n in out:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
if dry:
    print("\n--dry-run: no se escribió nada. Moldes leídos en", os.path.join(args[0], "moldes-leidos.json"))
    sys.exit(0)

wid = C.buscar(NOMBRE)
if wid and C.nodos_vivos(wid):
    sys.exit(f"{NOMBRE} ya existe con nodos (wid={wid}). Este script se corre una vez.")
wid = wid or C.crear(NOMBRE)
ok, msg = C.escribir(wid, out)          # nace con status null; escribir() lo deja en draft
print("\nPUT", "ok" if ok else "RECHAZADO: " + msg)
v2 = C.nodos_vivos(wid)
json.dump(v2, open(os.path.join(args[0], "AP04.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(out), "enviados,", len(v2), "vivos | status:", C.leer(wid).get("status"), "| wid:", wid)
for n in v2:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
print("""
Falta en la UI (Germán):
  1. Trigger «Form Submitted» → formulario «Registrar Envío», enganchado al nodo «Buscar el pedido en almacén».
     ⚠️ Crear el trigger PUBLICA el workflow. Dejarlo en borrador hasta probarlo.
  2. En «Mover a Enviado — Guía Generada», agregar los campos de OPORTUNIDAD (no los gemelos de contacto):
       numero_guia ← número de guía del formulario · track_url ← liga del formulario
       fecha_envio ← {{right_now.little_endian_date}}
  3. Después del SMS, un nodo Email al cliente con {{opportunity.track_url}} (hoy el canal que sí llega).
  4. Prender «Allow re-entry» en Settings: un cliente despacha más de una vez en su vida.
""")
