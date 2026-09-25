#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba de la API de Envia.com contra el SANDBOX, con los endpoints que usan N3, N4 y N5.
Confirma los supuestos 3 a 6 de n8n/README.md y los pendientes de docs/06 §5.

Corre en orden y se detiene en el primer paso que falle:
  1. paqueterías activas en México            GET  queries/carrier?country_code=MX
  2. servicios de la paquetería elegida       GET  queries/service?country_code=MX&carrier=…
  3. coordenadas de un código postal          GET  geocodes/zipcode/MX/{cp}
  4. sucursales de la paquetería cerca del CP GET  queries/branches/{carrier}/MX?zipcode=…
  5. cotización almacén → CP                  POST ship/rate/
  6. guía de prueba (sandbox, sin cargo)      POST ship/generate/     (sólo con --guia)
  7. rastreo de esa guía                      POST ship/generaltrack/ (sólo con --guia)

Uso:
    export ENVIA_TOKEN='…'        # llave del SANDBOX: shipping-test.envia.com/settings/developers
    export ENVIA_CARRIER='paquetexpress'   # opcional; si no existe con ese nombre, el paso 1 lo dice
    export DESTINO_CP='64060'              # opcional, un CP de destino para la prueba
    python3 scripts/probar-envia.py [--guia] [--produccion]

Sin --guia no genera nada, sólo consulta. Con --produccion usa api.envia.com y SÍ cobra.
El token se lee del entorno y nunca se escribe a disco.
"""
import json
import os
import sys

import requests

SANDBOX = "--produccion" not in sys.argv
API = "https://api-test.envia.com" if SANDBOX else "https://api.envia.com"
QUERIES = "https://queries.test.envia.com" if SANDBOX else "https://queries.envia.com"
GEO = "https://geocodes.envia.com"

TOKEN = os.environ.get("ENVIA_TOKEN") or sys.exit("falta ENVIA_TOKEN en el entorno")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "Accept": "application/json"}
CARRIER = os.environ.get("ENVIA_CARRIER", "paquetexpress")
CP = os.environ.get("DESTINO_CP", "64060")

# ponytail: el almacén real (Nuevo Laredo) todavía no lo manda el cliente; esto es un
# origen de prueba válido para cotizar. Cuando lleguen los ALMACEN_* del README, van aquí.
ORIGEN = {"name": "Almacén Paca", "company": "Greentex", "email": "almacen@example.com",
          "phone": "8671234567", "street": "Av. Reforma", "number": "100", "district": "Centro",
          "city": "Nuevo Laredo", "state": "TM", "country": "MX", "postalCode": "88000"}
PAQUETE = {"type": "box", "content": "Ropa usada, paca 100 lb", "amount": 1, "name": "Paca",
           "declaredValue": 1500, "lengthUnit": "CM", "weightUnit": "KG", "weight": 45,
           "dimensions": {"length": 80, "width": 50, "height": 50}}


def paso(n, que, r):
    print(f"\n[{n}] {que} -> {r.status_code}")
    if r.status_code >= 400:
        print(r.text[:1500])
        sys.exit(f"paso {n} falló")
    return r.json()


def main():
    d = paso(1, "paqueterías en MX", requests.get(f"{QUERIES}/carrier", headers=H, params={"country_code": "MX"}, timeout=30))
    nombres = [c.get("name") for c in d.get("data", []) if c.get("active", True)]
    print("   activas:", ", ".join(nombres))
    if CARRIER not in nombres:
        sys.exit(f"'{CARRIER}' no está en la lista: elige uno de arriba y ponlo en ENVIA_CARRIER")

    d = paso(2, f"servicios de {CARRIER}", requests.get(f"{QUERIES}/service", headers=H, params={"country_code": "MX", "carrier": CARRIER}, timeout=30))
    servicios = [s.get("name") for s in d.get("data", [])]
    print("   servicios:", ", ".join(servicios))

    geo = paso(3, f"geocodes del CP {CP}", requests.get(f"{GEO}/zipcode/MX/{CP}", headers=H, timeout=30)).get("data", {})
    print("   ", json.dumps(geo, ensure_ascii=False)[:300], "  <- pendiente 2 de docs/06 §5")

    d = paso(4, f"sucursales de {CARRIER} cerca de {CP}",
             requests.get(f"{QUERIES}/branches/{CARRIER}/MX", headers=H, params={"zipcode": CP, "limitBranches": 5}, timeout=30))
    sucursales = d if isinstance(d, list) else d.get("data", [])
    print(f"   {len(sucursales)} sucursales; primera:", json.dumps(sucursales[0], ensure_ascii=False)[:400] if sucursales else "ninguna")
    con_coord = [s for s in sucursales if (s.get("address") or {}).get("latitude")]
    print(f"   con coordenadas: {len(con_coord)} de {len(sucursales)}   <- supuesto 4 de n8n/README.md")

    destino = dict(ORIGEN, name="Cliente Prueba", company="", email="cliente@example.com",
                   phone="8112345678", street="Calle Uno", number="1", district="Centro",
                   city=geo.get("city", ""), state=geo.get("state", ""), postalCode=CP)
    cuerpo = {"origin": ORIGEN, "destination": destino, "packages": [PAQUETE],
              "shipment": {"type": 1, "carrier": CARRIER}, "settings": {"currency": "MXN"}}
    d = paso(5, "cotización almacén -> CP", requests.post(f"{API}/ship/rate/", headers=H, json=cuerpo, timeout=60))
    tarifas = d.get("data", [])
    for t in tarifas:
        print(f"   {t.get('carrier')} {t.get('service')}: {t.get('totalPrice')} {t.get('currency')} — {t.get('deliveryEstimate')}")
    if not tarifas:
        sys.exit("sin tarifas: revisa peso/medidas o la paquetería")

    if "--guia" not in sys.argv:
        print("\nConsultas OK. Para generar una guía de prueba en el sandbox, vuelve a correr con --guia.")
        return

    servicio = min(tarifas, key=lambda t: t.get("totalPrice", 1e9)).get("service")
    cuerpo["shipment"] = {"carrier": CARRIER, "service": servicio, "type": 1, "reverse_pickup": 0, "import": 0}
    cuerpo["settings"] = {"currency": "MXN", "printFormat": "PDF", "printSize": "STOCK_4X6"}
    d = paso(6, f"guía {CARRIER}/{servicio}", requests.post(f"{API}/ship/generate/", headers=H, json=cuerpo, timeout=60))
    g = d.get("data", [{}])[0]
    print("   trackingNumber:", g.get("trackingNumber"), "| label:", g.get("label"), "| precio:", g.get("totalPrice"), g.get("currency"))

    d = paso(7, "rastreo", requests.post(f"{API}/ship/generaltrack/", headers=H, json={"trackingNumbers": [g.get("trackingNumber")]}, timeout=60))
    print("   ", json.dumps(d, ensure_ascii=False)[:800])
    print("\nTodo OK. Con esto se corrigen N3, N4 y N5 y se cierran los supuestos 3 a 6.")


if __name__ == "__main__":
    main()
