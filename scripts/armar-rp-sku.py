# RP-SKU · Respaldo determinístico de la detección de paca
#
# POR QUÉ EXISTE. Las acciones de Conversation AI en GHL se ejecutan de forma
# intermitente (plantilla GALK, docs/18-arquitectura-asistentes.md §1): el bot lee bien,
# contesta bien, y la acción que escribe `sku_elegido` simplemente no corre ese turno.
# No da error. El cliente se queda esperando una ficha que nunca sale.
#
# Este workflow llega al MISMO campo con el MISMO valor, sin IA, por palabras clave.
# Si el bot funcionó, se sale callado. Si falló, salva la venta.
#
#   [Trigger: Customer Replied + «el mensaje contiene alguna de» + WhatsApp]  ← lo conecta Germán
#     → Wait 30 s                        le damos su turno al bot, que entiende mejor
#     → If sku_elegido está vacío        si el bot ya escribió, aquí se sale
#         └─ árbol: categoría → (temporada) → (calidad) → escribe sku_elegido
#
# LA FORMA DEL ÁRBOL SALE DEL CATÁLOGO, NO DE UNA SUPOSICIÓN. Medido el 14 oct sobre
# data/catalogo.csv: 6 de los 30 SKUs se identifican con la pura categoría (disfraz,
# suéter navideño, ropa de hospital, ropa de casa, vestido de fiesta, playera), 6 necesitan
# dos dimensiones y 18 necesitan las tres. Por eso el árbol sólo pregunta la dimensión que
# de verdad hace falta en cada rama, en vez de bajar siempre tres niveles.
#
# ⚠️ LAS PALABRAS CLAVE DE AQUÍ SON PROVISIONALES. La plantilla es explícita: se sacan de
# las conversaciones reales de los clientes, no se inventan. Hoy no hay conversaciones.
# Éstas son un piso razonable para arrancar y HAY QUE CORREGIRLAS con tráfico real.
#
# ⚠️ El filtro de GHL compara PALABRAS COMPLETAS, no subcadenas: una lista de raíces
# («melamin», «chamarr») no dispara nunca. Por eso cada lista trae variantes, plurales,
# la versión sin tilde y los errores de tipeo frecuentes.
#
# ⚠️ ESTE SCRIPT NUNCA SE HA CORRIDO CONTRA LA CUENTA. Lo escribe Germán con `!`.
# Correrlo primero con --dry-run y revisar el árbol impreso.
#
# Uso (desde la raíz del repo):
#   python scripts/armar-rp-sku.py --dry-run
#   python scripts/armar-rp-sku.py <carpeta-respaldo>          (escribe de verdad)
import csv
import importlib.util
import os
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOGO = "data/catalogo.csv"
NOMBRE = "RP-SKU · Respaldo de detección"
CAMPO = "sku_elegido"
ESPERA_SEG = 30

