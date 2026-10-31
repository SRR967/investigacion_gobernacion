"""Codifica los requisitos documentales (Fase 1) según las reglas de la metodología (D-035, D-036, D-038).
Entrada: datos/requisitos_suit_2026-10-31.csv (Visor SUIT, F-105). Salida: datos/matriz_documentos_suit_2026-10-31.csv (una fila por
requisito documental distinto por trámite) y un resumen por consola.
La tabla R asigna a cada nombre normalizado (por prefijo): categoría (a/b/c/excluido), nombre canónico (para fusionar
el mismo documento dentro de un trámite), marcas y emisor. La atribución del emisor es conocimiento general por
verificar con la norma de cada trámite.
Marca «misma_competencia»: acto previo que, por tratarse de un trámite de la Gobernación, se presume expedido por la
misma dependencia en ejercicio de la misma competencia (p. ej., la resolución de pensión de un docente de la planta
departamental); es una interpretación del estudio, por confirmar con la norma del trámite.
Uso: python3 -I herramientas/codificar_requisitos.py <requisitos_csv> <salida_csv>"""
import csv, unicodedata, re, sys


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', s).split())


GOB_PAGO = ('excluido', 'recibo o declaración de pago a la Gobernación', 'pago', 'Gobernación (recaudo propio)')  # regla: el pago no es documento
ID = ('b', 'documento de identidad', 'registro_publico', 'Registraduría Nacional / Migración Colombia')
CCIO = ('b', 'certificado de existencia y representación legal', 'registro_publico;particular_funcion_publica', 'Cámara de Comercio')
ACTAS = ('c', 'actas de asamblea o junta', '', 'solicitante')
SOL = ('excluido', 'solicitud', 'solicitud', 'solicitante')
DIPL = ('b', 'diploma o acta de grado', 'emisor_variable', 'institución educativa')
NOTAS = ('b', 'certificado de estudios o notas', 'emisor_variable', 'institución educativa')
CURSO = ('b', 'certificado de capacitación o curso', 'emisor_variable', 'institución que dicta el curso')
LAB = ('b', 'certificación laboral de otras entidades', 'emisor_variable', 'cada empleador')
PENS = ('b', 'certificado de administradora de pensiones', 'emisor_variable', 'Colpensiones o fondo privado')
INVAL = ('b', 'certificado de invalidez', 'emisor_variable', 'prestador de salud')
FNA = ('b', 'paz y salvo o estado de deuda del Fondo Nacional del Ahorro', '', 'Fondo Nacional del Ahorro')
ESPEC = ('b', 'certificado de especialidad médica', 'emisor_variable', 'institución de educación superior')
SUEF = ('c', 'certificado de suficiencia patrimonial', 'tercero_privado', 'contador o revisor fiscal')
EXPER = ('c', 'certificación de experiencia', 'tercero_privado;emisor_variable', 'empleadores')
DECL = ('c', 'declaración ante notario', 'declaracion', 'ciudadano o terceros ante notario')
MANIF = ('c', 'declaración de terceros o manifestación', 'declaracion', 'ciudadano o terceros')
VISITA = ('a', 'acta de visita sanitaria', 'emisor_variable', 'Secretaría de Salud Departamental u otra autoridad sanitaria')
SUELO = ('b', 'certificado o concepto de uso del suelo', '', 'municipio')
TRAD = ('b', 'certificado de tradición y libertad', 'registro_publico', 'Oficina de Registro de Instrumentos Públicos')
CREA = ('b', 'acto administrativo de creación de la entidad', '', 'autoridad que crea la entidad')
RETIRO = ('a', 'acto administrativo de retiro del servicio docente', 'misma_competencia', 'Gobernación (nominadora del docente)')
PENSION = ('a', 'resolución de pensión del docente', 'misma_competencia', 'Gobernación (acto expedido para el FOMAG; por confirmar)')
CESANT = ('a', 'resolución de cesantías pagadas', 'misma_competencia', 'Gobernación (acto expedido para el FOMAG; por confirmar)')
REPCES = ('a', 'reportes anuales de cesantías', 'emisor_variable', 'empleador (Gobernación para docentes oficiales)')
LICGOB = ('a', 'licencia de funcionamiento expedida por la Gobernación', 'misma_competencia', 'Gobernación (Educación o Salud)')
LICRAD = ('b', 'licencia de material radiactivo', '', 'autoridad nuclear nacional')
TRANS = ('b', 'licencia de tránsito', 'registro_publico', 'organismo de tránsito / RUNT')
RUT = ('b', 'RUT o NIT', 'registro_publico', 'DIAN')
CONV = ('b', 'convalidación de título extranjero', '', 'Ministerio de Educación Nacional')
PUBLI = ('c', 'publicación en medios', 'tercero_privado', 'medio de comunicación')
CONTR = ('c', 'contrato', 'tercero_privado', 'partes del contrato')
TVAL = ('c', 'título valor', 'tercero_privado', 'partes')
MATER = ('c', 'materiales de capacitación', '', 'solicitante')
HV = ('c', 'hojas de vida', '', 'solicitante')
SSO_T = ('b', 'certificado de terminación del servicio social obligatorio', 'emisor_variable', 'institución del servicio social')

