#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea en GoHighLevel los campos personalizados del formulario de alta de subcuenta.

Los deja todos dentro de una carpeta, para poder arrastrarlos de un jalón al armar
el formulario en la interfaz. El formulario en sí no se puede construir por API.

Uso:
    export GHL_API_KEY='pit-...'
    export GHL_LOCATION_ID='...'
    python3 scripts/crear-campos-alta-subcuenta.py [--dry-run]

Es idempotente: deduplica por fieldKey, así que correrlo dos veces no duplica nada.
Las credenciales se leen del entorno y nunca se escriben a disco.
"""
import os
import sys

import requests

BASE = "https://services.leadconnectorhq.com"
CARPETA = "Alta de subcuenta"

PAISES = ["México", "Estados Unidos", "Otro"]

ZONAS = [
    "Centro de México — America/Mexico_City",
    "Monterrey y Nuevo Laredo — America/Monterrey",
    "Chihuahua — America/Chihuahua",
    "Tijuana — America/Tijuana",
    "Texas — America/Chicago",
]

# (fieldKey, nombre, dataType, opciones)
# El fieldKey va PELADO, sin "contact.": GHL le antepone el prefijo solo.
CAMPOS = [
    # ── Datos del negocio: van tal cual al alta de la subcuenta ──────────
    ("alta_nombre_negocio",     "Nombre del negocio",         "TEXT",           None),
    ("alta_giro_negocio",       "Giro o nicho del negocio",   "TEXT",           None),
    ("alta_telefono_negocio",   "Teléfono del negocio",       "PHONE",          None),
    ("alta_direccion_negocio",  "Dirección del negocio",      "TEXT",           None),
    ("alta_ciudad_negocio",     "Ciudad del negocio",         "TEXT",           None),
    ("alta_estado_negocio",     "Estado o provincia",         "TEXT",           None),
    ("alta_pais_negocio",       "País del negocio",           "SINGLE_OPTIONS", PAISES),
    # TEXT y no NUMERICAL: los CP mexicanos que empiezan en cero perderían el dígito
    ("alta_codigo_postal",      "Código postal",              "TEXT",           None),
    ("alta_sitio_web",          "Sitio web",                  "URL",            None),
    ("alta_zona_horaria",       "Zona horaria",               "SINGLE_OPTIONS", ZONAS),

    # ── Administrador de la subcuenta ────────────────────────────────────
    # Son campos propios y no el nombre/correo estándar del contacto, porque
    # quien llena el formulario no tiene por qué ser el administrador.
    ("alta_admin_nombre",       "Nombre del administrador",   "TEXT",           None),
    ("alta_admin_apellido",     "Apellido del administrador", "TEXT",           None),
    # No existe dataType EMAIL en GHL
    ("alta_admin_correo",       "Correo del administrador",   "TEXT",           None),

    # ── Los tres usuarios de la subcuenta ────────────────────────────────
    # Planos y no un TEXTBOX_LIST: así cada dato se lee y escribe por separado
    # desde un workflow.
    ("alta_usuario1_nombre",    "Usuario 1 · Nombre completo", "TEXT",  None),
    ("alta_usuario1_correo",    "Usuario 1 · Correo",          "TEXT",  None),
    ("alta_usuario1_telefono",  "Usuario 1 · Teléfono",        "PHONE", None),
    ("alta_usuario2_nombre",    "Usuario 2 · Nombre completo", "TEXT",  None),
    ("alta_usuario2_correo",    "Usuario 2 · Correo",          "TEXT",  None),
    ("alta_usuario2_telefono",  "Usuario 2 · Teléfono",        "PHONE", None),
    ("alta_usuario3_nombre",    "Usuario 3 · Nombre completo", "TEXT",  None),
    ("alta_usuario3_correo",    "Usuario 3 · Correo",          "TEXT",  None),
    ("alta_usuario3_telefono",  "Usuario 3 · Teléfono",        "PHONE", None),

    # ── Cierre ───────────────────────────────────────────────────────────
    ("alta_notas",              "Algo más que debamos saber",  "LARGE_TEXT", None),
]


def cabeceras(token):
    return {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def falla(resp, que):
    """Los 422 de GHL dicen exactamente qué propiedad sobra. Hay que leerlos."""
    print(f"  ✗ {que} → {resp.status_code}")
    print(f"    {resp.text[:500]}")
    return None


def main():
    seco = "--dry-run" in sys.argv
    token = os.environ.get("GHL_API_KEY")
    loc = os.environ.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("Faltan GHL_API_KEY y/o GHL_LOCATION_ID en el entorno.")

    H = cabeceras(token)
    url = f"{BASE}/locations/{loc}/customFields"

    # urllib lo bloquea Cloudflare con un 1010 por el user-agent; requests pasa.
    r = requests.get(url, headers=H, timeout=30)
    if not r.ok:
        sys.exit(f"No se pudo leer la cuenta: {r.status_code} {r.text[:300]}")
    previos = r.json().get("customFields", [])

    # Deduplicar por fieldKey, NUNCA por nombre: dos campos cuyo nombre sólo
    # difiere en mayúsculas son campos distintos y conviven.
    existentes = {c.get("fieldKey") for c in previos}
    print(f"Cuenta {loc} · {len(previos)} campos antes de empezar")

    pendientes = [c for c in CAMPOS if f"contact.{c[0]}" not in existentes]
    saltados = len(CAMPOS) - len(pendientes)
    print(f"Por crear: {len(pendientes)} · ya existían: {saltados}")
    if seco:
        for k, n, t, _ in pendientes:
            print(f"  · {k:26} {t:15} {n}")
        return
    if not pendientes:
        print("Nada que hacer.")
        return

    # ── La carpeta ───────────────────────────────────────────────────────
    # El GET de customFields NO lista carpetas, así que no hay forma de
    # preguntar si ya existe: se deduce del parentId que comparten los campos
    # que ya están dentro.
    padre = None
    dentro = [c.get("parentId") for c in previos
              if (c.get("fieldKey") or "").startswith("contact.alta_")]
    if dentro and dentro[0]:
        padre = dentro[0]
        print(f"Carpeta ya existente: {padre}")
    else:
        r = requests.post(url, headers=H, timeout=30,
                          json={"name": CARPETA, "documentType": "folder"})
        if not r.ok:
            falla(r, f"carpeta «{CARPETA}»")
            sys.exit(1)
        # La respuesta viene envuelta en customFieldFolder, no en customField.
        # Leerla del lugar equivocado devuelve None y los campos se crean fuera
        # de la carpeta sin que nadie se queje.
        d = r.json()
        padre = (d.get("customFieldFolder") or d.get("customField") or d).get("id")
        if not padre:
            sys.exit(f"La carpeta se creó pero no se pudo leer su id: {d}")
        print(f"Carpeta «{CARPETA}» creada: {padre}")

    # ── Los campos ───────────────────────────────────────────────────────
    hechos, fallidos = 0, 0
    for clave, nombre, tipo, opciones in pendientes:
        cuerpo = {
            "name": nombre,
            "dataType": tipo,
            "fieldKey": clave,       # pelado: GHL antepone "contact."
            "documentType": "field",
            "parentId": padre,
        }
        if opciones:
            # options es lo que exige el POST; picklistOptions es lo que
            # devuelve el GET y se rechaza con 422.
            cuerpo["options"] = opciones
        if tipo == "URL":
            # Sin urlValidation responde 400 «urlValidation is required»,
            # y es un objeto, no un booleano.
            cuerpo["urlValidation"] = {"mode": "allow_all"}

        r = requests.post(url, headers=H, json=cuerpo, timeout=30)
        if r.ok:
            hechos += 1
            print(f"  ✓ {clave:26} {tipo:15} {nombre}")
        else:
            fallidos += 1
            falla(r, clave)

    print(f"\nCreados: {hechos} · fallidos: {fallidos} · saltados: {saltados}")
    if fallidos:
        sys.exit(1)


if __name__ == "__main__":
    main()
