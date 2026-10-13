#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea en n8n un flujo del repo que todavía no existe en la instancia. Queda apagado.

Uso:
    N8N_API_URL=https://devn8n.korvance.com N8N_API_KEY=... \
        python scripts/crear-n8n.py n8n/N6-envio-pedido.json [--aplicar]

Sin --aplicar sólo dice qué haría. `subir-n8n.py` no crea flujos: toma la credencial real
de los nodos vivos del mismo flujo, y uno nuevo no tiene. Aquí se toma de `N1`. Si el
flujo ya existe, no hace nada: para actualizarlo está `subir-n8n.py`.
"""
import json
import os
import sys

import requests


def main():
    aplicar = "--aplicar" in sys.argv
    archivos = [a for a in sys.argv[1:] if not a.startswith("--")]
    url = os.environ.get("N8N_API_URL", "").rstrip("/")
    key = os.environ.get("N8N_API_KEY")
    if not url or not key or len(archivos) != 1:
        sys.exit(__doc__)
    H = {"X-N8N-API-KEY": key, "Accept": "application/json", "Content-Type": "application/json"}
    api = f"{url}/api/v1"

    r = requests.get(f"{api}/workflows", headers=H, params={"limit": 250}, timeout=30)
    if not r.ok:
        sys.exit(f"No se pudo listar los flujos: {r.status_code} {r.text[:300]}")
    vivos = [w for w in r.json()["data"] if not w.get("isArchived")]

    repo = json.load(open(archivos[0], encoding="utf-8"))
    nombre = repo["name"]
    if any(w["name"] == nombre for w in vivos):
        sys.exit(f"«{nombre}» ya existe en la instancia. Usa scripts/subir-n8n.py.")

    n1 = [w for w in vivos if w["name"].startswith("N1")]
    if len(n1) != 1:
        sys.exit(f"{len(n1)} flujos N1 en la instancia; no se adivina de cuál copiar la credencial.")
    n1 = requests.get(f"{api}/workflows/{n1[0]['id']}", headers=H, timeout=30).json()

    # tipo de credencial -> credencial real de N1
    reales = {}
    for n in n1["nodes"]:
        for tipo, cred in (n.get("credentials") or {}).items():
            if cred.get("id") not in (None, "REEMPLAZAR"):
                reales.setdefault(tipo, cred)

    faltan = []
    for n in repo["nodes"]:
        for tipo in (n.get("credentials") or {}):
            if tipo in reales:
                n["credentials"][tipo] = reales[tipo]
            else:
                faltan.append(f"{tipo} (nodo «{n['name']}»)")
    if faltan:
        # Un nodo HTTP sin credencial se guarda sin error y falla en la corrida.
        sys.exit("N1 no tiene credencial real para: " + "; ".join(faltan))

    print(f"{archivos[0]} → «{nombre}», {len(repo['nodes'])} nodos")
    for tipo, cred in reales.items():
        print(f"  credencial {tipo} → «{cred.get('name')}»")
    for n in repo["nodes"]:
        if n["type"].endswith(".webhook"):
            print(f"  {n['parameters'].get('httpMethod', 'GET')} {url}/webhook/{n['parameters']['path']}")

    if not aplicar:
        print("\nNada se cambió. Corre con --aplicar para crearlo.")
        return
    r = requests.post(f"{api}/workflows", headers=H, timeout=60,
                      json={"name": nombre, "nodes": repo["nodes"], "connections": repo["connections"],
                            "settings": {"executionOrder": "v1", "saveManualExecutions": True}})
    if not r.ok:
        sys.exit(f"✗ {r.status_code} {r.text[:400]}")
    d = r.json()
    print(f"  ✓ creado: id {d['id']} · {'activo' if d.get('active') else 'apagado'} · {len(d['nodes'])} nodos")


if __name__ == "__main__":
    main()
