#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma workflows de GHL por la API interna, que es la única que los crea.

Uso:
    GHL_TOKEN_ID=AMf-... GHL_LOCATION_ID=c9jj... python scripts/armar-workflow.py --listar
    GHL_TOKEN_ID=AMf-... GHL_LOCATION_ID=c9jj... python scripts/armar-workflow.py --ver <workflowId>

**Primero se lee, después se escribe.** La API interna no está documentada y su forma
cambia sin aviso, así que este script no adivina el JSON: lee un workflow que ya exista
en la cuenta y vuelca su estructura. Con esa forma en la mano se arma el payload del
que se quiera crear, no antes.

Por qué la API interna y no la pública: `GET /workflows/` de la pública sólo lista. No
hay POST. Crear un workflow sólo se puede desde la interfaz o desde aquí.

El token (`GHL_TOKEN_ID`) es el de Firebase de una sesión abierta del navegador y
**dura alrededor de una hora**. Se saca de las DevTools, en la cabecera `token-id` de
cualquier petición a backend.leadconnectorhq.com. Como todo en este repo, se lee del
entorno y nunca se escribe a un archivo.

⚠️ Regla dura del proyecto: **GHL guarda y muestra nodos malformados que después no
ejecutan, sin dar ningún error.** Nada que se cree con esto cuenta como hecho hasta
volver a leerlo y correrlo.
"""
import json
import os
import sys

import requests

BASE = "https://backend.leadconnectorhq.com"

# La interna no está documentada: estas rutas son las candidatas que hay que probar.
# `--listar` reporta cuál contestó, y ésa es la buena para esta versión de GHL.
RUTAS_LISTAR = [
    "/workflow/{loc}",
    "/workflows/?locationId={loc}",
    "/workflow/?locationId={loc}",
    "/automation/workflow/{loc}",
]
RUTAS_VER = [
    "/workflow/{loc}/{wid}",
    "/workflows/{wid}?locationId={loc}",
    "/workflow/{wid}",
]


def cabeceras(token):
    # channel/source son las que manda la propia interfaz; sin ellas contesta 401.
    return {
        "token-id": token,
        "channel": "APP",
        "source": "WEB_USER",
        "version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def probar(rutas, H, **fmt):
    """Prueba las rutas candidatas en orden y devuelve la primera que conteste 2xx."""
    fallos = []
    for r in rutas:
        url = BASE + r.format(**fmt)
        try:
            resp = requests.get(url, headers=H, timeout=30)
        except requests.RequestException as e:
            fallos.append((r, "error de red", str(e)[:90]))
            continue
        if resp.ok:
            return r, resp.json(), fallos
        fallos.append((r, resp.status_code, resp.text[:90]))
    return None, None, fallos


def main():
    token = os.environ.get("GHL_TOKEN_ID")
    loc = os.environ.get("GHL_LOCATION_ID")
    if not token or not loc or len(sys.argv) < 2:
        sys.exit(__doc__)
    H = cabeceras(token)

    if sys.argv[1] == "--listar":
        ruta, datos, fallos = probar(RUTAS_LISTAR, H, loc=loc)
        if not ruta:
            print("Ninguna ruta contestó. Lo que dijo cada una:")
            for r, cod, txt in fallos:
                print(f"  {cod:<14} {r}")
                print(f"                 {txt}")
            print("\nSi todas dan 401, el token caducó: saca uno nuevo del navegador.")
            sys.exit(1)
        print(f"Ruta buena: {ruta}\n")
        ws = datos.get("workflows") or datos.get("data") or datos
        if isinstance(ws, list):
            for w in ws:
                print(f"  {str(w.get('status','?')):<10} {w.get('name','')}")
                print(f"  {'':<10} id={w.get('id') or w.get('_id')}")
        else:
            print(json.dumps(datos, indent=2, ensure_ascii=False)[:2000])
        return

    if sys.argv[1] == "--ver":
        if len(sys.argv) < 3:
            sys.exit("Falta el id del workflow.")
        wid = sys.argv[2]
        ruta, datos, fallos = probar(RUTAS_VER, H, loc=loc, wid=wid)
        if not ruta:
            print("Ninguna ruta contestó. Lo que dijo cada una:")
            for r, cod, txt in fallos:
                print(f"  {cod:<14} {r}  {txt}")
            sys.exit(1)
        print(f"Ruta buena: {ruta}\n")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        return

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
