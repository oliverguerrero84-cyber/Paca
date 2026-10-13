# -*- coding: utf-8 -*-
"""Genera propuesta/propuesta-contenido-usd.html desde la de pesos.

Se corre desde la raiz del repo, y es idempotente: reconstruye el archivo
completo desde la version en pesos cada vez. La de pesos es la unica fuente
de verdad; si cambia un precio, se cambia ALLA y se vuelve a correr esto.

Antes de escribir verifica que la derivacion siga cerrando por los dos
caminos: el tier del proveedor mas su propio incremento, contra convertir
nuestro precio directo. Si el redondeo la rompe, aborta — esa suma es el
argumento entero de la propuesta. A 18.20 cierra; a 18.50 no.
Ver docs/17-precotizacion-contenido.md seccion 3bis.
"""
import re, math, sys

TC = 18.20   # referencia Banxico del 8 oct 2026
def usd(mxn):                       # hacia arriba, al decimo
    return int(math.ceil((mxn / TC) / 10.0) * 10)

# ── los tiers del proveedor, convertidos ─────────────────────────────
T2, T3a, T3b, TCAMP = usd(5000), usd(7000), usd(8000), usd(10000)
INC_ESE, INC_COM = TCAMP - T3a, TCAMP - T3b      # su incremento por campanas
ESE, COM = T2 + INC_ESE, T3b + INC_COM           # derivados de SU lista
ARR  = usd(15000)
BASE = usd(7000)    # la reactivacion de la base, concepto aparte desde el 13 oct

print(f"tipo de cambio {TC}  ·  redondeo hacia arriba al decimo\n")
print(f"  sus tiers:   2 redes ${T2}   3 redes 8-12 ${T3a}   3 redes 20 ${T3b}   con campanas ${TCAMP}")
print(f"  su incremento por campanas: ${INC_COM} a ${INC_ESE}")
print(f"  Esencial = {T2} + {INC_ESE} = ${ESE}      Completo = {T3b} + {INC_COM} = ${COM}")
print(f"  arranque ${ARR}   ·   despertar la base ${BASE}\n")

# la derivacion tiene que coincidir con convertir nuestro precio directo
assert ESE == usd(8000),  f"Esencial no cuadra: derivado {ESE} vs directo {usd(8000)}"
assert COM == usd(10000), f"Completo no cuadra: derivado {COM} vs directo {usd(10000)}"

ac = {}
# La mensualidad empieza en el MES 3 (Brenda, 13 oct): el ano 1 lleva 10, no 12.
for nom, mes in (("Esencial", ESE), ("Completo", COM)):
    ac[nom] = (ARR + mes*10, mes*12, ARR + mes*10 + mes*12)
ac["Proveedor"] = (TCAMP*12, TCAMP*12, TCAMP*12*2)
# El acumulado ya NO se muestra en el documento (Oliver, 11 oct: confundia).
# Se sigue calculando aqui porque es como se comprueban los tres argumentos
# que si quedaron escritos. No borrar.
for nom, (a1, a2, dos) in ac.items():
    print(f"  {nom:10} ano1 ${a1:,}  del ano2 ${a2:,}  dos anos ${dos:,}")

# los tres argumentos del documento, verificados
assert ac["Completo"][1] == ac["Proveedor"][1], "Completo ya no queda a la par del ano 2"
assert ac["Completo"][0] < ac["Proveedor"][0], "Completo deberia quedar debajo el ano 1"
assert ac["Esencial"][0] < ac["Proveedor"][0], "Esencial deberia quedar debajo el ano 1"
# El documento dice dos cosas con el MISMO token "$2,000": el incremento que su
# lista cobra por campanas, y cuanto queda Esencial por debajo del mensual que
# pagan hoy. Si al convertir dejaran de ser el mismo numero, una de las dos
# frases quedaria mintiendo en dolares.
assert TCAMP - ESE == INC_COM, (
    f"'Esencial queda X por debajo' ({TCAMP-ESE}) ya no es el mismo numero que "
    f"el incremento por campanas ({INC_COM}): revisar las dos frases")
print("\n✓ los tres argumentos del documento se sostienen en dolares")

