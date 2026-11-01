"""Fase 2 (versión 2, regla de dominios con evidencia, D-041): relaciona cada requisito documental de las categorías
(a) y (b) con la base de datos o sistema de la Gobernación que lo respalda, con el mecanismo de intercambio que declaran
sus documentos (Datos Maestros, F-008; PETI 2026, F-007) y con las consultas públicas en línea de las entidades emisoras
(F-107 a F-111), y asigna los dominios de interoperabilidad solo cuando una fuente da evidencia.
Entradas: datos/matriz_documentos_suit_2026-10-31.csv, datos/requisitos_suit_2026-10-31.csv.
Salidas: datos/fase2_requisitos_2026-10-31.csv (una fila por documento y trámite) y datos/fase2_documentos_2026-10-31.csv.
La relación documento-base es una lectura del investigador sobre lo que declaran las fuentes; no verifica los sistemas.
Uso: python3 -I herramientas/fase2_relacionar.py <matriz_csv> <requisitos_csv> <salida_req_csv> <salida_doc_csv>"""
import csv, collections, sys, unicodedata

# documento -> (base o sistema de la Gobernación, cobertura, mecanismo declarado, campo no equivalente, evidencia)
# cobertura: completa / parcial / ninguna.  campo no equivalente: la base registra un campo distinto del dato certificado.
B = {
 'certificado de tiempo de servicio': ('Docentes_Sector_Educativo (F-008, p. 3); Historial_Laboral (p. 2); Servidores_Publicos (p. 2); SIFA nómina (F-007, p. 35)', 'parcial', 'interno: oficio o correo institucional (F-008, Historial_Laboral, p. 2)', True, 'Fecha_Ingreso no equivale a tiempo de servicio por entidad; Historial_Laboral declara la elaboración de certificaciones de tiempo de servicio y salarios para trámites de pensión, entregadas por oficio o correo'),
 'certificado de salarios': ('Servidores_Publicos (p. 2); SIFA nómina (F-007, p. 35)', 'parcial', 'interno: oficio o correo institucional (F-008, Historial_Laboral, p. 2)', True, 'Servidores_Publicos tiene Salario, pero no incluye docentes; la tabla de docentes no tiene salario'),
 'resolución de pensión del docente': ('Pensionados_Departamento (p. 2)', 'parcial', 'interno', False, 'registra Acto_Administrativo de reconocimiento de los pensionados a cargo del departamento; la tabla de tipos de pensión separa el régimen del FOMAG'),
 'acto administrativo de retiro del servicio docente': ('Historial_Laboral (p. 2); Docentes_Sector_Educativo (p. 3, campo Estado)', 'parcial', 'interno: expediente digitalizado (F-008, Historial_Laboral, p. 2)', False, 'actos de retiro de servidores como PDF; la tabla de docentes solo registra el estado'),
 'licencia de funcionamiento expedida por la Gobernación': ('Instituciones_Educativas (p. 3); IPS_Prestadoras_Salud (p. 3); Farmacias (p. 3)', 'parcial', 'interno', False, 'Instituciones_Educativas solo incluye instituciones oficiales'),
 'paz y salvo de la pagaduría del empleador': ('SIFA nómina (F-007, p. 35)', 'parcial', 'interno', False, ''),
 'acta de visita sanitaria': ('Farmacias (p. 3, sistema IVC-Salud)', 'parcial', 'interno', False, ''),
 'certificado de habilitación': ('IPS_Prestadoras_Salud (p. 3)', 'completa', 'interno (dato consumido del REPS del MSPS)', False, 'Estado_Habilitacion y Fecha_Habilitacion'),
 'registro profesional en salud': ('Medicos; Enfermeras (p. 3)', 'parcial', 'servicio web declarado con RETHUS (MSPS)', False, 'las tablas consumen RETHUS'),
 'constancia de no sanción por comercio ilegal de medicamentos': ('Farmacias (p. 3)', 'parcial', 'interno', False, 'sin campo de sanciones'),
 'licencia de tránsito': ('Impuestos_Vehiculos; Contribuyentes_Rentas (p. 2)', 'parcial', 'servicio web declarado con el RUNT', True, 'no registran el número de la licencia'),
 'RUT o NIT': ('Contratistas_Proponentes (p. 1); Contribuyentes_Rentas (p. 2)', 'completa', 'servicio web declarado con la DIAN (API RUT)', False, ''),
 'certificado de administradora de pensiones': ('Pensionados_Departamento (p. 2)', 'parcial', 'servicio web declarado con Colpensiones', True, 'el servicio es de validación de derechos pensionales y no cubre fondos privados'),
 'certificado de existencia y representación legal': ('Contratistas_Proponentes (p. 1)', 'parcial', 'servicio web declarado con el RUP («CCE», según la fuente)', True, 'el RUP no es el certificado de existencia y representación legal'),
 'certificado de escolaridad': ('Estudiantes_Matriculados (p. 3), SIMAT', 'parcial', 'servicio web declarado con el SIMAT (MEN)', False, 'solo matrícula oficial'),
 'certificado catastral': ('Predios_Rurales (p. 4)', 'parcial', 'servicio web declarado con el IGAC', False, 'solo predios rurales'),
 'tarjeta profesional': ('Medicos; Enfermeras (p. 3)', 'parcial', 'servicio web declarado con RETHUS (MSPS)', False, 'solo profesiones de la salud'),
}
# consultas públicas en línea de la entidad emisora (F-107 a F-111), con su alcance
C = {
 'documento de identidad': ('Registraduría: certificado de vigencia de la cédula, gratuito y en línea (F-109)', 'parcial', 'certifica la vigencia, no reemplaza la copia del documento'),
 'certificado de antecedentes disciplinarios': ('Procuraduría: consulta y certificado en línea, gratuitos; las entidades pueden consultarlo (Ley 1238 de 2008) (F-107)', 'completa', ''),
 'certificado de antecedentes fiscales': ('Contraloría: certificado en línea, sin costo (F-108); también consultable en el portal de la Procuraduría (F-107)', 'completa', ''),
 'certificado de existencia y representación legal': ('RUES: información detallada y sin costo para funcionarios de entidades (F-111)', 'parcial', 'información del registro, no el certificado'),
 'tarjeta profesional': ('ReTHUS: consulta ciudadana del cumplimiento de requisitos del personal de salud (F-110)', 'parcial', 'solo profesiones de la salud'),
 'registro profesional en salud': ('ReTHUS: consulta ciudadana (F-110)', 'parcial', ''),
}


