#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Levanta el esqueleto de GoHighLevel del menudeo: pipeline, campos y custom values.

Es el eslabón 0.2b de docs/13-accesos.md, y sale tal cual de docs/01-mapa-ghl.md
§1 (las 8 etapas), §4 (los 19 campos en 4 carpetas) y §5 (los 8 custom values).

Uso:
    export GHL_API_KEY='pit-...'
    export GHL_LOCATION_ID='c9jj5uu1WZOIkwi6Vfj5'    # Greentex Clothing LLC
    python3 scripts/crear-esqueleto-menudeo.py [--dry-run]

Idempotente: deduplica pipeline por nombre, campos por fieldKey y custom values
por nombre. Las credenciales se leen del entorno y nunca se escriben a disco.
"""
import os
import sys

import requests

BASE = "https://services.leadconnectorhq.com"
PIPELINE = "SP · Menudeo"

# §1 — las 8 etapas, en orden
ETAPAS = [
    "Lead Nuevo",
    "En Conversación (Bot)",
    "Pedido Apartado (24 h)",
    "Liga de Pago Enviada",
    "Pago Confirmado",
    "Orden en Almacén",
    "Enviado — Guía Generada",
    "Entregado / Cerrado",
]

ESTADOS_APARTADO = ["apartado", "pagado", "vencido", "cancelado"]

# §4 — 19 campos en 4 carpetas: (carpeta, [(fieldKey, nombre, dataType, opciones)])
# Las fechas van todas en TEXT: los DATE de GHL no guardan hora, y §4 lo exige
# explícitamente para expira_en y fecha_pago. Las otras dos se hacen igual.
CARPETAS = [
    ("Apartado", [
        ("orden_id",           "Orden ID",            "TEXT",           None),
        ("sku_apartado",       "SKU apartado",        "TEXT",           None),
        # El nombre legible. sku_apartado es la clave (PV-MUJ-BOU) y ningún
        # mensaje al cliente puede decir "tu apartado de PV-MUJ-BOU".
        ("articulo_apartado",  "Artículo apartado",   "TEXT",           None),
        ("cantidad_apartada",  "Cantidad apartada",   "NUMERICAL",      None),
        ("monto_apartado",     "Monto apartado",      "NUMERICAL",      None),
        # Desplegable porque lo escriben los workflows, no el bot: la limitación
        # del playbook es que los bots no pueden escribir en SINGLE_OPTIONS.
        ("estado_apartado",    "Estado del apartado", "SINGLE_OPTIONS", ESTADOS_APARTADO),
        ("expira_en",          "Expira en",           "TEXT",           None),
    ]),
    ("Pago", [
        ("mp_preference_id",   "Mercado Pago · preference ID", "TEXT", None),
        ("liga_pago",          "Liga de pago",                 "TEXT", None),
        ("fecha_pago",         "Fecha de pago",                "TEXT", None),
    ]),
    ("Envío", [
        ("ciudad",             "Ciudad",            "TEXT", None),
        ("estado_mx",          "Estado",            "TEXT", None),
        # SP05 manda al almacén "nombre, cantidad, destino y CP", y la regla 8
        # del Global Prompt obliga a pedir el código postal. Necesita dónde vivir.
        ("codigo_postal",      "Código postal",     "TEXT", None),
        ("sucursal_ocurre",    "Sucursal a ocurre", "TEXT", None),
        ("numero_guia",        "Número de guía",    "TEXT", None),
        ("fecha_envio",        "Fecha de envío",    "TEXT", None),
    ]),
    ("Atribución", [
        ("canal_origen",           "Canal de origen",        "TEXT", None),
        ("utm_source",             "UTM source",             "TEXT", None),
        ("utm_medium",             "UTM medium",             "TEXT", None),
        ("utm_campaign",           "UTM campaign",           "TEXT", None),
        ("fecha_primer_contacto",  "Fecha de primer contacto", "TEXT", None),
    ]),
]

# §5 — los 8 custom values. Sólo horas_apartado se puede llenar hoy; el resto
# depende de n8n (eslabón 0.3) y de datos que el cliente todavía no manda.
# PENDIENTE a propósito: si un workflow lo usa antes de tiempo, falla ruidoso.
# Una URL de relleno con forma de URL fallaría en silencio o pegaría en otro lado.
PENDIENTE = "PENDIENTE"
CUSTOM_VALUES = [
    ("url_n8n_consultar_stock",  PENDIENTE),
    ("url_n8n_crear_apartado",   PENDIENTE),
    ("url_n8n_buscar_sucursal",  PENDIENTE),
    ("url_n8n_generar_guia",     PENDIENTE),
    ("url_n8n_rastrear",         PENDIENTE),
    ("whatsapp_almacen",         PENDIENTE),
    ("email_duenos",             PENDIENTE),
    ("horas_apartado",           "24"),
]


def falla(resp, que):
    """Los 422 de GHL dicen exactamente qué propiedad sobra. Hay que leerlos."""
    print(f"  ✗ {que} → {resp.status_code}")
    print(f"    {resp.text[:400]}")


def main():
    seco = "--dry-run" in sys.argv
    token = os.environ.get("GHL_API_KEY")
    loc = os.environ.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("Faltan GHL_API_KEY y/o GHL_LOCATION_ID en el entorno.")

    # urllib lo bloquea Cloudflare con un 1010 por el user-agent; requests pasa.
    H = {"Authorization": f"Bearer {token}", "Version": "2021-07-28",
         "Accept": "application/json", "Content-Type": "application/json"}
    url_cf = f"{BASE}/locations/{loc}/customFields"
    url_cv = f"{BASE}/locations/{loc}/customValues"
    url_pl = f"{BASE}/opportunities/pipelines"

    r = requests.get(url_cf, headers=H, timeout=30)
    if not r.ok:
        sys.exit(f"No se pudo leer la cuenta: {r.status_code} {r.text[:300]}")
    campos_previos = r.json().get("customFields", [])
    claves = {c.get("fieldKey") for c in campos_previos}

    valores_previos = requests.get(url_cv, headers=H, timeout=30).json().get("customValues", [])
    nombres_cv = {v.get("name") for v in valores_previos}

    pipes = requests.get(f"{url_pl}?locationId={loc}", headers=H, timeout=30).json().get("pipelines", [])
    hay_pipeline = any(p.get("name") == PIPELINE for p in pipes)

    todos = [c for _, cs in CARPETAS for c in cs]
    faltan_campos = [c for c in todos if f"contact.{c[0]}" not in claves]
    faltan_cv = [v for v in CUSTOM_VALUES if v[0] not in nombres_cv]

    print(f"Cuenta {loc}")
    print(f"  pipeline «{PIPELINE}»: {'ya existe' if hay_pipeline else 'por crear'}")
    print(f"  campos: {len(faltan_campos)} por crear, {len(todos) - len(faltan_campos)} ya estaban")
    print(f"  custom values: {len(faltan_cv)} por crear, {len(CUSTOM_VALUES) - len(faltan_cv)} ya estaban")
    if seco:
        for k, n, t, _ in faltan_campos:
            print(f"    · {k:24} {t:15} {n}")
        for n, v in faltan_cv:
            print(f"    · {n:24} = {v}")
        return

    errores = 0

    # ── Pipeline ─────────────────────────────────────────────────────────
    if not hay_pipeline:
        cuerpo = {
            "name": PIPELINE,
            "locationId": loc,          # el POST lo exige (el PUT lo prohíbe)
            "stages": [
                # sin position responde 422 sin decir cuál falta
                {"name": nombre, "position": i} for i, nombre in enumerate(ETAPAS)
            ],
            # nacen en false: sin esto el pipeline no aparece en los tableros
            "showInFunnel": True,
            "showInPieChart": True,
        }
        r = requests.post(url_pl, headers=H, json=cuerpo, timeout=30)
        if r.ok:
            print(f"  ✓ pipeline «{PIPELINE}» con {len(ETAPAS)} etapas")
        else:
            falla(r, "pipeline"); errores += 1

    # ── Carpetas y campos ────────────────────────────────────────────────
    for carpeta, campos in CARPETAS:
        pend = [c for c in campos if c in faltan_campos]
        if not pend:
            continue
        # El GET de customFields no lista carpetas, así que la de una carpeta ya
        # usada se deduce del parentId que comparten sus campos.
        padre = next((c.get("parentId") for c in campos_previos
                      if c.get("fieldKey") in {f"contact.{k}" for k, *_ in campos}
                      and c.get("parentId")), None)
        if not padre:
            r = requests.post(url_cf, headers=H, timeout=30,
                              json={"name": carpeta, "documentType": "folder"})
            if not r.ok:
                falla(r, f"carpeta «{carpeta}»"); errores += 1; continue
            d = r.json()
            # Viene envuelta en customFieldFolder, no en customField: leerla del
            # lugar equivocado devuelve None y los campos quedan fuera, en silencio.
            padre = (d.get("customFieldFolder") or d.get("customField") or d).get("id")
            if not padre:
                falla(r, f"id de la carpeta «{carpeta}»"); errores += 1; continue
            print(f"  ✓ carpeta «{carpeta}» → {padre}")

        for clave, nombre, tipo, opciones in pend:
            cuerpo = {"name": nombre, "dataType": tipo, "fieldKey": clave,
                      "documentType": "field", "parentId": padre}
            if opciones:
                # options es lo que exige el POST; picklistOptions es de lectura
                cuerpo["options"] = opciones
            r = requests.post(url_cf, headers=H, json=cuerpo, timeout=30)
            if r.ok:
                print(f"    ✓ {clave:24} {tipo:15} {nombre}")
            else:
                falla(r, clave); errores += 1

    # ── Custom values ────────────────────────────────────────────────────
    for nombre, valor in faltan_cv:
        r = requests.post(url_cv, headers=H, json={"name": nombre, "value": valor}, timeout=30)
        if r.ok:
            print(f"  ✓ {nombre:24} = {valor}")
        else:
            falla(r, nombre); errores += 1

    print(f"\nErrores: {errores}")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