# ── Palabras clave ────────────────────────────────────────────────────────────
# Criterio para dejar fuera una palabra: que aparezca en conversaciones que NO son
# sobre esa paca. «casa» y «hogar» se cayeron porque medio flujo de envío dice «a mi
# casa»; «interior» y «noche», por lo mismo. Más vale que el respaldo no dispare a
# que dispare mal: cuando no dispara, el bot sigue preguntando; cuando dispara mal,
# el cliente recibe la ficha equivocada.
CATEGORIA = {
    "Mujer":            ["mujer", "mujeres", "dama", "damas", "señora", "senora",
                         "señoras", "senoras", "femenina", "femenino"],
    "Hombre":           ["hombre", "hombres", "caballero", "caballeros", "varon",
                         "varón", "masculina", "masculino"],
    "Niño":             ["niño", "nino", "niños", "ninos", "niña", "nina", "niñas",
                         "ninas", "infantil", "bebe", "bebé", "bebes", "bebés"],
    "Corsé":            ["corse", "corsé", "corses", "corsés", "lenceria", "lencería",
                         "brasier", "brasieres", "pantaleta", "pantaletas", "pijama",
                         "pijamas"],
    "Chamarra":         ["chamarra", "chamarras", "chamara", "chamaras", "chaqueta",
                         "chaquetas", "abrigo", "abrigos"],
    "Mixta Plus":       ["plus", "curvy", "extragrande", "extragrandes"],
    "Playera":          ["playera", "playeras", "camiseta", "camisetas", "polo", "polos"],
    "Vestido de fiesta": ["vestido", "vestidos", "fiesta", "gala", "xv", "quinceañera",
                          "quinceanera"],
    "Ropa de hospital": ["hospital", "scrub", "scrubs", "medico", "médico", "medicos",
                         "médicos", "enfermera", "enfermeria", "enfermería",
                         "quirurgico", "quirúrgico"],
    "Ropa de casa":     ["sabana", "sábana", "sabanas", "sábanas", "cortina", "cortinas",
                         "cojin", "cojín", "cojines", "blancos", "mantel", "manteles"],
    "Disfraz":          ["disfraz", "disfraces", "halloween", "cosplay"],
    "Suéter navideño":  ["navideño", "navideno", "navideños", "navidenos", "navidad",
                         "sueter", "suéter", "sueters", "suéters"],
}

TEMPORADA = {
    "Verano":   ["verano", "calor", "caluroso", "veraniego", "veraniega", "fresco",
                 "fresca", "ligera", "ligero"],
    "Invierno": ["invierno", "frio", "frío", "invernal", "abrigador", "abrigadora",
                 "caliente", "calientita"],
}

# «Estándar» no lleva palabras: es la calidad de las pacas que sólo tienen una, así que
# nadie la nombra. Si una rama sólo ofrece Estándar, el árbol ni pregunta.
CALIDAD = {
    "Boutique": ["boutique", "butique", "butik", "botique", "boutiqe"],
    "Premium":  ["premium", "premiun", "premium", "premier"],
    "Especial": ["especial", "especiales", "economica", "económica", "barata", "baratas"],
    "Estándar": [],
}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower().strip()