# ── mapa MXN -> USD, token por token ─────────────────────────────────
MAPA = {
    "$5,000":  f"${T2}",        # su tier de 2 redes
    "$8,000":  f"${ESE}",       # nuestro Esencial, y tambien su tier de 3 redes x 20
    "$10,000": f"${COM}",       # nuestro Completo, y tambien su paquete con campanas
    "$3,000":  f"${INC_ESE}",   # su incremento por campanas, columna Esencial
    "$2,000":  f"${INC_COM}",   # su incremento por campanas, columna Completo
    "$15,000": f"${ARR}",       # el arranque
    "$7,000":  f"${BASE}",      # despertar la base, aparte y opcional
}
s = open("propuesta/propuesta-contenido.html", encoding="utf-8").read()
sin_mapa = {t for t in re.findall(r"\$[\d,]*\d", s)} - set(MAPA)
if sin_mapa:
    print("\nABORTA — cifras sin traducir:", sin_mapa); sys.exit(1)
s = re.sub(r"\$[\d,]*\d", lambda m: MAPA[m.group(0)], s)
print(f"\n{len(MAPA)} cifras traducidas, ninguna suelta")

# ── la prosa que habla de moneda ─────────────────────────────────────
TCTXT = "18.20 pesos por dólar"
FECHA_TC = "8 de octubre de 2026"
cambios = [
 ("<title>Contenido y campañas — Propuesta</title>",
  "<title>Contenido y campañas — Propuesta en dólares</title>"),
 ("   Fecha: 2026-10-09 · Revisión 2",
  f"   Fecha: 2026-10-11 · Revisión 2 · EN DÓLARES\n"
  f"   Gemela de propuesta-contenido.html (en pesos). Las cifras salen de\n"
  f"   esa lista al tipo de cambio de referencia de Banxico del {FECHA_TC}\n"
  f"   ({TCTXT}), redondeadas hacia arriba al décimo. Si se toca un precio,\n"
  f"   se toca en la de PESOS y se regenera\n"
  f"   esta con scripts/convertir-propuesta-usd.py \u2014 no a mano, se sobrescribe."),
 ("""      Dos niveles, para que tengan margen de maniobra con el cliente. En pesos
      mexicanos, y sin lo que se le paga a Meta por los anuncios: eso va aparte y lo define
      el presupuesto que quieran poner.""",
  """      Dos niveles, para que tengan margen de maniobra con el cliente. En dólares
      americanos, y sin lo que se le paga a Meta por los anuncios: eso va aparte y lo define
      el presupuesto que quieran poner."""),
 ("""      La atribución va en los dos niveles. No es un extra que se cobre aparte: es la razón
      de la propuesta.""",
  f"""      La atribución va en los dos niveles. No es un extra que se cobre aparte: es la razón
      de la propuesta.
    </p>
    <p class="nota">
      <strong>Precio fijo en dólares.</strong> Equivale a nuestra lista en pesos al tipo de
      cambio de referencia del Banco de México del {FECHA_TC} —{TCTXT}—, redondeado hacia
      arriba. Al ser precio fijo, no se recalcula cada mes."""),
 ("""      No pusimos un precio y después buscamos cómo justificarlo. Tomamos la lista que nos
      compartieron y sumamos sus propias partes. Por eso los dos mensuales caen exacto donde
      caen.""",
  f"""      No pusimos un precio y después buscamos cómo justificarlo. Tomamos la lista que nos
      compartieron y sumamos sus propias partes. Por eso los dos mensuales caen exacto donde
      caen. Los montos de su lista van convertidos al mismo tipo de cambio ({TCTXT}), para
      que la comparación sea de manzanas con manzanas."""),
 ("&middot; 9 de octubre de 2026 &middot; 786 Marketing</p>",
  "&middot; 11 de octubre de 2026 &middot; 786 Marketing</p>"),
 ("""y los nuestros antes de su margen.</p>""",
  f"""y los nuestros antes de su margen.</p>
    <p style="margin-top:9px">Cifras en <strong>dólares americanos</strong>, al tipo de cambio de referencia de Banxico del {FECHA_TC}: {TCTXT}. La versión en pesos es el documento gemelo.</p>"""),
]
for viejo, nuevo in cambios:
    assert s.count(viejo) == 1, f"{s.count(viejo)} coincidencias: {viejo[:60]!r}"
    s = s.replace(viejo, nuevo)

open("propuesta/propuesta-contenido-usd.html", "w", encoding="utf-8").write(s)
print(f"{len(cambios)} ajustes de prosa — escrito propuesta/propuesta-contenido-usd.html")