def n(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return ''.join(c for c in s if not unicodedata.combining(c))


mat, req, out_r, out_d = sys.argv[1:5]
M = [x for x in csv.DictReader(open(mat, encoding='utf-8')) if x['categoria'] in ('a', 'b')]
R = list(csv.DictReader(open(req, encoding='utf-8')))
verif = collections.defaultdict(str)
tipo = {}
for x in R:
    if x['tipo'] == 'VERIFICACION_INST':
        verif[x['codigo']] += ' ' + n(x['nombre'])
    if x['tipo'] == 'DOCUMENTO':
        tipo[(x['codigo'], x['nombre'].strip())] = x['tipo_documento_suit']
rows = []
for x in M:
    doc, cat, cod = x['documento'], x['categoria'], x['codigo']
    base, cob, mec, noeq, ev = B.get(doc, ('—', 'ninguna', 'interno' if cat == 'a' else 'ninguno declarado', False, ''))
    cp = C.get(doc)
    nombres = x['nombres_en_ficha'].split(' | ')
    tipos = {tipo.get((cod, nm), '') for nm in nombres}
    propio = tipos == {'PROPIO_DEL_TRAMITE'}
    # Dominio técnico
    if cat == 'a':
        tec = {'ninguna': 'técnico: no hay base', 'parcial': 'técnico: base parcial'}.get(cob, '')
    else:
        if mec == 'ninguno declarado' and not cp:
            tec = 'técnico: no hay medio'
        elif mec == 'ninguno declarado' and cp:
            tec = 'técnico: solo consulta pública en línea'
        elif cob == 'parcial':
            tec = 'técnico: medio parcial'
        else:
            tec = ''
    # Dominio organizacional: solo con evidencia de que el dato está al alcance y aun así se pide el documento
    org = []
    if doc == 'certificado de tiempo de servicio' and 'tiempo de servicio' in verif[cod]:
        org.append('el SUIT registra la verificación del tiempo de servicio y además pide el certificado')
    if doc == 'certificado de existencia y representación legal' and 'camara de comercio' in verif[cod]:
        org.append('el SUIT registra la verificación de la inscripción en cámara de comercio y además pide el certificado')
    if mec.startswith('interno: oficio'):
        org.append('la fuente declara entrega manual de la certificación (oficio o correo)')
    if cob == 'completa':
        org.append('una base declarada tiene el dato completo')
    if cp and cp[1] == 'completa':
        org.append('la entidad emisora ofrece consulta pública en línea del dato completo')
    # Dominio semántico: campo no equivalente o documento no estandarizado en el SUIT
    sem = []
    if noeq:
        sem.append('el campo de la base no equivale al dato certificado')
    if propio:
        sem.append('el SUIT lo registra como documento propio, no estandarizado')
    pl = 'no se asigna (art. 9 DL 019)' if cat == 'a' else 'no determinable (depende de la vinculación al servicio de interoperabilidad)'
    rows.append([cat, doc, cod, x['tramite'], x['emisor'], x['marcas'], base, cob, mec, cp[0] if cp else '', cp[1] if cp else '',
                 tec, 'sí' if org else 'no determinable', ' | '.join(org), 'sí' if sem else 'no', ' | '.join(sem), pl, ';'.join(sorted(tipos))])
cols = ['categoria', 'documento', 'codigo', 'tramite', 'emisor', 'marcas', 'base_gobernacion', 'cobertura', 'mecanismo_declarado',
        'consulta_publica', 'cobertura_consulta', 'tecnico', 'organizacional', 'evidencia_organizacional', 'semantico',
        'evidencia_semantica', 'politico_legal', 'tipo_documento_suit']
w = csv.writer(open(out_r, 'w', encoding='utf-8', newline=''))
w.writerow(cols); w.writerows(rows)
# resumen por documento
D = collections.OrderedDict()
for r in rows:
    k = (r[0], r[1])
    D.setdefault(k, {'n': 0, 'r': r})['n'] += 1
w = csv.writer(open(out_d, 'w', encoding='utf-8', newline=''))
w.writerow(['categoria', 'documento', 'n_tramites', 'base_gobernacion', 'cobertura', 'mecanismo_declarado', 'consulta_publica', 'cobertura_consulta'])
for (cat, doc), v in sorted(D.items(), key=lambda kv: (kv[0][0], -kv[1]['n'])):
    r = v['r']; w.writerow([cat, doc, v['n'], r[6], r[7], r[8], r[9], r[10]])
# resumen por consola
for cat in 'ab':
    rr = [r for r in rows if r[0] == cat]
    print(cat, len(rr), 'cobertura', dict(collections.Counter(r[7] for r in rr)), 'técnico', dict(collections.Counter(r[11] for r in rr)),
          'org sí', sum(r[12] == 'sí' for r in rr), 'sem sí', sum(r[14] == 'sí' for r in rr),
          'propio', sum(r[17] == 'PROPIO_DEL_TRAMITE' for r in rr), 'noeq', sum('equivale' in r[15] for r in rr))
b = [r for r in rows if r[0] == 'b']
print('b: servicio web', sum(not r[8].startswith('ninguno') for r in b), '; solo consulta pública', sum(r[8].startswith('ninguno') and bool(r[9]) for r in b),
      '; ninguno', sum(r[8].startswith('ninguno') and not r[9] for r in b))
tr = collections.defaultdict(list)
for r in b: tr[r[2]].append(r)
print('trámites con b', len(tr), '; con al menos un b sin servicio web ni consulta', sum(any(r[8].startswith('ninguno') and not r[9] for r in v) for v in tr.values()),
      '; todos con servicio web', sum(all(not r[8].startswith('ninguno') for r in v) for v in tr.values()))
print('evidencia organizacional:', dict(collections.Counter(e for r in rows for e in r[13].split(' | ') if e)))
