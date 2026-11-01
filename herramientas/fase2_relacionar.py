"""Fase 2 (versión 3: lo que la fuente no menciona se reporta como «no declarado», no como ausencia; D-041, D-042, informe 14).
Relaciona cada requisito documental de las categorías (a) y (b) con la base de datos o sistema de la Gobernación que lo
respalda y con el mecanismo de intercambio que declaran sus documentos (Datos Maestros, F-008; PETI 2026, F-007), con la
consulta pública en línea de la entidad emisora (F-107 a F-111) y con la estandarización del SUIT, y asigna los dominios
del Marco de interoperabilidad solo cuando una fuente da evidencia.
Reglas de dominio:
  técnico: la fuente declara que la base o el servicio cubren solo una parte del dato; si no declara nada, no determinable.
  organizacional: el dato está al alcance de la entidad y aun así se pide el documento (la fuente declara entrega manual de
    la certificación, una base declarada tiene el dato completo, o la entidad emisora ofrece consulta pública del dato completo).
  semántico: el campo de la base no equivale al dato que certifica el documento.
  político-legal: no se asigna en (a) (art. 9 DL 019 de 2012); no determinable en (b).
Entradas: matriz_documentos_suit, requisitos_suit. Salidas: fase2_requisitos, fase2_documentos, fase2_candidatos (CSV).
La relación documento-base es una lectura del investigador de lo que declaran las fuentes; no verifica los sistemas.
Uso: python3 -I herramientas/fase2_relacionar.py <matriz_csv> <requisitos_csv> <salida_req_csv> <salida_doc_csv> <salida_cand_csv>"""
import csv, collections, sys, unicodedata

# documento -> (base o sistema de la Gobernación con páginas de F-008, cobertura, mecanismo declarado, campo no equivalente, nota)
B = {
 'certificado de tiempo de servicio': ('Docentes_Sector_Educativo, Historial_Laboral, Servidores_Publicos (F-008, p. 2); SIFA nómina (F-007, p. 35)', 'parcial', 'interno: entrega por oficio o correo (F-008, p. 2, Historial_Laboral)', True, 'Fecha_Ingreso no equivale a tiempo de servicio por entidad'),
 'certificado de salarios': ('Servidores_Publicos (F-008, p. 2); SIFA nómina (F-007, p. 35)', 'parcial', 'interno: entrega por oficio o correo (F-008, p. 2, Historial_Laboral)', True, 'Servidores_Publicos tiene Salario pero no incluye docentes'),
 'resolución de pensión del docente': ('Pensionados_Departamento (F-008, p. 2)', 'parcial', 'interno', False, 'registra el acto de los pensionados a cargo del departamento'),
 'acto administrativo de retiro del servicio docente': ('Historial_Laboral; Docentes_Sector_Educativo, campo Estado (F-008, p. 2)', 'parcial', 'interno: expediente digitalizado (F-008, p. 2)', False, 'el historial laboral es de servidores; la tabla de docentes solo registra el estado'),
 'licencia de funcionamiento expedida por la Gobernación': ('Instituciones_Educativas (p. 2); IPS_Prestadoras_Salud (p. 2); Farmacias (p. 3) (F-008)', 'parcial', 'interno', False, 'Instituciones_Educativas solo incluye instituciones oficiales'),
 'paz y salvo de la pagaduría del empleador': ('SIFA nómina (F-007, p. 35)', 'parcial', 'interno', False, ''),
 'acta de visita sanitaria': ('Farmacias (F-008, p. 3, sistema IVC-Salud)', 'parcial', 'interno', False, ''),
 'certificado de habilitación': ('IPS_Prestadoras_Salud (F-008, p. 2)', 'completa', 'interno (dato consumido del REPS del MSPS)', False, 'Estado_Habilitacion y Fecha_Habilitacion'),
 'registro profesional en salud': ('Medicos; Enfermeras (F-008, p. 3)', 'parcial', 'servicio web declarado con RETHUS (MSPS)', False, 'las tablas consumen RETHUS'),
 'constancia de no sanción por comercio ilegal de medicamentos': ('Farmacias (F-008, p. 3)', 'parcial', 'interno', False, 'sin campo de sanciones'),
 'licencia de tránsito': ('Impuestos_Vehiculos; Contribuyentes_Rentas (F-008, p. 1)', 'parcial', 'servicio web declarado con el RUNT', True, 'no registran el número de la licencia'),
 'RUT o NIT': ('Contratistas_Proponentes; Contribuyentes_Rentas (F-008, p. 1)', 'completa', 'servicio web declarado con la DIAN (validación con API RUT)', False, 'la fuente declara la validación; no dice que se use dentro de los trámites que exigen el RUT'),
 'certificado de administradora de pensiones': ('Pensionados_Departamento (F-008, p. 2)', 'parcial', 'servicio web declarado con Colpensiones (validación de derechos)', True, 'no cubre fondos privados ni equivale al certificado de cualquier administradora'),
 'certificado de existencia y representación legal': ('Contratistas_Proponentes (F-008, p. 1)', 'parcial', 'servicio web declarado con el RUP («CCE», según la fuente)', True, 'el RUP no es el certificado de existencia y representación legal'),
 'certificado de escolaridad': ('Estudiantes_Matriculados (F-008, p. 2), SIMAT', 'parcial', 'servicio web declarado con el SIMAT (MEN)', False, 'solo matrícula oficial'),
 'certificado catastral': ('Predios_Rurales (F-008, p. 3)', 'parcial', 'servicio web declarado con el IGAC', False, 'solo predios rurales'),
 'tarjeta profesional': ('Medicos; Enfermeras (F-008, p. 3)', 'parcial', 'servicio web declarado con RETHUS (MSPS)', False, 'solo profesiones de la salud'),
}
# consultas públicas en línea de la entidad emisora: (descripción, alcance, nota)
C = {
 'documento de identidad': ('Registraduría: certificado de vigencia de la cédula, gratuito y en línea (F-109, noticia de 2013)', 'vigencia (sin confirmar)', 'confirma la vigencia, no reemplaza la copia; la fuente es de 2013'),
 'certificado de antecedentes disciplinarios': ('Procuraduría: consulta y certificado en línea, gratuitos (F-107)', 'completa', 'la página la presenta para quienes van a posesionarse o a contratar'),
 'certificado de antecedentes fiscales': ('Contraloría: certificado en línea, sin costo (F-108)', 'completa', 'la página dice que las entidades deben consultar directamente a futuros contratistas o funcionarios'),
 'certificado de existencia y representación legal': ('RUES: información de registros empresariales sin costo para funcionarios de entidades (F-111)', 'parcial', 'información del registro, no el certificado'),
 'tarjeta profesional': ('ReTHUS: consulta ciudadana (F-110)', 'parcial', 'solo profesiones de la salud'),
 'registro profesional en salud': ('ReTHUS: consulta ciudadana (F-110)', 'parcial', ''),
}
ND_A, ND_B = 'no declarada', 'no declarado'


