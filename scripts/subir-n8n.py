#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sube los flujos de n8n/ del repo a la instancia de n8n, sin reimportar a mano.

Uso:
    N8N_API_URL=https://devn8n.korvance.com N8N_API_KEY=... \
        python scripts/subir-n8n.py n8n/N1-apartar.json [n8n/N2-...json ...] [--aplicar]

Sin --aplicar sólo dice qué haría. Busca en la instancia el flujo con el mismo nombre y
lo actualiza en su lugar: conserva su id, si está activo y sus settings.

Las credenciales del repo son marcadores (id REEMPLAZAR, nombre «GHL · PIT Greentex» o
«Envia · API»). Para cada marcador se usa la credencial real que ya tiene asignada algún
nodo del flujo en la instancia; así los nodos nuevos heredan la de sus hermanos. Si un
marcador no tiene credencial real en la instancia, no sube nada: un nodo HTTP sin
credencial se guarda sin error y después falla en la corrida.
"""
import json
import os
import sys

import requests

# Los settings que acepta el PUT de la API pública; cualquier otra llave da 400.
SETTINGS_API = {"saveExecutionProgress", "saveManualExecutions", "saveDataErrorExecution",
                "saveDataSuccessExecution", "executionTimeout", "errorWorkflow", "timezone",
                "executionOrder", "callerPolicy", "callerIds", "timeSavedPerExecution"}


def main():
    aplicar = "--aplicar" in sys.argv
    archivos = [a for a in sys.argv[1:] if not a.startswith("--")]
    url = os.environ.get("N8N_API_URL", "").rstrip("/")
    key = os.environ.get("N8N_API_KEY")
    if not url or not key or not archivos:
        sys.exit(__doc__)
    H = {"X-N8N-API-KEY": key, "Accept": "application/json", "Content-Type": "application/json"}
    api = f"{url}/api/v1"

    vivos, cursor = [], None
    while True:
        r = requests.get(f"{api}/workflows", headers=H, timeout=30,
                         params={"limit": 250, **({"cursor": cursor} if cursor else {})})
        if not r.ok:
            sys.exit(f"No se pudo listar los flujos: {r.status_code} {r.text[:300]}")
        d = r.json()
        vivos += d.get("data", [])
        cursor = d.get("nextCursor")
        if not cursor:
            break

    errores = 0
    for archivo in archivos:
        repo = json.load(open(archivo, encoding="utf-8"))
        nombre = repo["name"]
        # Las archivadas son las copias viejas que deja cada reimportación: no cuentan.
        iguales = [w for w in vivos if w["name"] == nombre and not w.get("isArchived")]
        print(f"\n{archivo} → «{nombre}»")
        if len(iguales) != 1:
            # Con dos copias del mismo nombre no se adivina cuál es la buena.
            print(f"  ✗ {len(iguales)} flujos con ese nombre en la instancia: "
                  + ", ".join(f"{w['id']} ({'activo' if w.get('active') else 'inactivo'})" for w in iguales)
                  + ". Renombra o borra las copias viejas.")
            errores += 1
            continue
        vivo = requests.get(f"{api}/workflows/{iguales[0]['id']}", headers=H, timeout=30).json()

        # marcador (nombre en el repo) -> credencial real, sacada de los nodos vivos
        repo_por_nombre = {n["name"]: n for n in repo["nodes"]}
        reales = {}
        for n in vivo["nodes"]:
            espejo = repo_por_nombre.get(n["name"])
            for tipo, cred in (n.get("credentials") or {}).items():
                if espejo and tipo in (espejo.get("credentials") or {}) and cred.get("id") not in (None, "REEMPLAZAR"):
                    reales[(tipo, espejo["credentials"][tipo]["name"])] = cred

        faltan = set()
        for n in repo["nodes"]:
            for tipo, cred in (n.get("credentials") or {}).items():
                real = reales.get((tipo, cred.get("name")))
                if real:
                    n["credentials"][tipo] = real
                else:
                    faltan.add(f"{tipo} «{cred.get('name')}» (nodo «{n['name']}»)")
        if faltan:
            print("  ✗ sin credencial real en la instancia para: " + "; ".join(sorted(faltan)))
            print("    Asígnala a mano en al menos un nodo de ese tipo y vuelve a correr.")
            errores += 1
            continue

        antes = {n["name"] for n in vivo["nodes"]}
        despues = {n["name"] for n in repo["nodes"]}
        print(f"  id {vivo['id']} · {'activo' if vivo.get('active') else 'inactivo'}")
        for (tipo, marcador), real in sorted(reales.items()):
            print(f"  credencial «{marcador}» → «{real.get('name')}»")
        for x in sorted(despues - antes):
            print(f"  + {x}")
        for x in sorted(antes - despues):
            print(f"  - {x}")
        print(f"  = {len(antes & despues)} nodos que se quedan (con el contenido del repo)")

        if not aplicar:
            continue
        cuerpo = {"name": nombre, "nodes": repo["nodes"], "connections": repo["connections"],
                  "settings": {k: v for k, v in (vivo.get("settings") or {}).items() if k in SETTINGS_API}}
        r = requests.put(f"{api}/workflows/{vivo['id']}", headers=H, json=cuerpo, timeout=60)
        if r.ok:
            print("  ✓ actualizado")
        else:
            print(f"  ✗ {r.status_code} {r.text[:400]}")
            errores += 1

    if not aplicar:
        print("\nNada se cambió. Corre con --aplicar para subirlo.")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
