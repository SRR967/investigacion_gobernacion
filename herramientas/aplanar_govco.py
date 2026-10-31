"""Aplana las fichas de gov.co (F-103 + F-104, combinadas en datos/govco_fichas_combinadas_2026-10-31.json)
en una tabla de requisitos, una fila por requisito, con el nombre y la modalidad del buscador de gov.co
y el número del catálogo de la sede electrónica cuando existe.
Uso: python3 -I herramientas/aplanar_govco.py <json_combinado> <catalogo_csv> <salida_csv>"""
import csv, json, sys
src, cat, out = sys.argv[1:4]
d = json.load(open(src, encoding='utf-8'))
fichas, busc = d['fichas'], d['buscador']
catn = {}
for r in csv.DictReader(open(cat, encoding='utf-8')):
    c = r['codigo_govco'].lstrip('T')
    if c and '(registro duplicado)' not in r['nombre']:
        catn.setdefault(c, []).append(r['n'])
def txt(v): return ' '.join(str(v or '').split())
rows = {}
for c, v in fichas.items():
    for aud, p in v.get('por', {}).items():
        mom = {str(m['MomentoId']): m['Orden'] for m in p['moms']}
        for mid, dd in p['det'].items():
            for a in dd.get('acciones') or []:
                t = a['TipoAccionCondicion']
                for i, x in enumerate(a.get('data') or [{}], 1):
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
                    key = (c, mom.get(str(mid), ''), a['Orden'], i, t, txt(nom), txt(det), txt(a.get('Excepcion')))
                    rows.setdefault(key, set()).add(aud)
w = csv.writer(open(out, 'w', encoding='utf-8', newline=''))
w.writerow(['codigo', 'n_catalogo', 'nombre_govco', 'en_linea_govco', 'audiencias', 'orden_momento', 'orden_accion', 'item', 'tipo', 'nombre', 'detalle', 'excepcion'])
for k in sorted(rows, key=lambda k: (int(k[0]), k[1] or 0, k[2], k[3])):
    b = busc.get(k[0], {})
    w.writerow([k[0], ';'.join(catn.get(k[0], [])), txt(b.get('titulo')), b.get('enLinea', ''), '|'.join(sorted(rows[k]))] + list(k[1:]))
print(len(rows), 'filas;', len(fichas), 'trámites')
