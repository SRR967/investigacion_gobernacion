"""Fase 2: relaciona cada documento de las categorías (a) y (b) con la base de datos o sistema de la Gobernación que lo
respalda y con el mecanismo de intercambio que declaran sus documentos (Datos Maestros, F-008; PETI 2026, F-007),
y asigna los dominios de interoperabilidad con la regla D-031.
Entrada: datos/matriz_documentos_suit_2026-10-31.csv. Salida: datos/fase2_documentos_2026-10-31.csv.
La relación documento-base es una lectura del investigador sobre lo que declaran las fuentes; no verifica los sistemas.
Uso: python3 -I herramientas/fase2_relacionar.py <matriz_csv> <salida_csv>"""
import csv, collections, sys

# documento canónico -> (base o sistema de la Gobernación que contiene el dato, cobertura del dato en esa base,
#                         mecanismo de intercambio declarado con la entidad que custodia el dato, evidencia)
# cobertura: 'completa' (la base tiene el dato que certifica el documento), 'parcial' (tiene parte del dato o solo
#            para una parte de los casos), 'ninguna' (ninguna base declarada lo contiene).
# mecanismo: 'interno' (el dato es de la propia Gobernación), 'servicio web bilateral con X', 'ninguno declarado'.
B = {
 # (a) documentos de la propia Gobernación
 'certificado de tiempo de servicio': ('Docentes_Sector_Educativo (F-008, tabla 45); Historial_Laboral (tabla 31); Servidores_Publicos (tabla 37); SIFA, módulo de nómina (F-007, p. 35)', 'parcial', 'interno', 'tabla 45 tiene Fecha_Ingreso pero no tiempos por entidad; tabla 31 guarda actos digitalizados y declara como caso de uso la elaboración de certificaciones de tiempo de servicio y salarios para trámites de pensión, entregadas por oficio o correo; la nómina de SIFA emite certificaciones laborales (texto OCR)'),
 'resolución de pensión del docente': ('Pensionados_Departamento (tabla 24)', 'parcial', 'interno', 'la tabla 24 registra Acto_Administrativo de reconocimiento, pero de los pensionados a cargo del departamento'),
 'certificado de salarios': ('Servidores_Publicos (tabla 37); SIFA, módulo de nómina (F-007, p. 35)', 'parcial', 'interno', 'la tabla 37 tiene Salario de los servidores; la tabla 45 de docentes no tiene campo de salario'),
 'acto administrativo de retiro del servicio docente': ('Historial_Laboral (tabla 31); Docentes_Sector_Educativo (tabla 45, campo Estado)', 'parcial', 'interno', 'tabla 31: actos de retiro de servidores, como expediente digitalizado; tabla 45: solo el estado'),
 'licencia de funcionamiento expedida por la Gobernación': ('Instituciones_Educativas (tabla 42); IPS_Prestadoras_Salud (tabla 50); Farmacias (tabla 56)', 'parcial', 'interno', 'la tabla 42 solo incluye instituciones oficiales; las tablas 50 y 56 registran habilitación'),
 'tornaguía': ('—', 'ninguna', 'interno', 'ni F-008 ni F-007 mencionan tornaguías ni el impuesto al consumo'),
 'reportes anuales de cesantías': ('—', 'ninguna', 'interno', 'ninguna tabla declarada'),
 'paz y salvo de la pagaduría del empleador': ('SIFA, módulo de nómina (F-007, p. 35)', 'parcial', 'interno', ''),
 'resolución de cesantías pagadas': ('—', 'ninguna', 'interno', 'ninguna tabla declarada'),
 'acta de visita sanitaria': ('Farmacias (tabla 56, sistema IVC-Salud)', 'parcial', 'interno', ''),
 'acta del accidente de trabajo': ('—', 'ninguna', 'interno', 'ninguna tabla declarada'),
 'certificado de habilitación': ('IPS_Prestadoras_Salud (tabla 50)', 'completa', 'interno', 'campos Estado_Habilitacion y Fecha_Habilitacion; la fuente dice que el REPS del MSPS es la fuente oficial y que la Gobernación consume el dato por servicio web'),
 'registro profesional en salud': ('Medicos (tabla 54); Enfermeras (tabla 55)', 'parcial', 'interno', 'las tablas consumen RETHUS por servicio web'),
 'resolución de autorización de etiquetas': ('—', 'ninguna', 'interno', 'ninguna tabla declarada'),
 'acta de comité de exoneración del servicio social obligatorio': ('—', 'ninguna', 'interno', 'ninguna tabla declarada'),
 'constancia de no sanción por comercio ilegal de medicamentos': ('Farmacias (tabla 56)', 'parcial', 'interno', 'la tabla no declara un campo de sanciones'),
 # (b) documentos de otras autoridades con mecanismo declarado
 'licencia de tránsito': ('Impuestos_Vehiculos (tabla 17); Contribuyentes_Rentas (tabla 22)', 'parcial', 'servicio web bilateral con el RUNT', 'tablas 17 y 22: validación de propietarios y datos de vehículos; no registran el número de la licencia'),
 'RUT o NIT': ('Contratistas_Proponentes (tabla 16); Contribuyentes_Rentas (tabla 22)', 'completa', 'servicio web bilateral con la DIAN (API RUT)', ''),
 'certificado de administradora de pensiones': ('Pensionados_Departamento (tabla 24)', 'parcial', 'servicio web bilateral con Colpensiones', 'solo Colpensiones; no los fondos privados'),
 'certificado de existencia y representación legal': ('Contratistas_Proponentes (tabla 16)', 'parcial', 'servicio web bilateral con el RUP (según la fuente, administrado por la CCE)', 'el RUP no es el certificado de existencia y representación legal'),
 'certificado de escolaridad': ('Estudiantes_Matriculados (tabla 44), SIMAT', 'parcial', 'servicio web bilateral con el SIMAT (MEN)', 'solo matrícula oficial'),
 'certificado catastral': ('Predios_Rurales (tabla 71)', 'parcial', 'servicio web bilateral con el IGAC', 'solo predios rurales; campos matricula_inmobiliaria y avaluo'),
 'tarjeta profesional': ('Medicos (tabla 54); Enfermeras (tabla 55)', 'parcial', 'servicio web bilateral con RETHUS (MSPS)', 'solo profesiones de la salud; la tabla declara RETHUS como fuente y Web Services como medio en sus columnas'),
}