def n(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return ''.join(c for c in s if not unicodedata.combining(c))


mat, req, out_r, out_d, out_c = sys.argv[1:6]
M = [x for x in csv.DictReader(open(mat, encoding='utf-8')) if x['categoria'] in ('a', 'b')]
R = list(csv.DictReader(open(req, encoding='utf-8')))
tipo = {(x['codigo'], x['nombre'].strip()): x['tipo_documento_suit'] for x in R if x['tipo'] == 'DOCUMENTO'}
rows = []
for x in M:
    doc, cat, cod = x['documento'], x['categoria'], x['codigo']
    base, cob, mec, noeq, nota = B.get(doc, ('—', ND_A, 'interno' if cat == 'a' else ND_B, False, ''))
    cp = C.get(doc)
    tipos = {tipo.get((cod, nm), '') for nm in x['nombres_en_ficha'].split(' | ')}
    ws = mec.startswith('servicio web')
    # técnico: solo con declaración de cobertura parcial
    tec = 'sí (cobertura parcial declarada)' if cob == 'parcial' else ('no determinable' if cob in (ND_A, ND_B) else 'no')
    org = []
    if mec.startswith('interno: entrega por oficio'):
        org.append('la fuente declara entrega manual de la certificación (oficio o correo)')
    if cob == 'completa':
        org.append('una base declarada tiene el dato completo')
    if cp and cp[1] == 'completa':
        org.append('la entidad emisora ofrece consulta pública del dato completo')
    sem = 'el campo de la base no equivale al dato certificado' if noeq else ''
    # situación del dato en (b)
    if cat == 'b':
        if ws and cob == 'completa': sit = 'servicio web completo'
        elif ws: sit = 'servicio web parcial'
        elif cp and cp[1] == 'completa': sit = 'consulta pública completa'
        elif cp and cp[1].startswith('vigencia'): sit = 'consulta pública de vigencia (sin confirmar)'
        else: sit = 'mecanismo no declarado'
    else:
        sit = cob
    rows.append(dict(categoria=cat, documento=doc, codigo=cod, tramite=x['tramite'], emisor=x['emisor'], marcas=x['marcas'],
                     base_gobernacion=base, cobertura=cob, mecanismo_declarado=mec, situacion=sit,
                     consulta_publica=cp[0] if cp else '', alcance_consulta=cp[1] if cp else '', nota_consulta=cp[2] if cp else '',
                     tecnico=tec, organizacional='sí' if org else 'no determinable', evidencia_organizacional=' | '.join(org),
                     semantico='sí' if sem else 'no determinable', evidencia_semantica=sem,
                     politico_legal='no se asigna (art. 9 DL 019)' if cat == 'a' else 'no determinable',
                     tipo_documento_suit=';'.join(sorted(tipos)), nota=nota))
cols = list(rows[0].keys())
w = csv.DictWriter(open(out_r, 'w', encoding='utf-8', newline=''), cols); w.writeheader(); w.writerows(rows)

# por documento
D = collections.OrderedDict()
for r in rows:
    d = D.setdefault((r['categoria'], r['documento']), dict(r=r, tr=set(), var=False, mc=False))
    d['tr'].add(r['codigo']); d['var'] |= 'emisor_variable' in r['marcas']; d['mc'] |= 'misma_competencia' in r['marcas']
orden = {'completa': 0, 'parcial': 1, ND_A: 2, ND_B: 2}
lst = sorted(D.items(), key=lambda kv: (kv[0][0], -len(kv[1]['tr']), orden.get(kv[1]['r']['cobertura'], 3), kv[0][1]))
w = csv.writer(open(out_d, 'w', encoding='utf-8', newline=''))
w.writerow(['categoria', 'documento', 'n_tramites', 'emisor_variable', 'misma_competencia', 'base_gobernacion', 'cobertura', 'mecanismo_declarado', 'situacion', 'consulta_publica', 'alcance_consulta'])
for (cat, doc), d in lst:
    r = d['r']; w.writerow([cat, doc, len(d['tr']), int(d['var']), int(d['mc']), r['base_gobernacion'], r['cobertura'], r['mecanismo_declarado'], r['situacion'], r['consulta_publica'], r['alcance_consulta']])
# candidatos: criterio 1 categoría (a) primero; 2 número de trámites; 3 disponibilidad del dato (completa > parcial > no declarada).
# (a): todos los documentos; (b): los que se exigen en 7 o más trámites (mismo umbral de la Tabla 2 de la Fase 1)
cand = [(k, d) for k, d in lst if k[0] == 'a' or len(d['tr']) >= 7]
w = csv.writer(open(out_c, 'w', encoding='utf-8', newline=''))
w.writerow(['orden', 'categoria', 'documento', 'n_tramites', 'emisor_variable', 'misma_competencia', 'situacion'])
for i, ((cat, doc), d) in enumerate(cand, 1):
    w.writerow([i, cat, doc, len(d['tr']), int(d['var']), int(d['mc']), d['r']['situacion']])

# resumen
def esc(cat, f):
    return [r for r in rows if r['categoria'] == cat and f(r)]
tod = lambda r: True
sev = lambda r: 'emisor_variable' not in r['marcas']
est = lambda r: 'emisor_variable' not in r['marcas'] and 'misma_competencia' not in r['marcas']
for cat in 'ab':
    for nm, f in [('todos', tod), ('sin emisor variable', sev), ('estricto', est)]:
        rr = esc(cat, f)
        print(cat, nm, len(rr), dict(collections.Counter(r['situacion'] for r in rr)))
for cat in 'ab':
    rr = [r for r in rows if r['categoria'] == cat]
    print(cat, 'técnico', dict(collections.Counter(r['tecnico'] for r in rr)), 'org', sum(r['organizacional'] == 'sí' for r in rr),
          'sem', sum(r['semantico'] == 'sí' for r in rr), 'propio', sum(r['tipo_documento_suit'] == 'PROPIO_DEL_TRAMITE' for r in rr),
          'estandarizado', sum(r['tipo_documento_suit'] == 'ESTANDARIZADO' for r in rr))
b = [r for r in rows if r['categoria'] == 'b']
tr = collections.defaultdict(list)
for r in b: tr[r['codigo']].append(r)
sw = lambda r: r['situacion'].startswith('servicio web')
cpub = lambda r: r['situacion'].startswith('consulta')
print('trámites con b', len(tr), '; algún b sin servicio web', sum(any(not sw(r) for r in v) for v in tr.values()),
      '; algún b sin servicio web ni consulta', sum(any(not sw(r) and not cpub(r) for r in v) for v in tr.values()),
      '; todos con servicio web', sum(all(sw(r) for r in v) for v in tr.values()))
print('org evidencia', dict(collections.Counter(e for r in rows for e in r['evidencia_organizacional'].split(' | ') if e)))
print('candidatos', len(cand))
for i, ((cat, doc), d) in enumerate(cand, 1):
    print(i, cat, doc, len(d['tr']), 'var' if d['var'] else '', 'mc' if d['mc'] else '', d['r']['situacion'])
