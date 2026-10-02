# SP02: inserta Find opportunity + If sobre opportunity.estado_apartado tras cada espera.
# Molde leído de «PRUEBA N1» el 2 oct (hecho a mano por Germán en la UI).
# Uso: python sp02_if.py <ruta-respaldo.json>   (correr desde la raíz del repo)
import importlib.util, os, json, sys, uuid, copy
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
ESTADO = "nvxnGXleQU26J2gkzabB"   # opportunity.estado_apartado
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])
wid = C.buscar("SP02 · Apartado 24 h")
vivos = {n["name"]: n for n in C.nodos_vivos(wid)}
assert len(vivos) == 8 and not any(n["type"] == "if_else" for n in vivos.values()), f"SP02 ya no es la cadena recta (wid={wid}, {len(vivos)} nodos leídos)"
json.dump(list(vivos.values()), open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)  # respaldo
print("respaldo:", sys.argv[1])
U = lambda: str(uuid.uuid4())
out = []


def accion(nombre, padre):
    n = copy.deepcopy(vivos[nombre]); n.pop("next", None); n.pop("parent", None); n["parentKey"] = padre
    out.append(n); return n


def enlazar(a, b):
    a["next"] = b["id"]


def chequeo(padre, valor, nombre):
    """Find opportunity → Found → If(estado == valor). Devuelve (find, rama_si, rama_no)."""
    f, tf, tn, i, si, no = U(), U(), U(), U(), U(), U()
    tr = lambda tid, n: {"id": tid, "name": n, "fields": [], "meta": {"__branchKey__": f"predefined_{n}"},
                         "conditionType": "pre-defined"}
    find = {"id": f, "parentKey": padre, "type": "find_opportunity", "name": f"Buscar oportunidad · {nombre}",
            "attributes": {"sorting": "latest", "type": "find_opportunity", "__customInputs__": {},
                           "cat": "multi-path", "convertToMultipath": True,
                           "transitions": [tr(tf, "Opportunity Found"), tr(tn, "Opportunity Not Found")],
                           "__name__": "Find opportunity", "__customInputFields__": []},
            "cat": "multi-path", "workflowsActionType": "INTERNAL", "next": [tf, tn]}
    found = {"id": tf, "parentKey": f, "parent": f, "type": "transition", "name": "Opportunity Found",
             "attributes": {}, "cat": "transition", "next": i}
    nfound = {"id": tn, "parentKey": f, "parent": f, "type": "transition", "name": "Opportunity Not Found",
              "attributes": {}, "cat": "transition"}
    cond = {"conditionType": "opportunities", "conditionSubType": ESTADO, "conditionOperator": "==",
            "conditionValue": valor, "__conditionId": U(), "ifElseNodeId": "",
            "__customFieldType__": "standard", "isWait": False}
    iff = {"id": i, "parent": tf, "parentKey": tf, "type": "if_else", "name": nombre, "cat": "conditions",
           "nodeType": "condition-node", "comments": [],
           "attributes": {"currentRecipeType": "CUSTOM",
                          "branches": [{"id": si, "name": f"Ya {valor}", "operator": "and",
                                        "segments": [{"__segmentId": U(), "operator": "and", "conditions": [cond]}]}],
                          "operator": "and", "if": True, "conditionName": nombre, "version": 2,
                          "noneBranchName": "No"},
           "next": [si, no]}
    bsi = {"id": si, "parent": i, "parentKey": i, "type": "if_else", "name": f"Ya {valor}", "cat": "conditions",
           "nodeType": "branch-yes", "comments": [], "sibling": [no],
           "attributes": {"if": False, "conditionName": nombre, "operator": "and", "branches": []}}
    bno = {"id": no, "parent": i, "parentKey": i, "type": "if_else", "name": "No", "cat": "conditions",
           "nodeType": "branch-no", "comments": [], "sibling": [si], "attributes": {"else": True}}
    out.extend([find, found, nfound, iff, bsi, bno])
    return find, bsi, bno


N = lambda k: next(x for x in vivos if k in x)
t = accion(N("rminos"), None)
w = accion(N("12 h"), t["id"]); enlazar(t, w)
f, si, no = chequeo(w["id"], "pagado", "¿Ya pagó? (12 h)"); enlazar(w, f)
r = accion(N("· Recordatorio"), no["id"]); enlazar(no, r)
w = accion(N("10 h"), r["id"]); enlazar(r, w)
f, si, no = chequeo(w["id"], "pagado", "¿Ya pagó? (22 h)"); enlazar(w, f)
r = accion(N("Recordatorio final"), no["id"]); enlazar(no, r)
w = accion(N("2 h 20"), r["id"]); enlazar(r, w)
f, si, no = chequeo(w["id"], "vencido", "¿Venció?"); enlazar(w, f)
tag = accion(N("Marcar vencido"), si["id"]); enlazar(si, tag)
v = accion(N("Apartado vencido"), tag["id"]); enlazar(tag, v)
for k, n in enumerate(out):
    n["order"] = k

ok, msg = C.escribir(wid, out)
print("PUT", "ok" if ok else "RECHAZADO: " + msg)
vivos2 = C.nodos_vivos(wid)
print(len(out), "enviados,", len(vivos2), "vivos | status:", C.leer(wid).get("status"))
for n in vivos2:
    print(f'  {n["type"]:<28} {n["name"]}  <- {n.get("parentKey")}')
