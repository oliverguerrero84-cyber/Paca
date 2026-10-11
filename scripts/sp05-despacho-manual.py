# SP05 pasa a despacho manual (decisión del cliente, 11 oct): la guía ya no la genera N4,
# la saca depósito a mano en Paquete Express y la registra en el formulario «Registrar Envío»
# (AP04). Con N4 apagado, el SP05 de hoy mandaría a TODOS los pedidos por la rama
# «Sin guía» y los escalaría a humano.
#
# Queda en línea recta, sin ramas:
#   correo a los dueños con lo que depósito necesita (destino, mapa, cantidad; sin monto)
#   → mover a «Orden en Almacén»
#
# Se quitan: el webhook a N4, la espera, el Find opportunity, el If y sus dos ramas, el tag
# «escalar-humano» y el SMS «Orden enviada» (ese aviso lo manda AP04 cuando sí hay guía).
# El SMS al almacén que pedía el plan no existe como nodo: un nodo SMS le escribe al
# contacto del workflow, no a un número ajeno. Lo que depósito necesita va en el correo.
#
# Se corre una vez: verifica que SP05 tenga la forma de las ramas del 2 oct y guarda respaldo.
# ⚠️ escribir() lo baja a borrador. Hay que volver a publicarlo en la UI, y lo imprime al final.
# Uso (desde la raíz del repo): python scripts/sp05-despacho-manual.py <respaldo.json> [--dry-run]
import importlib.util, os, json, sys, copy
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # la consola de Windows (cp1252) se ahoga con «→» y «⚠️»
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
dry = "--dry-run" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.exit("uso: python scripts/sp05-despacho-manual.py <respaldo.json> [--dry-run]")
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])
wid = C.buscar("SP05 · Despacho")
vivos = C.nodos_vivos(wid)
tipos = sorted(n["type"] for n in vivos)
ESPERADOS = sorted(["webhook", "wait", "find_opportunity", "transition", "transition", "if_else", "if_else",
                    "if_else", "add_contact_tag", "internal_notification", "sms", "internal_update_opportunity"])
assert tipos == ESPERADOS, f"SP05 ya no tiene la forma del 2 oct (wid={wid}): {tipos}"
json.dump(vivos, open(args[0], "w", encoding="utf-8"), ensure_ascii=False)
print("respaldo:", args[0])
por_tipo = {n["type"]: n for n in vivos}

# Al almacén nunca le va el monto (textual de Miguel: «ellos no tienen por qué enterarse»).
# Este correo es lo que los dueños le pasan a depósito, así que tampoco lo lleva.
ASUNTO = "Pedido pagado, listo para despachar — {{opportunity.articulo_apartado}}"
HTML = ("<p>Orden: <b>{{opportunity.orden_id}}</b></p>"
        "<p>Cliente: {{contact.first_name}} {{contact.last_name}} · {{contact.phone}}</p>"
        "<p>Artículo: {{opportunity.articulo_apartado}} · Cantidad: {{opportunity.cantidad_apartada}}</p>"
        "<p>Modalidad: <b>{{opportunity.modalidad_envio}}</b></p>"
        "<p>Sucursal: {{opportunity.sucursal_envio}} ({{opportunity.branch_code_envio}})</p>"
        "<p>Domicilio: {{opportunity.direccion_envio}}</p>"
        "<p>Mapa: {{opportunity.mapa_envio}}</p>"
        "<p>CP {{contact.codigo_postal}} · {{contact.ciudad}}, {{contact.estado_mx}}</p>"
        "<p>Cuando salga la guía en Paquete Express, regístrenla en el formulario "
        "«Registrar Envío»: eso mueve el pedido a «Enviado» y le manda la liga al cliente.</p>")

correo = copy.deepcopy(por_tipo["internal_notification"])
for k in ("next", "parent"):
    correo.pop(k, None)
correo["parentKey"] = None
correo["name"] = "Correo a los dueños · listo para despachar"
correo["attributes"]["email"]["subject"] = ASUNTO
correo["attributes"]["email"]["html"] = HTML

mover = copy.deepcopy(por_tipo["internal_update_opportunity"])
for k in ("next", "parent"):
    mover.pop(k, None)
mover["parentKey"] = correo["id"]
correo["next"] = mover["id"]

out = [correo, mover]
for k, n in enumerate(out):
    n["order"] = k

print("\nSP05 quedaría así:")
for n in out:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
if dry:
    print("\n--dry-run: no se escribió nada")
    sys.exit(0)

ok, msg = C.escribir(wid, out)
print("\nPUT", "ok" if ok else "RECHAZADO: " + msg)
v2 = C.nodos_vivos(wid)
estado = C.leer(wid).get("status")
print(len(out), "enviados,", len(v2), "vivos | status:", estado)
for n in v2:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
if ok and estado != "published":
    print("\n⚠️ SP05 quedó en", estado, "— escribir() lo baja a borrador. Publicarlo en la UI, "
          "y prenderle «Allow multiple opportunities» (quedó en false sólo en él).")
