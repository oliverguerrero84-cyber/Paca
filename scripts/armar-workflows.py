#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma los workflows de GHL por la API interna, que es la única que los crea.

Uso:
    GHL_FIREBASE_REFRESH_TOKEN=AMf-...  GHL_API_KEY=pit-...  GHL_LOCATION_ID=c9jj... \
        python scripts/armar-workflows.py AP02 [--aplicar]

Sin `--aplicar` sólo imprime el árbol que armaría y valida el grafo. No escribe nada.

**Hace falta el kit de 786** (`ghl-kit`), que trae el toolkit con los moldes de nodo
clonados de workflows vivos. Se le dice dónde está con `GHL_KIT`.

Qué resuelve este script, que costó averiguar (1 oct 2026):

* **La API pública NO crea workflows** — `GET /workflows/` sólo lista. La única vía es
  la interna, `backend.leadconnectorhq.com`, con la cabecera `token-id`.
* **El token de la extensión de Chrome no autentica.** Empieza con `AMf-` y es un
  *refresh token* de Firebase. Se canjea por un JWT (`eyJ…`, una hora de vida) contra
  `securetoken.googleapis.com`. La API key de HighLevel vive en el kit.
* **El `version` del workflow es control de concurrencia optimista.** Sube con cada PUT,
  así que hay que **releerlo justo antes de cada escritura**. Con uno viejo el API
  contesta «Your version is outdated», que parece un error del nodo y no lo es.
* **El PUT es todo o nada y sí explica el fallo**, en el cuerpo de la respuesta. Este
  script lo imprime siempre.
* **`allowMultiple` y `stopOnResponse` van siempre en el body**: lo omitido se resetea.

