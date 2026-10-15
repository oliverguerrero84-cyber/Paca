# Sube los videos de las fichas al media store de la subcuenta y guarda el mapa
# clave → video en data/videos-sp06.json, que es de donde lo lee scripts/armar-sp06.py.
#
# Los videos van YA COMPRIMIDOS: H.264, 720p, menos de 16 MB (el límite de WhatsApp).
# Cada archivo se llama como su clave: PV-MUJ-BOU.mp4. Los originales de Pamela son HEVC
# de 12 a 50 MB y WhatsApp no los acepta (docs/20-sp06-ficha.md §4).
#
# Idempotente: si en la carpeta ya hay un archivo con ese nombre, no lo vuelve a subir.
# Molde: ejemplos/subir_pdfs.py del kit (lo mismo, con PDFs, en GALK).
#
# El JSON no lleva credenciales: sólo la URL pública del CDN, el nombre y el peso, que es
# lo que pide el nodo whatsapp_media.
#
# Uso (desde la raíz del repo):
#   python scripts/subir-videos-sp06.py <carpeta-con-los-mp4> [--dry-run]
#   Opcional: SP06_CARPETA_MEDIA=<id de carpeta del media store>; sin ella, van a la raíz.
import json
import os
import pathlib
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

B = "https://services.leadconnectorhq.com"
SALIDA = pathlib.Path("data/videos-sp06.json")
LIMITE = 16 * 1024 * 1024


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("Uso: python scripts/subir-videos-sp06.py <carpeta-con-los-mp4> [--dry-run]")
    carpeta = pathlib.Path(args[0])
    seco = "--dry-run" in sys.argv

    videos = sorted(carpeta.glob("*.mp4"))
    grandes = [v.name for v in videos if v.stat().st_size > LIMITE]
    if grandes:
        sys.exit(f"Pesan más de 16 MB y WhatsApp no los acepta: {', '.join(grandes)}")
    print(f"{len(videos)} videos en {carpeta}")
    if seco:
        for v in videos:
            print(f"  {v.name:<16} {v.stat().st_size / 2**20:5.1f} MB")
        print("\n--dry-run: no se subió nada.")
        return

    token, loc = os.environ.get("GHL_API_KEY"), os.environ.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("Faltan GHL_API_KEY y/o GHL_LOCATION_ID en el entorno.")
    H = {"Authorization": f"Bearer {token}", "Version": "2021-07-28", "Accept": "application/json"}
    padre = os.environ.get("SP06_CARPETA_MEDIA")

    def listar():
        params = {"altId": loc, "altType": "location", "sortBy": "createdAt",
                  "sortOrder": "desc", "type": "file", "limit": 100}
        if padre:
            params["parentId"] = padre
        r = requests.get(f"{B}/medias/files", headers=H, params=params, timeout=30)
        r.raise_for_status()
        return {f.get("name"): f for f in r.json().get("files", [])}

    mapa = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {}
    existentes = listar()
    errores = 0
    for v in videos:
        sku = v.stem
        if v.name not in existentes:
            datos = {"hosted": "false", "name": v.name, "altId": loc, "altType": "location"}
            if padre:
                datos["parentId"] = padre
            with open(v, "rb") as fh:
                r = requests.post(f"{B}/medias/upload-file", headers=H, timeout=300,
                                  files={"file": (v.name, fh, "video/mp4")}, data=datos)
            if r.status_code not in (200, 201):
                print(f"  ✗ {v.name}: {r.status_code} {r.text[:150]}")
                errores += 1
                continue
            existentes = listar()
            if v.name not in existentes:
                print(f"  ✗ {v.name}: se subió pero no aparece en la carpeta, revisar a mano")
                errores += 1
                continue
            print(f"  ↑ {v.name}")
        else:
            print(f"  = {v.name} (ya estaba)")
        f = existentes[v.name]
        mapa[sku] = {"url": f.get("url"), "nombre": v.name,
                     "bytes": int(f.get("size") or v.stat().st_size)}

    SALIDA.write_text(json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"\n{len(mapa)} videos en {SALIDA}. Errores: {errores}")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
