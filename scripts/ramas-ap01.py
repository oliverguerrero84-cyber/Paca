# AP01: ramas por inboundWebhookRequest.estado. Molde leído del If armado en la UI el 2 oct.
#   en_sucursal          → SMS «llegó a la sucursal» (datos del webhook, no de la oportunidad)
#   incidencia/cancelado → tag escalar-humano (dispara AP02)
#   entregado / otro     → nada: N5 ya cierra la oportunidad como won
# Uso (desde la raíz del repo): python ap01_ramas.py <respaldo.json>
import importlib.util, os, json, sys, uuid, copy
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])
WID = "4f84c3b9-4aa9-44fa-af3f-f7d25958dec4"
vivos = C.nodos_vivos(WID)
por = {(n["type"], n["name"]): n for n in vivos}
assert ("find_contact", "Find contact") in por and len(vivos) == 8, f"AP01 cambió ({len(vivos)} nodos)"
json.dump(vivos, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
print("respaldo:", sys.argv[1])
U = lambda: str(uuid.uuid4())

find = por[("find_contact", "Find contact")]
found = por[("transition", "Contact found")]
nfound = por[("transition", "Contact not found")]
viejo_if = next(n for n in vivos if n.get("nodeType") == "condition-node")
cond0 = viejo_if["attributes"]["branches"][0]["segments"][0]["conditions"][0]
sms = copy.deepcopy(next(n for n in vivos if n["type"] == "sms"))

RAMAS = [("En sucursal", "en_sucursal"), ("Incidencia", "incidencia"), ("Cancelado", "cancelado")]
i, no = U(), U()
ids = [U() for _ in RAMAS]
todas = ids + [no]
branches = []
for (nombre, valor), bid in zip(RAMAS, ids):
    c = copy.deepcopy(cond0); c["conditionValue"] = valor; c["__conditionId"] = U()
    branches.append({"id": bid, "name": nombre, "operator": "and",
                     "segments": [{"__segmentId": U(), "operator": "and", "conditions": [c]}]})
iff = copy.deepcopy(viejo_if)
iff.update({"id": i, "parent": found["id"], "parentKey": found["id"], "name": "¿Qué pasó con el paquete?",
            "next": todas})
iff["attributes"]["branches"] = branches
iff["attributes"]["conditionName"] = "¿Qué pasó con el paquete?"
found = {**found, "next": i}

out = [find, found, nfound, iff]
rama = {}
for (nombre, _), bid in zip(RAMAS, ids):
    rama[bid] = {"id": bid, "parent": i, "parentKey": i, "type": "if_else", "name": nombre, "cat": "conditions",
                 "nodeType": "branch-yes", "comments": [], "sibling": [x for x in todas if x != bid],
                 "attributes": {"if": False, "conditionName": "¿Qué pasó con el paquete?", "operator": "and",
                                "branches": []}}
    out.append(rama[bid])
out.append({"id": no, "parent": i, "parentKey": i, "type": "if_else", "name": "None", "cat": "conditions",
            "nodeType": "branch-no", "comments": [], "sibling": ids, "attributes": {"else": True}})

# en_sucursal → SMS con los datos del webhook
sms.update({"id": U(), "parentKey": ids[0]}); sms.pop("next", None); sms.pop("parent", None)
sms["attributes"]["body"] = ("[TEMPORAL] Tu paca ya llegó a la sucursal y está lista para recoger. "
                             "Guía: {{inboundWebhookRequest.numero_guia}}. Síguela aquí: "
                             "{{inboundWebhookRequest.track_url}}. Llévate una identificación.")
rama[ids[0]]["next"] = sms["id"]; out.append(sms)
# incidencia y cancelado → tag escalar-humano (forma copiada de «Marcar vencido» de SP02)
for bid in ids[1:]:
    tag = {"id": U(), "parentKey": bid, "type": "add_contact_tag", "name": "Escalar a humano",
           "attributes": {"tags": ["escalar-humano"]}}
    rama[bid]["next"] = tag["id"]
    out.append(tag)
for k, n in enumerate(out):
    n["order"] = k

ok, msg = C.escribir(WID, out)
print("PUT", "ok" if ok else "RECHAZADO: " + msg)
v2 = C.nodos_vivos(WID)
print(len(out), "enviados,", len(v2), "vivos | status:", C.leer(WID).get("status"))
for n in v2:
    print(f'  {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