R = [
    ('', ('excluido', 'sin nombre', 'sin_nombre', '—')),
    ('acreditacion de los pagos', GOB_PAGO),
    # Nombres que solo aparecen en el extracto SUIT 2022 (comparación de la Fase 1)
    ('acta de aprobacion de estatutos', ACTAS), ('acta de asamblea', ACTAS),
    ('autorizacion ante el ministerio de relaciones exteriores', ('b', 'apostilla o legalización consular', '', 'Cancillería')),
    ('certificacion de delimitacion de territorio', ('b', 'certificación de delimitación del territorio', '', 'municipio')),
    ('certificacion de terminacion de estudios primarios', NOTAS),
    ('certificacion del tiempo de servicio', ('a', 'certificado de tiempo de servicio', 'emisor_variable', 'Gobernación; otra entidad si hubo servicio en otra parte')),
    ('certificacion no haber sido sancionados', ('a', 'constancia de no sanción por comercio ilegal de medicamentos', 'emisor_variable', 'autoridad sanitaria')),
    ('certificacion que acredite la calidad de delegado', ('c', 'acreditación de delegado', '', 'solicitante')),
    ('certificado de asistencia a un curso sobre proteccion radiologica', ('c', 'carné de protección radiológica', 'tercero_privado;emisor_variable', 'entidad que imparte el curso')),
    ('certificado de vecindad', ('b', 'certificado de residencia', '', 'alcaldía')),
    ('certificado que acredite que el programa academico', ('b', 'registro calificado del programa', '', 'Ministerio de Educación Nacional')),
    ('decision de la entidad que ejerce inspeccion', ('b', 'decisión de la entidad de inspección', '', 'entidad de inspección, control y vigilancia')),
    ('documento que describa las actividades', ('c', 'descripción de actividades', '', 'solicitante')),
    ('fallo del proceso', ('b', 'sentencia judicial', 'emisor_variable', 'autoridad que adelantó el proceso')),
    ('libro nuevo', ('c', 'libros de la entidad', '', 'solicitante')), ('libros anteriores', ('c', 'libros de la entidad', '', 'solicitante')),
    ('licencia anterior de salud ocupacional', ('a', 'licencia de funcionamiento expedida por la Gobernación', 'misma_competencia', 'Gobernación (Salud)')),
    ('listado de asistentes', ('c', 'listados y relaciones del solicitante', '', 'solicitante')),
    ('planchas o listas', ('c', 'listados y relaciones del solicitante', '', 'solicitante')),
    ('programa de trabajo inscrito', ('c', 'listados y relaciones del solicitante', '', 'solicitante')),
    ('relacion de', ('c', 'listados y relaciones del solicitante', '', 'solicitante')),
    ('paz y salvo expedido por la dian', ('b', 'paz y salvo DIAN', '', 'DIAN')),
    ('publicacion en diario', PUBLI),
    ('recibo servicio publico', ('c', 'recibo de servicio público', 'tercero_privado;emisor_variable', 'empresa de servicios públicos')),
    ('titulo o diploma', DIPL),
    ('acto administrativo mediante el cual se otorga el certificado de buenas practicas', ('b', 'certificado de buenas prácticas de manufactura', '', 'INVIMA')),
    ('carta especificando numero de ambulancias', ('c', 'descripción del servicio', '', 'solicitante')),
    ('certificacion de manipulacion de alimentos', CURSO),
    ('certificado catastral', ('b', 'certificado catastral', 'registro_publico', 'gestor catastral / IGAC')),
    ('publicacion de edictos', PUBLI),
    ('registros sanitarios o licencias de venta', ('b', 'registro sanitario', '', 'INVIMA')),
    ('reporte anual de las cesantias', REPCES),
    ('acta comite municipal de directivos', ('b', 'acta de comité municipal de directivos docentes', '', 'municipio')),
    ('acta de aprobacion de propuesta', ('b', 'acta de comité municipal de directivos docentes', '', 'municipio')),
    ('acta de constitucion', ('c', 'acta de constitución', '', 'solicitante')),
    ('acta de grado', DIPL),
    ('acta de la asamblea', ACTAS),
    ('acta de nombramiento extraida', ('c', 'acta de nombramiento', '', 'solicitante')),
    ('acta de posesion del representante', ('c', 'acta de posesión del representante legal', '', 'solicitante')),
    ('acta de recibo', ('c', 'acta de recibo del patrimonio o aportes', '', 'solicitante')),
    ('acta de visita con fecha', VISITA),
    ('acta del accidente', ('a', 'acta del accidente de trabajo', 'emisor_variable', 'empleador (Gobernación para docentes oficiales)')),
    ('acta o actas de la asamblea', ACTAS),
    ('actas de la asamblea', ACTAS),
    ('actas de la junta directiva', ACTAS),
    ('actas de liquidacion', ('c', 'actas de liquidación', '', 'solicitante')),
    ('actas de sesiones', ACTAS),
    ('actas en donde conste', ACTAS),
    ('acto administrativo de creacion', CREA),
    ('acto administrativo de nombramiento', ('c', 'acto de nombramiento del representante legal', '', 'solicitante')),
    ('acto administrativo de retiro', RETIRO),
    ('acto administrativo emitido por el instituto colombiano agropecuario', ('b', 'acto administrativo del ICA', '', 'ICA')),
    ('acto administrativo mediante el cual se crean', CREA),
    ('acto contrato negocio', ('c', 'acto, contrato o providencia objeto de registro', 'tercero_privado;emisor_variable', 'partes, notaría o juez')),
    ('autoevaluacion', ('c', 'autoevaluación', '', 'solicitante')),
    ('carne de proteccion radiologica', ('c', 'carné de protección radiológica', 'tercero_privado;emisor_variable', 'entidad que imparte el curso')),
    ('carpeta folder', ('excluido', 'carpeta', 'no_es_documento', '—')),
    ('carta de solicitud', SOL),
    ('carta del prestador', SOL),
    ('carta especificando el servicio', ('c', 'descripción del servicio', '', 'solicitante')),
    ('cd que contenga', MATER),
    ('cedula de ciudadania', ID),
    ('cedula de extranjeria', ID),
    ('certificacion bancaria', ('c', 'certificación bancaria', 'tercero_privado', 'banco')),
    ('certificacion de capacitacion', CURSO),
    ('certificacion de conexion a internet', ('c', 'certificación de conexión a internet', 'tercero_privado', 'operador')),
    ('certificacion de estudios', NOTAS),
    ('certificacion de suficiencia', SUEF),
    ('certificacion del curso de manipulador', CURSO),
    ('certificacion laboral', LAB),
    ('certificacion medico de invalidez', INVAL),
    ('certificacion o constancia de la experiencia', EXPER),
    ('certificacion que acredite experiencia', EXPER),
    ('certificacion que acredite la efectividad', ('c', 'acta de recibo del patrimonio o aportes', '', 'solicitante')),
    ('certificado actualizado de la deuda', FNA),
    ('certificado antecedentes de la dian', ('b', 'certificado de antecedentes DIAN', '', 'DIAN')),
    ('certificado de antecedentes disciplinarios', ('b', 'certificado de antecedentes disciplinarios', '', 'Procuraduría General de la Nación')),
    ('certificado de antecedentes fiscales', ('b', 'certificado de antecedentes fiscales', '', 'Contraloría General de la República')),
    ('certificado de camara de comercio', CCIO),
    ('certificado de curso taller', CURSO),
    ('certificado de entidades administradoras de pension', PENS),
    ('certificado de escolaridad', ('b', 'certificado de escolaridad', 'emisor_variable', 'establecimiento educativo')),
    ('certificado de especialidad', ESPEC),
    ('certificado de existencia', CCIO),
    ('certificado de idoneidad del titulo', ('b', 'certificado de idoneidad del título de posgrado', '', 'Ministerio de Educación Nacional')),
    ('certificado de idoneidad sanitaria', ('b', 'certificado de idoneidad sanitaria', 'emisor_variable', 'autoridad sanitaria')),
    ('certificado de idoneidad', ('c', 'certificado de curso de aplicador', 'tercero_privado;emisor_variable', 'entidad que imparte el curso')),
    ('certificado de induccion al servicio social', ('b', 'certificado de inducción al servicio social obligatorio', 'emisor_variable', 'institución del servicio social')),
    ('certificado de ingresos y retenciones', ('b', 'certificado de ingresos y retenciones', 'emisor_variable', 'pagador (FOMAG u otro empleador)')),
    ('certificado de invalidez', INVAL),
    ('certificado de la compania aseguradora', ('c', 'certificado de aseguradora', 'tercero_privado', 'aseguradora')),
    ('certificado de la entidad oficial financiera', ('c', 'certificado de crédito', 'tercero_privado;emisor_variable', 'entidad financiera o persona natural')),
    ('certificado de la entidad que cancelaba', ('b', 'certificado de la entidad que pagaba las cesantías', 'emisor_variable', 'entidad pagadora anterior')),
    ('certificado de la especialidad', ESPEC),
    ('certificado de notas', NOTAS),
    ('certificado de publicacion', PUBLI),
    ('certificado de residencia', ('b', 'certificado de residencia', '', 'alcaldía')),
    ('certificado de salarios', ('a', 'certificado de salarios', 'emisor_variable', 'empleador (Gobernación para docentes oficiales)')),
    ('certificado de salud', ('c', 'certificado médico de salud', 'tercero_privado', 'médico')),
    ('certificado de semanas cotizadas', PENS),
    ('certificado de suficiencia', SUEF),
    ('certificado de terminacion', SSO_T),
    ('certificado de tiempo de servicio', ('a', 'certificado de tiempo de servicio', 'emisor_variable', 'Gobernación; otra entidad si hubo servicio en otra parte')),
    ('certificado de tradicion', TRAD),
    ('certificado de uso de suelo', SUELO),
    ('certificado laboral', LAB),
    ('certificado o manifestacion expresa de no poseer', ('c', 'manifestación de no poseer vivienda', 'declaracion', 'ciudadano')),
    ('certificado y o visita de habilitacion', ('a', 'certificado de habilitación', '', 'Secretaría de Salud Departamental')),
    ('certificados de control de calidad', ('c', 'certificados de control de calidad de equipos', 'tercero_privado', 'empresa de control de calidad')),
    ('comprobante de pago de la ultima mesada', ('b', 'comprobante de pago de mesada pensional', '', 'FOMAG / Fiduprevisora')),
    ('concepto sanitario o acta de visita', VISITA),
    ('concepto uso del suelo', SUELO),
    ('constancia de no haber sido sancionado', ('a', 'constancia de no sanción por comercio ilegal de medicamentos', 'emisor_variable', 'autoridad sanitaria')),
    ('constancia de trabajo', EXPER),
    ('constitucion legal en camara', CCIO),
    ('contenido de la capacitacion', ('c', 'contenido de la capacitación', '', 'solicitante')),
    ('contrato', CONTR),
    ('contrato del quimico farmaceutico o el certificado', ('c', 'contrato o inscripción del químico farmacéutico', 'tercero_privado;emisor_variable', 'empleador o autoridad sanitaria')),
    ('convalidacion de titulos', CONV),
    ('copia del denuncio', ('b', 'denuncia penal', '', 'Fiscalía General de la Nación')),
    ('declaracion de importacion', ('b', 'declaración de importación', '', 'DIAN')),
    ('declaracion de impuesto', GOB_PAGO),
    ('declaracion de terceros', MANIF),
    ('declaracion extra', DECL),
    ('declaracion juramentada', DECL),
    ('declaracion original de dos', ('c', 'declaración de profesionales', 'declaracion', 'profesionales')),
    ('declaracion tributaria', GOB_PAGO),
    ('declaraciones extra', DECL),
    ('derecho de peticion', SOL),
    ('descripcion de la ubicacion', ('c', 'descripción de la ubicación', '', 'solicitante')),
    ('diploma', DIPL),
    ('disponibilidad presupuestal', ('b', 'certificado de disponibilidad presupuestal', 'emisor_variable', 'entidad que contrata al profesional')),
    ('documento de identidad', ID),
    ('documento de identificacion', ID),
    ('documento de venta', CONTR),
    ('documento del estudiante', ID),
    ('documento que fue objeto de liquidacion', TRAD),
    ('documento que soporta la solicitud', ('c', 'soporte de la solicitud', '', 'solicitante')),
    ('en caso de haber sido exonerado', ('a', 'acta de comité de exoneración del servicio social obligatorio', 'emisor_variable', 'comité de servicio social obligatorio')),
    ('escritura publica', ('b', 'escritura pública', 'particular_funcion_publica', 'notaría')),
    ('estatutos', ('c', 'estatutos', '', 'solicitante')),
    ('estudio y evaluacion de la instalacion', ('c', 'estudio de la instalación de rayos X', 'tercero_privado', 'institución autorizada')),
    ('extracto de intereses', ('b', 'extracto de intereses de cesantías', '', 'FOMAG')),
    ('factura', ('c', 'factura', 'tercero_privado', 'vendedor')),
    ('fallo o sentencia', ('b', 'sentencia judicial', '', 'Rama Judicial')),
    ('formato sed', ('excluido', 'formato de la entidad', 'formulario_de_la_entidad', 'Gobernación')),
    ('formulario de declaracion y pago', GOB_PAGO),
    ('fotocopia de cedula', ID),
    ('fotocopia declaracion pago', GOB_PAGO),
    ('fotografias', ('c', 'fotografías', '', 'solicitante')),
    ('hoja de vida', HV),
    ('hojas de vida', HV),
    ('idoneidad del constructor', ('c', 'idoneidad del constructor', 'tercero_privado', 'constructor')),
    ('informacion sobre las operaciones', ('c', 'información técnica de la planta de agua', '', 'solicitante')),
    ('informe', ('c', 'informe del solicitante', '', 'solicitante')),
    ('libros de', ('c', 'libros de la entidad', '', 'solicitante')),
    ('licencia de construccion', ('b', 'licencia de construcción', 'particular_funcion_publica', 'curaduría urbana o municipio')),
    ('licencia de funcionamiento', LICGOB),
    ('licencia de transito', TRANS),
    ('licencia de uso y manejo', LICRAD),
    ('licencia inicial', LICGOB),
    ('licencia vigente de uso', LICRAD),
    ('listado de medicamentos', ('c', 'listado de medicamentos', '', 'solicitante')),
    ('manifestacion', MANIF),
    ('manisfestacion', MANIF),
    ('materiales', MATER),
    ('nota devolutiva', ('b', 'nota devolutiva de registro', 'registro_publico', 'Oficina de Registro de Instrumentos Públicos')),
    ('numero de identificacion tributaria', RUT),
    ('obra de caracter', ('c', 'obra científica o pedagógica', '', 'solicitante')),
    ('paz y salvo del fondo nacional', FNA),
    ('paz y salvo expedido por la pagaduria', ('a', 'paz y salvo de la pagaduría del empleador', 'emisor_variable', 'empleador (Gobernación para docentes oficiales)')),
    ('paz y salvo medicina legal', ('b', 'paz y salvo de Medicina Legal', '', 'Instituto Nacional de Medicina Legal')),
    ('pensum', NOTAS),
    ('planos', ('c', 'planos', '', 'solicitante')),
    ('poder', ('c', 'poder', '', 'solicitante')),
    ('poliza', ('c', 'póliza', 'tercero_privado', 'aseguradora')),
    ('presentacion de examen', ('excluido', 'examen', 'no_es_documento', '—')),
    ('programa o proyecto', ('c', 'programa o proyecto', '', 'solicitante')),
    ('proyecto de correccion', ('c', 'proyecto de corrección', '', 'solicitante')),
    ('publicacion de los edictos', PUBLI),
    ('recibo de pago u orden de matricula', ('b', 'recibo de matrícula', 'emisor_variable', 'institución educativa')),
    ('recibo de pago', GOB_PAGO),
    ('recibo de servicio publico', ('c', 'recibo de servicio público', 'tercero_privado;emisor_variable', 'empresa de servicios públicos')),
    ('reconocimiento colciencias', ('b', 'reconocimiento de Minciencias', '', 'Minciencias')),
    ('reconocimiento deportivo', ('b', 'reconocimiento deportivo', 'emisor_variable', 'ente deportivo competente (por confirmar)')),
    ('registro certificado del programa', ('b', 'registro calificado del programa', '', 'Ministerio de Educación Nacional')),
    ('registro civil de defuncion', ('b', 'registro civil de defunción', 'registro_publico', 'Registraduría / notarías')),
    ('registro civil de matrimonio', ('b', 'registro civil de matrimonio', 'registro_publico', 'Registraduría / notarías')),
    ('registro civil de nacimiento', ('b', 'registro civil de nacimiento', 'registro_publico', 'Registraduría / notarías')),
    ('registro de defuncion', ('b', 'registro civil de defunción', 'registro_publico', 'Registraduría / notarías')),
    ('registro mercantil', CCIO),
    ('registro profesional', ('a', 'registro profesional en salud', 'emisor_variable', 'Secretaría de Salud Departamental u otra autoridad')),
    ('registro unico tributario', RUT),
    ('registros historicos', ('c', 'registros históricos de caracterización', '', 'solicitante')),
    ('reglamento de seguridad', ('c', 'reglamento de seguridad', '', 'solicitante')),
    ('relacion del personal', ('c', 'relación del personal docente', '', 'solicitante')),
    ('reporte anuales de las cesantias', REPCES),
    ('reportes anuales de las cesantias', REPCES),
    ('resolucion con que lo pensiono', PENSION),
    ('resolucion de autorizacion de las etiquetas', ('a', 'resolución de autorización de etiquetas', '', 'Gobernación (Hacienda; por confirmar)')),
    ('resolucion de cesantias', CESANT),
    ('resolucion de convalidacion', CONV),
    ('resolucion de retiro', RETIRO),
    ('resolucion que', PENSION),
    ('revision tecnico', ('b', 'revisión técnico-mecánica', 'particular_funcion_publica', 'centro de diagnóstico automotor')),
    ('solicitud', SOL),
    ('sulicitud', SOL),
    ('tarjeta de propiedad', TRANS),
    ('tarjeta de reservista', ('b', 'libreta militar', '', 'Ejército Nacional')),
    ('tarjeta profesional', ('b', 'tarjeta profesional', 'emisor_variable', 'consejo o colegio profesional')),
    ('titulo de estudios', DIPL),
    ('titulo posgrado', DIPL),
    ('titulo valor', TVAL),
    ('titulos firmados', TVAL),
    ('titulos profesionales', DIPL),
    ('tornaguia', ('a', 'tornaguía', 'emisor_variable', 'Gobernación (Hacienda) u otro departamento')),
    ('ultima resolucion de cesantias', CESANT),
]
R.sort(key=lambda x: -len(x[0]))