def cargar():
    with open(CATALOGO, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def arbol(filas):
    """Devuelve el árbol tal como el catálogo lo pide: sólo baja el nivel que hace falta."""
    salida = []
    cats = {}
    for x in filas:
        cats.setdefault(x["categoria"], []).append(x)

    for cat, skus in cats.items():
        temps = sorted({x["temporada"] for x in skus})
        cals = sorted({x["calidad"] for x in skus})
        if len(skus) == 1:
            salida.append({"cat": cat, "hojas": [(None, None, skus[0]["sku"], skus[0]["nombre_display"])]})
        elif len(temps) == 1 and len(cals) > 1:
            salida.append({"cat": cat, "pregunta": "calidad",
                           "hojas": [(None, x["calidad"], x["sku"], x["nombre_display"]) for x in skus]})
        elif len(temps) > 1 and len(cals) == 1:
            salida.append({"cat": cat, "pregunta": "temporada",
                           "hojas": [(x["temporada"], None, x["sku"], x["nombre_display"]) for x in skus]})
        else:
            salida.append({"cat": cat, "pregunta": "temporada+calidad",
                           "hojas": [(x["temporada"], x["calidad"], x["sku"], x["nombre_display"]) for x in skus]})
    return salida


def revisar(filas):
    """Las dos cosas que romperían esto en silencio."""
    problemas = []

    # 1. Una palabra en dos categorías manda al cliente a la ficha equivocada.
    visto = {}
    for cat, palabras in CATEGORIA.items():
        for p in palabras:
            k = norm(p)
            if k in visto and visto[k] != cat:
                problemas.append(f"«{p}» está en «{visto[k]}» y en «{cat}»")
            visto[k] = cat

    # 2. Una categoría del catálogo sin palabras clave es una paca que el respaldo
    #    nunca va a poder detectar.
    delcsv = {x["categoria"] for x in filas}
    for c in sorted(delcsv - set(CATEGORIA)):
        problemas.append(f"la categoría «{c}» del catálogo no tiene palabras clave")
    for c in sorted(set(CATEGORIA) - delcsv):
        problemas.append(f"«{c}» tiene palabras clave pero no existe en el catálogo")

    # 3. Las calidades y temporadas que el árbol va a preguntar tienen que existir.
    for col, tabla in (("calidad", CALIDAD), ("temporada", TEMPORADA)):
        for v in sorted({x[col] for x in filas}):
            if v not in tabla:
                problemas.append(f"la {col} «{v}» no tiene palabras clave")
    return problemas


def imprimir(ramas, filas):
    total_hojas = sum(len(r["hojas"]) for r in ramas)
    print(f"{NOMBRE}\n{'=' * 70}")
    print(f"Trigger:  Customer Replied + «contiene alguna de» + canal WhatsApp")
    print(f"Espera:   {ESPERA_SEG} s   ·   Guarda: sale si {CAMPO} ya tiene valor")
    print(f"Ramas:    {len(ramas)} categorías · {total_hojas} hojas · {len(filas)} SKUs en el catálogo\n")
    for r in sorted(ramas, key=lambda x: -len(x["hojas"])):
        preg = r.get("pregunta")
        print(f"  {r['cat']}  ({len(r['hojas'])} SKU" + (f", pregunta {preg}" if preg else ", directo") + ")")
        print(f"     palabras: {', '.join(CATEGORIA[r['cat']])}")
        for temp, cal, sku, nombre in sorted(r["hojas"]):
            cond = " · ".join(x for x in (temp, cal) if x) or "sin condición"
            print(f"       {cond:<22} → {CAMPO} = {sku:<12} ({nombre})")
        print()


def main():
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not dry and not args:
        sys.exit("uso: python scripts/armar-rp-sku.py <carpeta-respaldo> [--dry-run]")

    filas = cargar()
    problemas = revisar(filas)
    ramas = arbol(filas)
    imprimir(ramas, filas)

    if problemas:
        print("NO SE ESCRIBE NADA — hay que arreglar esto primero:")
        for p in problemas:
            print("  ✗", p)
        sys.exit(1)
    print("✓ sin palabras repetidas entre categorías, y el catálogo está cubierto completo")

    cubiertos = {h[2] for r in ramas for h in r["hojas"]}
    faltan = {x["sku"] for x in filas} - cubiertos
    assert not faltan, f"SKUs sin hoja: {faltan}"
    print(f"✓ los {len(cubiertos)} SKUs tienen hoja\n")

    if dry:
        print("--dry-run: nada se escribió. Para aplicar: python scripts/armar-rp-sku.py <carpeta-respaldo>")
        return

    # ── Escritura ─────────────────────────────────────────────────────────────
    # Se clona un nodo update_contact_field que ya viva en la cuenta en vez de
    # fabricarlo: «molde antes que invento». Si no hay ninguno, se para y se dice,
    # porque un nodo inventado se guarda, se ve bien y después no ejecuta.
    s = importlib.util.spec_from_file_location("aw", "scripts/armar-workflows.py")
    aw = importlib.util.module_from_spec(s)
    s.loader.exec_module(aw)
    os.makedirs(args[0], exist_ok=True)
    aw.Interna(aw.jwt_de(os.environ["GHL_FIREBASE_REFRESH_TOKEN"]),
               os.environ["GHL_LOCATION_ID"])
    sys.exit(
        "FALTA LA ESCRITURA.\n"
        "El árbol de arriba es correcto y está verificado, pero el molde del nodo\n"
        "«update_contact_field» con una condición If encima todavía no existe en la\n"
        "cuenta para clonarlo. Hay que armar UNA rama a mano en la UI, leerla por API\n"
        "y clonar esa forma — como se hizo con AP04. Inventar el nodo aquí es\n"
        "exactamente lo que docs/16-guias-workflows.md dice que no se haga."
    )


if __name__ == "__main__":
    main()
