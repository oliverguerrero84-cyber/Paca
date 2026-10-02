# SP04 y AP03: aviso a los dueños en la rama «Opportunity Not Found».
# Pasa cuando el pago llega y el pedido ya no está abierto en «Liga de Pago Enviada»: lo más
# probable, que N2 lo venció (abandoned) y devolvió la paca al stock. Sin esto, el cobro entra
# y nadie se entera. Copia los destinatarios y el remitente del aviso de AP02.
# Se corre una vez: verifica que la rama esté vacía y guarda respaldo.
# Uso (desde la raíz del repo): python scripts/aviso-pago-sin-pedido.py <carpeta-respaldo>
import importlib.util, os, json, sys, uuid, copy
s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
aw = importlib.util.module_from_spec(s); s.loader.exec_module(aw)
C = aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]), os.environ["GHL_LOCATION_ID"])

molde = C.nodos_vivos(C.buscar("AP02 · Escalamiento a humano"))
molde = next(n for n in molde if n["type"] == "internal_notification")["attributes"]

CLIENTE = ("<p>Cliente: <b>{{contact.first_name}} {{contact.last_name}}</b> · {{contact.phone}} · "
           "{{contact.email}}</p>")
QUE_HACER = ("<p>No encontramos su pedido abierto en «Liga de Pago Enviada». Lo más probable es que el "
             "apartado ya hubiera vencido y la paca volviera al stock.</p>"
             "<p>Revisen si todavía hay pieza para entregarle o si hay que devolverle el dinero.</p>")
AVISOS = {
    "SP04 · Pago confirmado": (
        "Pago recibido sin pedido abierto — {{contact.first_name}} {{contact.last_name}}",
        "<p>Llegó un pago y no hay pedido que marcar como pagado.</p>" + CLIENTE +
        "<p>Factura: {{payment.invoice.number}}</p>" + QUE_HACER),
    "AP03 · Pago manual por transferencia": (
        "Transferencia registrada sin pedido abierto — {{contact.first_name}} {{contact.last_name}}",
        "<p>Se registró una transferencia y no hay pedido que marcar como pagado.</p>" + CLIENTE + QUE_HACER),
}

os.makedirs(sys.argv[1], exist_ok=True)
for nombre, (asunto, html) in AVISOS.items():
    wid = C.buscar(nombre)
    vivos = C.nodos_vivos(wid)
    nf = [n for n in vivos if n["type"] == "transition" and n["name"] == "Opportunity Not Found"]
    assert len(nf) == 1 and not nf[0].get("next"), f"{nombre}: la rama Not Found no está vacía o no existe"
    json.dump(vivos, open(os.path.join(sys.argv[1], f"{nombre[:4]}.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    attrs = copy.deepcopy(molde)
    attrs["email"]["subject"] = asunto
    attrs["email"]["html"] = html
    nodo = {"id": str(uuid.uuid4()), "parentKey": nf[0]["id"], "type": "internal_notification",
            "name": "Avisar: pago sin pedido abierto", "attributes": attrs, "order": len(vivos)}
    nf[0]["next"] = nodo["id"]
    ok, msg = C.escribir(wid, vivos + [nodo])
    v2 = C.nodos_vivos(wid)
    print(f"{nombre}: PUT {'ok' if ok else 'RECHAZADO: ' + msg} · {len(v2)} nodos · {C.leer(wid).get('status')}")
    for n in v2:
        print(f'    {n["type"]:<28} {n["name"]}  <- {str(n.get("parentKey"))[:8]}')
