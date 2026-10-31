"""Aplana el Visor SUIT de Función Pública (F-105) en una tabla de requisitos, una fila por requisito,
con el mismo formato de columnas que usa herramientas/codificar_requisitos.py, más la fecha de última
modificación de cada trámite y la clasificación del propio SUIT (documento estandarizado o propio del trámite).
Uso: python3 -I herramientas/aplanar_visorsuit.py <json_visor> <catalogo_csv> <salida_csv> <tramites_csv>"""
import csv, json, sys, datetime
src, cat, out, out_t = sys.argv[1:5]
d = json.load(open(src, encoding='utf-8'))['tramites']
catn = {}
for r in csv.DictReader(open(cat, encoding='utf-8')):
    c = r['codigo_govco'].lstrip('T')
    if c and '(registro duplicado)' not in r['nombre']:
        catn.setdefault(c, []).append(r['n'])


def txt(v):
    return ' '.join(str(v or '').split())


def fecha(ms):
    return datetime.datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d') if ms else ''


rows, tram = [], []
for c, v in sorted(d.items(), key=lambda x: int(x[0])):
    t = (v.get('tramite') or {}).get('json')
    if not t:
        continue
    medio = t.get('tipoMedioElectronico') or ''
    tram.append([c, ';'.join(catn.get(c, [])), txt(t.get('nombre')), medio, fecha(t.get('fechaModificacion')), t.get('estado'), t.get('version')])
    for m in t.get('momentos') or []:
        for r in m.get('requisitos') or []:
            tipo = r.get('tipoRequisito')
            aud = '|'.join(sorted(a.get('nombre', '') for a in (r.get('tiposAudiencias') or [])))
            exc = r.get('tramiteExcepcion')
            exc = txt(exc.get('descripcion') if isinstance(exc, dict) else exc)
            if tipo == 'DOCUMENTO':
                nom = r.get('nombreDocumento')
                sop = r.get('cantidadDocSoportes') or []
                det = ' ; '.join(txt(' '.join(str(z) for z in [s.get('cantidad'), s.get('unidad'), s.get('observacion')] if z)) for s in sop)
                det = ' ; '.join(x for x in [det, txt(r.get('anotacionAdicional'))] if x)
            elif tipo == 'FORMULARIO':
                f = r.get('formulario') or {}
                nom = f.get('nombre') if isinstance(f, dict) else f
                det = txt(r.get('anotacionAdicional'))
            elif tipo == 'VERIFICACION_INST':
                nom = r.get('descripcionVerificado') or r.get('descripcionVerificacion') or r.get('descripcionDirectoInstitucion')
                det = ''
            elif tipo == 'SOLICITUD':
                nom = r.get('descripcionSolicitud') or 'solicitud'
                det = ''
            else:
                nom = tipo
                det = txt(r.get('anotacionAdicional'))
            de = r.get('documentoEstandarizado') or {}
            rows.append([c, ';'.join(catn.get(c, [])), txt(t.get('nombre')), medio, aud, m.get('orden'), r.get('orden'), 1, tipo,
                         txt(nom), det, exc, r.get('tipoDocumento') or '', de.get('tipoOferente') or '', de.get('idEntidadOferente') or ''])
w = csv.writer(open(out, 'w', encoding='utf-8', newline=''))
w.writerow(['codigo', 'n_catalogo', 'nombre_govco', 'en_linea_govco', 'audiencias', 'orden_momento', 'orden_accion', 'item', 'tipo',
            'nombre', 'detalle', 'excepcion', 'tipo_documento_suit', 'oferente_suit', 'id_entidad_oferente_suit'])
w.writerows(rows)
w = csv.writer(open(out_t, 'w', encoding='utf-8', newline=''))
w.writerow(['codigo', 'n_catalogo', 'nombre', 'medio_electronico', 'fecha_modificacion', 'estado', 'version'])
w.writerows(tram)
print(len(rows), 'requisitos;', len(tram), 'trámites')
