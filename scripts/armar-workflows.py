#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma los workflows de GHL por la API interna, que es la única que los crea.

Uso:
    GHL_KIT=/ruta/al/ghl-kit  GHL_FIREBASE_REFRESH_TOKEN=AMf-...  \
    GHL_API_KEY=pit-...  GHL_LOCATION_ID=c9jj... \
        python scripts/armar-workflows.py [LS01 SP02 ...|todos] [--aplicar]

Sin `--aplicar` sólo imprime el árbol y valida el grafo: no escribe nada.

Lo que costó averiguar, y por qué el script es así (1 oct 2026):

* **La API pública NO crea workflows** — `GET /workflows/` sólo lista. Única vía: la
  interna, `backend.leadconnectorhq.com`, cabecera `token-id`.
* **El token de la extensión no autentica.** Empieza con `AMf-`: es un *refresh token*.
  Se canjea por un JWT (`eyJ…`, una hora) contra `securetoken.googleapis.com`.
* **El `version` es control de concurrencia.** Hay que releer el workflow justo antes de
  cada PUT; con uno viejo contesta «Your version is outdated», que parece un error del
  nodo y no lo es.
* **Un workflow creado por API nace con `status: null`**, no `draft`, y se comporta a
  medias. Hay que ponerlo en `draft` explícitamente.
* **El trigger se crea con una forma distinta a la que devuelve el GET.** Van `workflowId`
  en camelCase, `status` y `triggersChanged: true`; y después un PUT con `targetActionId`
  apuntando al primer nodo. Con la forma del GET el POST contesta 200 con un id y el
  trigger no existe.
* **El PUT es todo o nada y sí dice qué falla**, en el cuerpo. Se imprime siempre.

⚠️ Nada se publica: **crear un trigger publica el workflow**, así que al final se devuelve
a `draft` a propósito. Ni WhatsApp ni Stripe están conectados; un workflow vivo a medias
hace daño.