def dominios(cat, cobertura, mecanismo, marcas):
    # Organizacional: se asigna a todos, porque ninguna fuente describe un procedimiento para verificar el dato dentro
    # de los trámites (supuesto de la regla; no se evaluó documento por documento). La regla no tiene rama para el
    # dominio político-legal.
    d = ['organizacional']
    if cat == 'a':
        if cobertura == 'ninguna':
            d.append('técnico: no hay base')
        elif cobertura == 'parcial':
            d.append('técnico: base parcial')
    else:
        if mecanismo == 'ninguno declarado':
            d.append('técnico: no hay medio')
        elif cobertura == 'parcial':
            d.append('técnico: medio parcial')
    if 'emisor_variable' in marcas or cobertura == 'parcial':
        d.append('semántico')
    return d


src, out = sys.argv[1:3]
M = [x for x in csv.DictReader(open(src, encoding='utf-8')) if x['categoria'] in ('a', 'b')]
g = collections.defaultdict(lambda: {'tramites': set(), 'marcas': set()})
for x in M:
    k = (x['categoria'], x['documento'], x['emisor'])
    g[k]['tramites'].add(x['codigo'])
    g[k]['marcas'].update(m for m in x['marcas'].split(';') if m)
rows = []
for (cat, doc, emisor), v in g.items():
    base, cob, mec, ev = B.get(doc, ('—', 'ninguna', 'ninguno declarado', 'ninguna tabla ni sistema declarado'))
    if cat == 'a' and doc not in B:
        mec = 'interno'
    d = dominios(cat, cob, mec, v['marcas'])
    rows.append([cat, doc, emisor, len(v['tramites']), ';'.join(sorted(v['tramites'])), ';'.join(sorted(v['marcas'])), base, cob, mec, ev, ';'.join(d)])
rows.sort(key=lambda r: (r[0], -r[3], r[1]))
w = csv.writer(open(out, 'w', encoding='utf-8', newline=''))
w.writerow(['categoria', 'documento', 'emisor', 'n_tramites', 'tramites', 'marcas', 'base_gobernacion', 'cobertura', 'mecanismo_declarado', 'evidencia', 'dominios'])
w.writerows(rows)
# Resumen ponderado por requisitos (documento x trámite)
R = collections.Counter(); Rcat = collections.defaultdict(collections.Counter)
for r in rows:
    n = r[3]
    for d in r[10].split(';'):
        R[d] += n
    Rcat[r[0]][r[8] if r[0] == 'b' else r[7]] += n
print('documentos canónicos:', len(rows), '; requisitos:', sum(r[3] for r in rows))
print('a por cobertura (requisitos):', dict(Rcat['a']))
print('b por mecanismo (requisitos):', dict(Rcat['b']))
print('dominios (requisitos):', dict(R))
