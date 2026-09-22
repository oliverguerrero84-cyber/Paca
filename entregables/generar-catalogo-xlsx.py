# -*- coding: utf-8 -*-
import csv, io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

VERDE_OSC = '0D5138'; VERDE     = '15855A'; VERDE_CLA = 'ECFDF5'
AMARILLO  = 'FFF3C4'; GRIS_TXT  = '64748B'; BORDE_GRIS= 'E2E8F0'
F = 'Arial'

cat = list(csv.DictReader(io.open('data/catalogo.csv', encoding='utf-8')))
assert len(cat) == 30, len(cat)

wb = Workbook(); ws = wb.active; ws.title = 'Catálogo menudeo'

ENC = ['Clave', 'Artículo', 'Temporada', 'Categoría', 'Calidad', 'Tallas',
       'Precio de venta\nal menudeo (MXN)', 'Piezas aprox.\npor paca',
       'Pacas para\nmenudeo', 'Notas']
ANCHO = [12, 30, 12, 16, 11, 16, 17, 14, 13, 30]
LLENAR = ('G', 'H', 'I')                      # columnas amarillas
FILA_ENC, FILA_EJ, FILA_1 = 7, 8, 9
FILA_N = FILA_1 + len(cat) - 1                # 40

for i, a in enumerate(ANCHO, 1):
    ws.column_dimensions[get_column_letter(i)].width = a

def pon(celda, valor, **kw):
    c = ws[celda]; c.value = valor
    c.font = Font(name=F, size=kw.get('size', 10), bold=kw.get('bold', False),
                  italic=kw.get('italic', False),
                  color=kw.get('color', '1E293B'))
    if kw.get('fill'):
        c.fill = PatternFill('solid', fgColor=kw['fill'])
    c.alignment = Alignment(horizontal=kw.get('h', 'left'),
                            vertical=kw.get('v', 'center'),
                            wrap_text=kw.get('wrap', False))
    if kw.get('fmt'):
        c.number_format = kw['fmt']
    return c

# ── Encabezado ────────────────────────────────────────────────────────────
ws.merge_cells('A1:J1')
pon('A1', 'Catálogo de menudeo — pacas de ropa americana', size=15, bold=True,
    color=VERDE_OSC)
ws.row_dimensions[1].height = 26
ws.merge_cells('A2:J2')
pon('A2', 'Sólo hay que llenar las tres columnas amarillas: el precio de venta, '
          'las piezas que trae cada paca y cuántas pacas destinan al menudeo.',
    size=11, bold=True)
ws.merge_cells('A3:J3')
pon('A3', 'Lo demás ya viene capturado. Pueden mandarlo por partes: lo que '
          'todavía no sepan, déjenlo en blanco.  ·  786 Marketing',
    size=10, color=GRIS_TXT)

# Contadores en vivo
pon('A5', 'Artículos con precio:', size=10, bold=True)
pon('C5', '=COUNT(G%d:G%d)&" de 30"' % (FILA_1, FILA_N), size=10, bold=True,
    color=VERDE, h='left')
pon('E5', 'Total de pacas para menudeo:', size=10, bold=True)
pon('H5', '=SUM(I%d:I%d)' % (FILA_1, FILA_N), size=10, bold=True, color=VERDE,
    h='left', fmt='#,##0')

# ── Cabecera de la tabla ──────────────────────────────────────────────────
ws.row_dimensions[FILA_ENC].height = 32
for i, t in enumerate(ENC, 1):
    col = get_column_letter(i)
    c = pon('%s%d' % (col, FILA_ENC), t, size=10, bold=True, color='FFFFFF',
            fill=AMARILLO if col in LLENAR else VERDE,
            h='center', wrap=True)
    if col in LLENAR:
        c.font = Font(name=F, size=10, bold=True, color=VERDE_OSC)

for col, nota in (('G', 'El precio en pesos al que venden esta paca al menudeo, '
                        'ya con el envío incluido.'),
                  ('H', 'Aproximado de prendas que trae la paca. Es de lo que '
                        'más preguntan los clientes.'),
                  ('I', 'Cuántas pacas de este artículo apartan para menudeo. '
                        'Es el dato que evita vender de más.')):
    ws['%s%d' % (col, FILA_ENC)].comment = Comment(nota, '786 Marketing',
                                                   width=260, height=90)

# ── Fila de ejemplo ───────────────────────────────────────────────────────
EJ = ['EJEMPLO', '— así se llena —', 'Verano', 'Mujer', 'Boutique',
      'CH, M, G, XL', 6300, 200, 15, '← fila de muestra, bórrenla']
for i, v in enumerate(EJ, 1):
    col = get_column_letter(i)
    pon('%s%d' % (col, FILA_EJ), v, size=9, italic=True, color=GRIS_TXT,
        fill='F1F5F9', h='right' if col in LLENAR else 'left',
        fmt='$#,##0' if col == 'G' else ('#,##0' if col in ('H', 'I') else None))

# ── Los 30 artículos ──────────────────────────────────────────────────────
borde = Border(bottom=Side('thin', color=BORDE_GRIS))
for n, a in enumerate(cat):
    f = FILA_1 + n
    base = [a['sku'], a['nombre_display'], a['temporada'], a['categoria'],
            a['calidad'], a['tallas']]
    for i, v in enumerate(base, 1):
        pon('%s%d' % (get_column_letter(i), f), v, size=10,
            bold=(i == 2), color='1E293B' if i == 2 else '334155')
    for col, fmt in (('G', '$#,##0'), ('H', '#,##0'), ('I', '#,##0')):
        pon('%s%d' % (col, f), None, size=10, fill=AMARILLO, h='right', fmt=fmt)
    pon('J%d' % f, None, size=10)
    for i in range(1, 11):
        ws['%s%d' % (get_column_letter(i), f)].border = borde

# ── Validación: sólo números, y positivos ─────────────────────────────────
rango = '%d:%d' % (FILA_1, FILA_N)
for col, tipo, op, f1, msg in (
        ('G', 'decimal', 'greaterThan', '0', 'El precio debe ser un número mayor que cero, en pesos.'),
        ('H', 'whole',   'greaterThan', '0', 'Las piezas deben ser un número entero mayor que cero.'),
        ('I', 'whole',   'greaterThanOrEqual', '0', 'Las pacas deben ser un número entero. Si no destinan ninguna, pongan 0.')):
    dv = DataValidation(type=tipo, operator=op, formula1=f1, allow_blank=True,
                        showErrorMessage=True, errorTitle='Dato no válido', error=msg)
    ws.add_data_validation(dv)
    dv.add('%s%s' % (col, rango.replace(':', ':%s' % col)))

ws.freeze_panes = 'A%d' % FILA_EJ
ws.sheet_view.showGridLines = False
ws.auto_filter.ref = 'A%d:J%d' % (FILA_ENC, FILA_N)
ws.print_title_rows = '%d:%d' % (FILA_ENC, FILA_ENC)
ws.page_setup.orientation = 'landscape'
ws.page_setup.fitToWidth = 1

OUT = 'entregables/catalogo-menudeo-para-llenar.xlsx'
wb.save(OUT)
print('escrito:', OUT, '· filas', FILA_1, 'a', FILA_N)
