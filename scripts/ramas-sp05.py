# SP05: tras la espera, Find opportunity → If(opportunity.etiqueta_pdf está vacío).
#   vacío (N4 falló)   → tag escalar-humano
#   con guía (None)    → correo a los dueños → SMS al cliente → mover a «Orden en Almacén»
# Molde del «está vacío» leído de la UI el 2 oct: conditionOperator "has_no_value", sin valor.
# Se corre una vez: verifica que SP05 sea la cadena recta de 5 nodos y guarda respaldo.
# Uso (desde la raíz del repo): python scripts/ramas-sp05.py <respaldo.json>
import importlib.util, os, json, sys, uuid, copy
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
ETIQUETA = "7m56gfUWz6dNlIs0ah8H"   # opportunity.etiqueta_pdf (no el de contacto, IWX1twUZyGC3I5FKCtJ4)
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])
wid = C.buscar("SP05 · Despacho")
vivos = {n["type"]: n for n in C.nodos_vivos(wid)}
assert sorted(vivos) == sorted(["webhook", "wait", "internal_notification", "sms", "internal_update_opportunity"]) \
    and len(C.nodos_vivos(wid)) == 5, f"SP05 ya no es la cadena recta (wid={wid}, {list(vivos)})"
json.dump(list(vivos.values()), open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
print("respaldo:", sys.argv[1])
U = lambda: str(uuid.uuid4())
out = []


def accion(tipo, padre):
    n = copy.deepcopy(vivos[tipo]); n.pop("next", None); n.pop("parent", None); n["parentKey"] = padre
    out.append(n); return n


wh = accion("webhook", None)
w = accion("wait", wh["id"]); wh["next"] = w["id"]

f, tf, tn, i, si, no = U(), U(), U(), U(), U(), U()
tr = lambda tid, n: {"id": tid, "name": n, "fields": [], "meta": {"__branchKey__": f"predefined_{n}"},
                     "conditionType": "pre-defined"}
out += [
    {"id": f, "parentKey": w["id"], "type": "find_opportunity", "name": "Buscar oportunidad del pedido",
     "attributes": {"sorting": "latest", "type": "find_opportunity", "__customInputs__": {}, "cat": "multi-path",
                    "convertToMultipath": True, "transitions": [tr(tf, "Opportunity Found"), tr(tn, "Opportunity Not Found")],
                    "__name__": "Find opportunity", "__customInputFields__": []},
     "cat": "multi-path", "workflowsActionType": "INTERNAL", "next": [tf, tn]},
    {"id": tf, "parentKey": f, "parent": f, "type": "transition", "name": "Opportunity Found",
     "attributes": {}, "cat": "transition", "next": i},
    {"id": tn, "parentKey": f, "parent": f, "type": "transition", "name": "Opportunity Not Found",
     "attributes": {}, "cat": "transition"},
    {"id": i, "parent": tf, "parentKey": tf, "type": "if_else", "name": "¿N4 escribió la guía?", "cat": "conditions",
     "nodeType": "condition-node", "comments": [], "next": [si, no],
     "attributes": {"currentRecipeType": "CUSTOM", "operator": "and", "if": True, "version": 2,
                    "conditionName": "¿N4 escribió la guía?", "noneBranchName": "Con guía",
                    "branches": [{"id": si, "name": "Sin guía", "operator": "and", "segments": [
                        {"__segmentId": U(), "operator": "and", "conditions": [
                            {"conditionType": "opportunities", "conditionSubType": ETIQUETA,
                             "conditionOperator": "has_no_value", "conditionValue": None, "__conditionId": U(),
                             "ifElseNodeId": "", "__customFieldType__": "standard", "isWait": False}]}]}]}},
    {"id": si, "parent": i, "parentKey": i, "type": "if_else", "name": "Sin guía", "cat": "conditions",
     "nodeType": "branch-yes", "comments": [], "sibling": [no],
     "attributes": {"if": False, "conditionName": "¿N4 escribió la guía?", "operator": "and", "branches": []}},
    {"id": no, "parent": i, "parentKey": i, "type": "if_else", "name": "Con guía", "cat": "conditions",
     "nodeType": "branch-no", "comments": [], "sibling": [si], "attributes": {"else": True}},
]
w["next"] = f
rama_si = next(n for n in out if n["id"] == si)
rama_no = next(n for n in out if n["id"] == no)

tag = {"id": U(), "parentKey": si, "type": "add_contact_tag", "name": "N4 falló · escalar a humano",
       "attributes": {"tags": ["escalar-humano"]}}
rama_si["next"] = tag["id"]; out.append(tag)

correo = accion("internal_notification", no); rama_no["next"] = correo["id"]
sms = accion("sms", correo["id"]); correo["next"] = sms["id"]
mover = accion("internal_update_opportunity", sms["id"]); sms["next"] = mover["id"]
for k, n in enumerate(out):
    n["order"] = k

ok, msg = C.escribir(wid, out)
print("PUT", "ok" if ok else "RECHAZADO: " + msg)
v2 = C.nodos_vivos(wid)
print(len(out), "enviados,", len(v2), "vivos | status:", C.leer(wid).get("status"))
for n in v2:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
