"""Aplana las fichas de gov.co (F-103) en una tabla de requisitos, una fila por requisito.
Uso: python3 -I herramientas/aplanar_govco.py <json> <catalogo_csv> <salida_csv>"""
import csv, json, sys
src, cat, out = sys.argv[1:4]
raw = json.load(open(src, encoding='utf-8'))
cat_rows = list(csv.DictReader(open(cat, encoding='utf-8')))
nombres = {}
for r in cat_rows:
    c = r['codigo_suit'].lstrip('T')
    if c and '(registro duplicado)' not in r['nombre']:
        nombres.setdefault(c, []).append((r['n'], r['nombre'], r['modalidad_portal']))
def txt(v): return ' '.join(str(v or '').split())
rows = {}
for c, v in raw.items():
    for aud, p in v.get('por', {}).items():
        mom = {str(m['MomentoId']): (m['Orden'], txt(m['Descripcion'])) for m in p['moms']}
        for mid, d in p['det'].items():
            for a in d.get('acciones') or []:
                t = a['TipoAccionCondicion']
                items = a.get('data') or [{}]
                for i, x in enumerate(items, 1):
                    if t == 'DOCUMENTO':
                        nom = x.get('DocumentoNombre'); det = ' ; '.join(str(z) for z in [x.get('Cantidad'), x.get('UnidadCantidad'), x.get('DocumentoAnotacionAdicional'), x.get('Observacion')] if z)
                    elif t == 'VERIFICACION_INST':
                        nom = x.get('VerificacionInstDescripcion'); det = ''
                    elif t == 'FORMULARIO':
                        nom = x.get('FormularioNombre'); det = x.get('FormularioAnotacion')
                    elif t == 'PAGO':
                        nom = x.get('Descripcion'); det = ' ; '.join(str(z) for z in [x.get('TipoValor'), x.get('Valor'), x.get('CantidadSmlv')] if z is not None)
                    elif t == 'SOLICITUD':
                        nom = x.get('TipoCanal'); det = x.get('NombreCanalWeb') or x.get('UrlCanalWeb') or x.get('Correo') or ''
                    else:
                        nom = json.dumps(x, ensure_ascii=False)[:150]; det = ''
                    key = (c, mom.get(str(mid), ('', ''))[0], a['Orden'], i, t, txt(nom), txt(det), txt(a.get('Excepcion')))
                    rows.setdefault(key, set()).add(aud)
w = csv.writer(open(out, 'w', encoding='utf-8', newline=''))
w.writerow(['codigo', 'n_portal', 'nombre_portal', 'modalidad_portal', 'audiencias', 'orden_momento', 'orden_accion', 'item', 'tipo', 'nombre', 'detalle', 'excepcion'])
for k in sorted(rows, key=lambda k: (int(k[0]), k[1] or 0, k[2], k[3])):
    info = nombres.get(k[0], [('', '', '')])
    w.writerow([k[0], ';'.join(x[0] for x in info), info[0][1], info[0][2], '|'.join(sorted(rows[k]))] + list(k[1:]))
print(len(rows), 'filas;', len(raw), 'códigos;', sum(1 for c,v in raw.items() if not v.get('por')), 'sin datos')
