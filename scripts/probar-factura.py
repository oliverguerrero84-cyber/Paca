#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validación 1: crea una factura por la API de Invoices con el MISMO cuerpo que manda
n8n/N1-apartar.json, la marca como enviada sin correo, y dice qué liga devuelve.

Sirve para confirmar los dos supuestos anotados en N1:
  1. que POST /invoices/ acepta contactDetails sólo con id
  2. cuál es el formato de la liga de pago de la factura

Uso:
    export GHL_API_KEY='pit-...'            # de la subcuenta donde se prueba
    export GHL_LOCATION_ID='...'            # Korvance para el ensayo, Greentex para la real
    export GHL_CONTACT_ID='...'
    export GHL_PRODUCT_ID='...'
    export GHL_PRICE_ID='...'
    export GHL_USER_ID='...'                # quien "manda" la factura (sentBy)
    export GHL_CURRENCY='USD'               # MXN en Greentex
    python3 scripts/probar-factura.py

No escribe nada a disco. Si la API contesta 4xx, imprime el cuerpo del error tal cual:
eso es lo que hay que leer para corregir N1.
"""
import datetime as dt
import json
import os
import sys

import requests

BASE = "https://services.leadconnectorhq.com"


def env(nombre):
    v = os.environ.get(nombre)
    if not v:
        sys.exit(f"falta {nombre} en el entorno")
    return v


def main():
    H = {"Authorization": f"Bearer {env('GHL_API_KEY')}", "Version": "2021-07-28",
         "Content-Type": "application/json", "Accept": "application/json"}
    loc, moneda = env("GHL_LOCATION_ID"), os.environ.get("GHL_CURRENCY", "MXN")
    hoy = dt.date.today()

    # ponytail: mismo cuerpo que el nodo «GHL · crear factura» de N1; el monto real
    # sale del price, aquí va fijo porque sólo probamos la mecánica.
    cuerpo = {
        "altId": loc, "altType": "location",
        "name": "Paca PRUEBA",
        "currency": moneda,
        "liveMode": True,
        "contactDetails": {"id": env("GHL_CONTACT_ID")},
        "items": [{"name": "Paca de prueba", "currency": moneda, "amount": 1, "qty": 1,
                   "productId": env("GHL_PRODUCT_ID"), "priceId": env("GHL_PRICE_ID")}],
        "issueDate": hoy.isoformat(),
        "dueDate": (hoy + dt.timedelta(days=1)).isoformat(),
    }
    r = requests.post(f"{BASE}/invoices/", headers=H, json=cuerpo, timeout=30)
    print(f"POST /invoices/ -> {r.status_code}")
    if r.status_code >= 400:
        print(r.text)
        sys.exit("crear falló: ese es el supuesto 1 de N1, corrígelo con lo que dice arriba")
    factura = r.json()
    fid = factura.get("_id") or factura.get("id")
    print("invoice_id:", fid)
    print("campos con URL en la respuesta:",
          {k: v for k, v in factura.items() if isinstance(v, str) and "http" in v} or "ninguno")

    envio = {"altId": loc, "altType": "location", "userId": env("GHL_USER_ID"),
             "action": "send_manually", "liveMode": True}
    r = requests.post(f"{BASE}/invoices/{fid}/send", headers=H, json=envio, timeout=30)
    print(f"POST /invoices/{fid}/send -> {r.status_code}")
    if r.status_code >= 400:
        print(r.text)
        sys.exit("enviar falló")
    resp = r.json()
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:2000])
    print("\nSi arriba no viene una liga, la de N1 es {dominio de la subcuenta}/invoice/" + str(fid)
          + " — ábrela y confirma que levanta el checkout.")


if __name__ == "__main__":
    main()