⚠️ **Los nodos marcados «TEMPORAL · SMS» son provisionales.** Van donde irá un mensaje de
WhatsApp: hoy la cuenta rechaza `whatsapp_v2` porque no hay número ni plantillas
aprobadas. Se reemplazan cuando exista la WhatsApp Business Account.
"""
import os
import sys

import requests

BASE = "https://backend.leadconnectorhq.com"
PUB = "https://services.leadconnectorhq.com"
FIREBASE_KEY = "AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"   # la de HighLevel, pública
TEMP = "TEMPORAL · SMS"      # prefijo de todo nodo que después será WhatsApp


def jwt_de(refresh_token):
    r = requests.post(f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_KEY}",
                      data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                      timeout=40)
    if not r.ok:
        sys.exit(f"no se pudo canjear el token: {r.status_code} {r.text[:200]}")
    return r.json()["id_token"]


class Interna:
    def __init__(self, jwt, loc):
        self.loc = loc
        self.H = {"token-id": jwt, "channel": "APP", "source": "WEB_USER",
                  "version": "2021-07-28", "Accept": "application/json",
                  "Content-Type": "application/json"}

    def _j(self, r):
        try:
            return r.json()
        except ValueError:
            return {}

    def listar(self):
        return self._j(requests.get(f"{BASE}/workflow/{self.loc}", headers=self.H, timeout=30)) or []

    def leer(self, wid):
        return self._j(requests.get(f"{BASE}/workflow/{self.loc}/{wid}", headers=self.H, timeout=30))

    def crear(self, nombre):
        r = requests.post(f"{BASE}/workflow/{self.loc}", headers=self.H, timeout=30,
                          json={"name": nombre})
        if not r.ok:
            sys.exit(f"no se pudo crear «{nombre}»: {r.status_code} {r.text[:200]}")
        return self._j(r)["id"]

    def buscar(self, nombre):
        for w in self.listar():
            if w.get("name") == nombre:
                return w.get("_id") or w.get("id")
        return None

    def escribir(self, wid, nodos, status="draft"):
        """PUT releyendo la versión. `allowMultiple`/`stopOnResponse` van siempre:
        lo que se omite se resetea a su valor por defecto."""
        d = self.leer(wid)
        r = requests.put(f"{BASE}/workflow/{self.loc}/{wid}", headers=self.H, timeout=40,
                         json={"name": d.get("name"), "version": d.get("version"),
                               "parentId": d.get("parentId"), "status": status,
                               "allowMultiple": False, "stopOnResponse": False,
                               "workflowData": {"templates": nodos}})
        if r.ok:
            return True, ""
        j = self._j(r)
        return False, j.get("errorMessage") or j.get("msg") or r.text[:300]

    def nodos_vivos(self, wid):
        """GHL devuelve los nodos bajo `templates` en unos workflows y bajo `nodes` en
        otros: leer sólo una de las dos hace creer que se guardó vacío."""
        wd = self.leer(wid).get("workflowData") or {}
        return wd.get("nodes") or wd.get("templates") or []

    def triggers(self, wid):
        t = self._j(requests.get(f"{BASE}/workflow/{self.loc}/trigger?workflowId={wid}",
                                 headers=self.H, timeout=30))
        return t.get("triggers", t) if isinstance(t, dict) else (t or [])

    def crear_etiqueta(self, tag):
        requests.post(f"{BASE}/workflow/{self.loc}/tags/create", headers=self.H,
                      timeout=30, json={"tag": tag})

    def crear_trigger(self, wid, cuerpo, primer_nodo):
        """La forma de CREACIÓN, que no es la que devuelve el GET."""
        body = {**cuerpo, "status": "draft", "workflowId": wid,
                "triggersChanged": True, "location_id": self.loc, "active": True,
                "schedule_config": {},
                "actions": [{"workflow_id": wid, "type": "add_to_workflow"}]}
        r = requests.post(f"{BASE}/workflow/{self.loc}/trigger", headers=self.H,
                          timeout=30, json=body)
        tid = (self._j(r) or {}).get("id")
        if not tid:
            return None, f"{r.status_code} {r.text[:160]}"
        # segundo paso: por qué nodo entra. Sin esto existe pero no engancha.
        requests.put(f"{BASE}/workflow/{self.loc}/trigger/{tid}", headers=self.H, timeout=30,
                     json={**body, "id": tid, "targetActionId": primer_nodo,
                           "advanceCanvasMeta": {"position": {"x": 57.5, "y": -73}}})
        return tid, ""


# ---------------------------------------------------------------------------
# Los workflows. Cada armador devuelve (nombre, nodos_def, trigger|None).
# nodos_def = [(attrs, nombre, tipo, workflowsActionType|None)]
# ---------------------------------------------------------------------------

PIPE = "80QTHEK406nT2KJhQ6TZ"
ETAPA = {"lead": "bd808b6f-2132-4c20-bff8-67ec06db36f6",
         "bot": "d34058aa-0d9e-42a0-af22-b1732835e676",
         "apartado": "4e1d2753-b967-4817-b3b2-2b0a42efa5c6",
         "liga": "4f1e4ebd-9514-4f7d-98ef-0bcb4c145744",
         "pagado": "6cd0228e-6968-49fc-9492-4ea1f1ba47be",
         "almacen": "26291c30-53c4-47ae-bf24-20f6f761211f",
         "enviado": "352335f2-4150-43a0-8067-737cbcd8695e",
         "entregado": "ba84ff53-246f-4f04-9547-acd6f6210292"}

TRIG_TAG = lambda tag: {"type": "contact_tag", "masterType": "highlevel",
                        "name": "Contact Tag",
                        "conditions": [{"operator": "index-of-true", "field": "tagsAdded",
                                        "value": tag, "title": "Tag Added",
                                        "type": "select", "id": "tag-added"}]}


def sms(texto, nombre):
    """Nodo provisional. Va donde irá un WhatsApp cuando exista la WABA."""
    return ({"body": f"[TEMPORAL] {texto}", "attachments": []},
            f"{TEMP} · {nombre}", "sms", None)


def ctx(loc, pit):
    H = {"Authorization": f"Bearer {pit}", "Version": "2021-07-28"}
    l = requests.get(f"{PUB}/locations/{loc}", headers=H, timeout=30).json().get("location", {})
    duenos = [u["id"] for u in requests.get(f"{PUB}/users/", headers=H,
              params={"locationId": loc}, timeout=30).json().get("users", [])
              if (u.get("email") or "").endswith("@gtxusa.com")]
    return l.get("email") or "no-reply@gtxusa.com", l.get("name") or "Greentex", duenos


def ls01(tk, loc, pit):
    """LS01 · Entrada de lead — atribución y oportunidad en «Lead Nuevo»."""
    return "LS01 · Entrada de lead menudeo", [
        (tk.n_campo_estandar("source", "WhatsApp", "Source"), "Marcar origen",
         "update_contact_field", None),
        (tk.n_crear_oportunidad(PIPE, ETAPA["lead"]), "Crear oportunidad",
         "internal_create_opportunity", "INTERNAL"),
    ], None


def sp02(tk, loc, pit):
    """SP02 · Apartado 24 h — el reloj. 12 h + 10 h + 2 h 20 = 24 h 20 min.

    Los 20 minutos de más son margen para el cron de `N2`, que corre cada 15 y es quien
    marca la oportunidad como vencida.
    """
    return "SP02 · Apartado 24 h", [
        sms("Tu paca quedó apartada. Tienes 24 horas para pagarla: "
            "{{opportunity.liga_pago}}. Si no alcanzas, se libera sola y no hay ningún "
            "cargo.", "Términos y condiciones"),
        (tk.n_espera(12, "hours"), "Espera 12 h", "wait", None),
        sms("Tu apartado de {{opportunity.articulo_apartado}} vence hoy. Aquí está tu "
            "liga: {{opportunity.liga_pago}}", "Recordatorio"),
        (tk.n_espera(10, "hours"), "Espera 10 h", "wait", None),
        sms("Última llamada: tu apartado vence en un par de horas. "
            "{{opportunity.liga_pago}}", "Recordatorio final"),
        (tk.n_espera(140, "minutes"), "Espera 2 h 20 min", "wait", None),
        (tk.n_tags(["apartado-vencido"]), "Marcar vencido", "add_contact_tag", None),
        sms("Tu apartado de {{opportunity.articulo_apartado}} venció y la paca volvió a "
            "estar disponible. Si todavía la quieres, contéstanos por aquí.",
            "Apartado vencido"),
    ], None


def sp04(tk, loc, pit):
    """SP04 · Pago confirmado — mueve la oportunidad y avisa."""
    return "SP04 · Pago confirmado", [
        (tk.n_mover_oportunidad(PIPE, ETAPA["pagado"]), "Mover a Pago Confirmado",
         "internal_update_opportunity", "INTERNAL"),
        (tk.n_tags(["apartado-vencido"]), "Quitar marca de vencido",
         "remove_contact_tag", None),
        sms("¡Listo! Ya recibimos tu pago. Tu orden pasa a preparación y en cuanto salga "
            "del almacén te mandamos el número de guía.", "Pago confirmado"),
    ], None


def sp05(tk, loc, pit):
    """SP05 · Despacho — llama a `N4`, que genera la guía en Envia.

    ⚠️ Al almacén **nunca** le va el monto. Regla dura, textual de Miguel.
    """
    de_correo, de_nombre, duenos = ctx(loc, pit)
    return "SP05 · Despacho", [
        # El Custom Data va en `customData`, no en `data`: con `data` el webhook sale vacío y N4 falla.
        ({"url": "{{custom_values.url_n8n_generar_guia}}", "method": "POST", "data": [],
          "customData": [{"key": k, "value": v} for k, v in [
              ("opportunityId", "{{opportunity.id}}"), ("orden_id", "{{opportunity.orden_id}}"),
              ("cantidad", "{{opportunity.cantidad_apartada}}"), ("nombre", "{{contact.name}}"),
              ("telefono", "{{contact.phone}}"), ("email", "{{contact.email}}"),
              ("calle", "{{contact.address1}}"), ("ciudad", "{{contact.ciudad}}"),
              ("estado_mx", "{{contact.estado_mx}}"), ("codigo_postal", "{{contact.codigo_postal}}"),
              ("servicio", "{{contact.servicio_envio}}"), ("branch_code", "{{contact.branch_code}}")]]},
         "Pedirle la guía a n8n", "webhook", None),
        (tk.n_espera(2, "minutes"), "Espera a que N4 escriba la guía", "wait", None),
        (tk.n_aviso_correo(
            "Nueva orden pagada — {{opportunity.articulo_apartado}}",
            "<p>Orden: {{opportunity.orden_id}}</p>"
            "<p>Cliente: {{contact.first_name}} {{contact.last_name}} · {{contact.phone}}</p>"
            "<p>Artículo: {{opportunity.articulo_apartado}}</p>"
            "<p>Destino: {{contact.ciudad}}, {{contact.estado_mx}} · CP {{contact.codigo_postal}}</p>"
            "<p>Guía: {{opportunity.numero_guia}}</p>",
            duenos, de_correo, de_nombre), "Correo a los dueños",
         "internal_notification", None),
        sms("Tu paca ya va en camino. Guía: {{opportunity.numero_guia}} · "
            "Paquetería: Paquete Express. La recoges en {{contact.sucursal_ocurre}}. "
            "Llévate una identificación.", "Orden enviada"),
        (tk.n_mover_oportunidad(PIPE, ETAPA["almacen"]), "Mover a Orden en Almacén",
         "internal_update_opportunity", "INTERNAL"),
    ], None


def ap01(tk, loc, pit):
    """AP01 · Rastreo — lo llama `N5` por Inbound Webhook.

    ⚠️ **El trigger espera la URL del Inbound Webhook**, que la da la interfaz. Los nodos
    se arman igual; el trigger se conecta después, y su id va en `GHL_WEBHOOK_RASTREO`
    del `Config` de `N5`.
    """
    return "AP01 · Rastreo", [
        sms("Tu paquete ya llegó a la sucursal. Guía: {{opportunity.numero_guia}}. "
            "Llévate una identificación para recogerlo.", "Llegó a la sucursal"),
        (tk.n_mover_oportunidad(PIPE, ETAPA["entregado"]), "Cerrar como entregado",
         "internal_update_opportunity", "INTERNAL"),
    ], None


def ap02(tk, loc, pit):
    """AP02 · Escalamiento a humano.

    ⚠️ **Le falta el primer nodo**, el que apaga el bot: Greentex lo rechaza con «action
    has a corrupted type» porque Conversation AI no está provisionado —cero números y
    cero bots—. Va PRIMERO en cuanto exista: si el bot no se apaga, el dueño contesta y
    el bot le escribe encima al cliente.
    """
    de_correo, de_nombre, duenos = ctx(loc, pit)
    return "AP02 · Escalamiento a humano", [
        (tk.n_aviso_correo(
            "Un cliente pidió hablar con una persona — {{contact.first_name}} {{contact.last_name}}",
            "<p><b>{{contact.first_name}} {{contact.last_name}}</b> pidió que lo atienda "
            "una persona.</p><p>Teléfono: {{contact.phone}}<br>Correo: {{contact.email}}</p>",
            duenos, de_correo, de_nombre), "Avisar a los dueños",
         "internal_notification", None),
    ], TRIG_TAG("escalar-humano")


def ap03(tk, loc, pit):
    """AP03 · Registro manual de pago por transferencia.

    ⚠️ **El formulario es de interfaz**: lo crea Germán y después se conecta como trigger.
    """
    return "AP03 · Pago manual por transferencia", [
        (tk.n_mover_oportunidad(PIPE, ETAPA["pagado"]), "Mover a Pago Confirmado",
         "internal_update_opportunity", "INTERNAL"),
        sms("¡Listo! Registramos tu pago por transferencia. Tu orden pasa a preparación.",
            "Pago manual confirmado"),
    ], None


ARMADORES = {"LS01": ls01, "SP02": sp02, "SP04": sp04, "SP05": sp05,
             "AP01": ap01, "AP02": ap02, "AP03": ap03}


def main():
    pedidos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if pedidos == ["todos"] or not pedidos:
        pedidos = list(ARMADORES)
    malos = [p for p in pedidos if p not in ARMADORES]
    if malos:
        sys.exit(f"no conozco {malos}. Disponibles: {', '.join(ARMADORES)}")
    aplicar = "--aplicar" in sys.argv

    kit = os.environ.get("GHL_KIT")
    rt = os.environ.get("GHL_FIREBASE_REFRESH_TOKEN")
    pit = os.environ.get("GHL_API_KEY")
    loc = os.environ.get("GHL_LOCATION_ID")
    if not (kit and rt and pit and loc):
        sys.exit(__doc__)
    sys.path.insert(0, kit)
    from cli_anything.gohighlevel.utils import wf_toolkit as tk

    C = Interna(jwt_de(rt), loc) if aplicar else None
    resumen = []

    for cual in pedidos:
        nombre, nodos_def, trig = ARMADORES[cual](tk, loc, pit)
        nodos = tk.cadena_raiz(nodos_def)
        print(f"\n=== {nombre} ===")
        for n in nodos:
            print(f'  {n["type"]:<30} {n["name"]}')
        problemas = tk.validar_grafo(nodos)
        if problemas:
            print("  grafo roto, no se escribe:")
            for p in problemas:
                print("   ✗", p)
            resumen.append((cual, "GRAFO ROTO"))
            continue
        if not aplicar:
            resumen.append((cual, f"{len(nodos)} nodos · validado"))
            continue

        wid = C.buscar(nombre) or C.crear(nombre)
        ok, msg = C.escribir(wid, nodos)
        if not ok:
            print(f"  PUT RECHAZADO: {msg}")
            resumen.append((cual, f"RECHAZADO: {msg[:40]}"))
            continue
        vivos = C.nodos_vivos(wid)

        estado = f"{len(vivos)} nodos"
        if trig and not C.triggers(wid):
            C.crear_etiqueta(trig["conditions"][0]["value"])
            tid, err = C.crear_trigger(wid, trig, vivos[0]["id"] if vivos else None)
            C.escribir(wid, vivos)            # crear el trigger publica: de vuelta a draft
            estado += f" · trigger {'ok' if C.triggers(wid) else 'NO persistió ' + err}"
        elif trig:
            estado += " · trigger ya estaba"
        else:
            estado += " · sin trigger (va a mano)"

        d = C.leer(wid)
        estado += f" · {d.get('status')}"
        print(f"  → {estado}")
        resumen.append((cual, estado))

    print("\n" + "=" * 70)
    for cual, est in resumen:
        print(f"  {cual:<6} {est}")
    if not aplicar:
        print("\n--aplicar para escribirlo")


if __name__ == "__main__":
    main()