⚠️ **Crear un trigger PUBLICA el workflow**, aunque el body diga `active: false`. Por eso
los triggers se escriben con `--con-trigger`, a propósito y por separado.
"""
import os
import sys

import requests

BASE = "https://backend.leadconnectorhq.com"
FIREBASE_KEY = "AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"   # la de HighLevel, pública


def jwt_de(refresh_token):
    """Canjea el refresh token de la extensión por el JWT que sí autentica."""
    r = requests.post(f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_KEY}",
                      data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                      timeout=40)
    if not r.ok:
        sys.exit(f"no se pudo canjear el token: {r.status_code} {r.text[:200]}")
    return r.json()["id_token"]


class Interna:
    """Cliente de la API interna. Relee la versión antes de cada PUT."""

    def __init__(self, jwt, loc):
        self.loc = loc
        self.H = {"token-id": jwt, "channel": "APP", "source": "WEB_USER",
                  "version": "2021-07-28", "Accept": "application/json",
                  "Content-Type": "application/json"}

    def listar(self):
        return requests.get(f"{BASE}/workflow/{self.loc}", headers=self.H, timeout=30).json()

    def leer(self, wid):
        return requests.get(f"{BASE}/workflow/{self.loc}/{wid}", headers=self.H, timeout=30).json()

    def crear(self, nombre):
        r = requests.post(f"{BASE}/workflow/{self.loc}", headers=self.H, timeout=30,
                          json={"name": nombre})
        if not r.ok:
            sys.exit(f"no se pudo crear «{nombre}»: {r.status_code} {r.text[:200]}")
        return r.json()["id"]

    def escribir(self, wid, nodos, allow_multiple=False, stop_on_response=False):
        """PUT releyendo la versión. Devuelve (ok, mensaje)."""
        d = self.leer(wid)                      # versión FRESCA, siempre
        r = requests.put(f"{BASE}/workflow/{self.loc}/{wid}", headers=self.H, timeout=40,
                         json={"name": d.get("name"), "version": d.get("version"),
                               "parentId": d.get("parentId"), "status": d.get("status"),
                               "allowMultiple": allow_multiple,
                               "stopOnResponse": stop_on_response,
                               "workflowData": {"templates": nodos}})
        if r.ok:
            return True, ""
        try:
            j = r.json()
            return False, j.get("errorMessage") or j.get("msg") or r.text[:300]
        except ValueError:
            return False, r.text[:300]

    def nodos_vivos(self, wid):
        """Lo que quedó escrito. Mira las DOS claves: GHL devuelve los nodos bajo
        `templates` en unos workflows y bajo `nodes` en otros."""
        wd = self.leer(wid).get("workflowData") or {}
        return wd.get("nodes") or wd.get("templates") or []

    def buscar(self, nombre):
        for w in self.listar():
            if w.get("name") == nombre:
                return w.get("_id") or w.get("id")
        return None


# ---------------------------------------------------------------------------
# Los workflows. Cada uno devuelve (nombre, nodos_def).
# nodos_def = [(attrs, nombre, tipo, workflowsActionType|None)]
# ---------------------------------------------------------------------------

def ap02(tk, loc, pit):
    """AP02 · Escalamiento a humano — el cliente pide una persona.

    ⚠️ **Le falta el primer nodo**, el que apaga el bot. Greentex lo rechaza hoy con
    «action has a corrupted type», con los dos nombres de tipo (`ai_status` y
    `update_conversation_ai_status`): Conversation AI no está provisionado todavía,
    porque no hay bot ni WhatsApp. **Hay que volver a meterlo en cuanto exista el bot**,
    y va PRIMERO: si el bot no se apaga, el dueño contesta y el bot le escribe encima
    al cliente.
    """
    loc_d = requests.get(f"https://services.leadconnectorhq.com/locations/{loc}",
                         headers={"Authorization": f"Bearer {pit}", "Version": "2021-07-28"},
                         timeout=30).json().get("location", {})
    # Los 3 del cliente. El aviso es para quien atiende, así que 786 queda fuera.
    duenos = [u["id"] for u in requests.get(
        "https://services.leadconnectorhq.com/users/",
        headers={"Authorization": f"Bearer {pit}", "Version": "2021-07-28"},
        params={"locationId": loc}, timeout=30).json().get("users", [])
        if (u.get("email") or "").endswith("@gtxusa.com")]
    if not duenos:
        sys.exit("no encontré usuarios del cliente (@gtxusa.com) en la subcuenta")

    cuerpo = (
        "<p><b>{{contact.first_name}} {{contact.last_name}}</b> pidió que lo atienda "
        "una persona.</p>"
        "<p>Teléfono: {{contact.phone}}<br>Correo: {{contact.email}}</p>"
        "<p>El asistente ya quedó apagado en esa conversación, así que pueden "
        "contestarle directo por WhatsApp sin que les escriba encima.</p>")

    return "AP02 · Escalamiento a humano", [
        (tk.n_aviso_correo(
            "Un cliente pidió hablar con una persona — "
            "{{contact.first_name}} {{contact.last_name}}",
            cuerpo, duenos, loc_d.get("email") or "no-reply@gtxusa.com",
            loc_d.get("name") or "Greentex"),
         "Avisar a los dueños", "internal_notification", None),
    ]


ARMADORES = {"AP02": ap02}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ARMADORES:
        sys.exit(__doc__ + f"\nDisponibles: {', '.join(sorted(ARMADORES))}\n")
    cual = sys.argv[1]
    aplicar = "--aplicar" in sys.argv

    kit = os.environ.get("GHL_KIT")
    rt = os.environ.get("GHL_FIREBASE_REFRESH_TOKEN")
    pit = os.environ.get("GHL_API_KEY")
    loc = os.environ.get("GHL_LOCATION_ID")
    if not (kit and rt and pit and loc):
        sys.exit(__doc__)
    sys.path.insert(0, kit)
    from cli_anything.gohighlevel.utils import wf_toolkit as tk

    nombre, nodos_def = ARMADORES[cual](tk, loc, pit)
    nodos = tk.cadena_raiz(nodos_def)

    print(f"{nombre}\n")
    for n in nodos:
        print(f'  {n["type"]:<30} {n["name"]}')

    problemas = tk.validar_grafo(nodos)
    if problemas:
        print("\nGrafo roto — no se escribe nada:")
        for p in problemas:
            print("  ✗", p)
        sys.exit(1)
    print(f"\n{len(nodos)} nodos · grafo válido")

    if not aplicar:
        print("\n--aplicar para escribirlo")
        return

    C = Interna(jwt_de(rt), loc)
    wid = C.buscar(nombre) or C.crear(nombre)
    print(f"\nworkflow: {wid}")

    ok, msg = C.escribir(wid, nodos)
    print("PUT:", "ok" if ok else f"RECHAZADO — {msg}")
    if not ok:
        sys.exit(1)

    vivos = C.nodos_vivos(wid)
    print(f"\nLeído de vuelta: {len(vivos)} nodos")
    for n in vivos:
        print(f'  {n.get("type"):<30} {n.get("name")}')
    if len(vivos) != len(nodos):
        sys.exit("\n⚠️  quedaron menos nodos de los que se mandaron")
    print("\nSin trigger: no dispara todavía. Crear el trigger PUBLICA el workflow.")


if __name__ == "__main__":
    main()