def code(n):
    for p, v in R:
        if (p == '' and n == '') or (p and n.startswith(p)):
            return v
    return None


src, out = sys.argv[1], sys.argv[2]
rows = [x for x in csv.DictReader(open(src, encoding='utf-8')) if x['tipo'] == 'DOCUMENTO']
sin = sorted({norm(x['nombre']) for x in rows if code(norm(x['nombre'])) is None})
if sin:
    print('SIN CÓDIGO:', sin)
    sys.exit(1)
M = {}
for x in rows:
    cat, can, marcas, emisor = code(norm(x['nombre']))
    k = (x['codigo'], can)
    m = M.setdefault(k, {'codigo': x['codigo'], 'n_catalogo': x['n_catalogo'], 'tramite': x['nombre_govco'],
                         'en_linea_govco': x['en_linea_govco'], 'documento': can, 'categoria': cat, 'marcas': marcas,
                         'emisor': emisor, 'nombres_en_ficha': set(), 'filas_ficha': 0, 'condicional': False})
    m['nombres_en_ficha'].add(x['nombre'].strip())
    m['filas_ficha'] += 1
    if x['excepcion'] or re.search(r'\b(si |en caso|cuando|solo aplica)', ((x['detalle'] or '') + ' ' + (x['nombre'] or '')).lower()):
        m['condicional'] = True
cols = ['codigo', 'n_catalogo', 'tramite', 'en_linea_govco', 'documento', 'categoria', 'marcas', 'emisor',
        'condicional', 'filas_ficha', 'nombres_en_ficha']
w = csv.writer(open(out, 'w', encoding='utf-8', newline=''))
w.writerow(cols)
for m in sorted(M.values(), key=lambda m: (int(m['codigo']), m['documento'])):
    m['nombres_en_ficha'] = ' | '.join(sorted(m['nombres_en_ficha']))
    w.writerow([m[c] for c in cols])
D = [m for m in M.values() if m['categoria'] != 'excluido']
print('requisitos documentales:', len(D), 'en', len({m['codigo'] for m in D}), 'trámites; excluidos:', len(M) - len(D))
for c in 'abc':
    n = sum(m['categoria'] == c for m in D)
    print(c, n, f"{100 * n / len(D):.1f} %")
for mk in ['emisor_variable', 'registro_publico', 'particular_funcion_publica', 'tercero_privado', 'declaracion']:
    print(mk, sum(mk in m['marcas'] for m in D))
print('condicionales', sum(m['condicional'] for m in D))
