# Introducción

## Planteamiento del problema

En Colombia, el Decreto 088 de 2022 establece los lineamientos, plazos y condiciones para la digitalización y automatización de los trámites. Para las gobernaciones, la norma fija que el primer 30 % de los trámites debe estar digitalizado hasta mayo de 2028, el 60 % hasta julio de 2031 y el total hasta marzo de 2034 [@colombia2022decreto088, art. 2.2.20.7]. Además, dispone que las iniciativas de digitalización y automatización de trámites "deben incorporarse en el plan estratégico de tecnologías de información (PETI) de cada entidad" [@colombia2022decreto088, Anexo 1, num. 2.3.2]. Además, la normativa colombiana prohíbe exigir al ciudadano "actos administrativos, constancias, certificaciones o documentos que ya reposen en la entidad ante la cual se está tramitando la respectiva actuación" [@colombia2012decreto019, art. 9], y el Decreto 620 de 2020 dispone incluir "los mecanismos de interoperabilidad necesarios que permitan hacer más ágiles y eficientes los trámites y servicios evitando solicitar información a ciudadanos y empresas a la que puedan acceder, consultar o solicitar a otra entidad" [@colombia2020decreto620, art. 2.2.17.4.7, num. 8]. De esta manera, la digitalización de los trámites y el intercambio de información entre bases de datos se encuentran vinculados en la normativa vigente.

En el caso de la Gobernación del Huila, el diagnóstico del Plan de Desarrollo Departamental 2024-2027 reporta 86 trámites inscritos en el Sistema Único de Información de Trámites (SUIT), de los cuales 23 estaban en línea, 15 parcialmente en línea y 48 eran presenciales [@gobernaciondelhuila2024ordenanza, p. 32]. La entidad ha avanzado en la racionalización de sus trámites. Su Programa de Transparencia y Ética Pública (PTEP) 2026-2027 registra una calificación de 90,5 sobre 100 en la política de racionalización de trámites para la vigencia 2024 [@gobernaciondelhuila2026ptep, pp. 75, 134] y prioriza cinco trámites para racionalización tecnológica durante 2026 [@gobernaciondelhuila2026ptep, pp. 135-136].

No obstante, el mismo programa reconoce una limitación. Su diagnóstico preliminar para la vigencia 2026 "identifica una necesidad de profundizar en la interoperabilidad de bases de datos, ya que persiste la solicitud de documentos que la entidad ya posee o que pueden consultarse en línea", y señala que, "a pesar de los avances en años anteriores", ciertos trámites de alto impacto "aún presentan cuellos de botella que generan percepciones de ineficiencia" [@gobernaciondelhuila2026ptep, p. 134]. Los requisitos que la entidad registró en el SUIT, según los datos abiertos disponibles con corte a febrero de 2022, apuntan en la misma dirección. Entre los documentos que se piden al ciudadano figuran certificados de tiempo de servicio y actos administrativos de retiro del servicio, que podrían corresponder a información de la propia administración, así como documentos expedidos por otras entidades, como certificados de existencia y representación legal y de semanas cotizadas [@funcionpublica2022suit] [CONFIRMAR: vigencia de los requisitos y entidad que expide cada documento (P-035, P-038)]. Además, la Gobernación ofrece en su sede electrónica un trámite propio para expedir certificados laborales, salariales y de tiempo de servicio [@gobernaciondelhuila2026tramites] [CONFIRMAR].

Considerando lo anterior, la Gobernación del Huila sigue solicitando a los ciudadanos, en sus trámites, documentos que ella misma posee o que podría consultar en línea, situación ante la cual su propio diagnóstico identifica la necesidad de profundizar en la interoperabilidad de sus bases de datos. Mientras esa solicitud persista, el ciudadano debe obtener y entregar información que la administración ya tiene, lo que puede limitar que esos trámites se realicen completamente en línea. Esta situación da lugar a la pregunta que orienta el estudio.

## Pregunta de investigación

¿Cómo puede la Gobernación del Huila reducir la solicitud a los ciudadanos de documentos que ya posee o que puede consultar en línea, mediante la interoperabilidad de sus bases de datos con los trámites? [DATO PENDIENTE: pregunta propuesta; por ratificar por el autor (P-018)]

## Justificación

El estudio se justifica desde las perspectivas institucional, normativa, tecnológica y académica. En el plano institucional, el problema que aborda está formulado por la propia entidad en el diagnóstico de su PTEP 2026 [@gobernaciondelhuila2026ptep, p. 134]. Además, la reducción de trámites para facilitar el acceso del ciudadano figura entre las estrategias del Sector 45 del Plan de Desarrollo Departamental 2024-2027 "Por Un Huila Grande" [@gobernaciondelhuila2024ordenanza, p. 187]. Una propuesta que identifique qué documentos pueden dejar de pedirse y qué datos habría que conectar para ello puede servir de insumo para las acciones de racionalización que la entidad formula en su PTEP [DATO PENDIENTE: anclaje a un producto o meta del Programa 4599 del Plan de Desarrollo (P-030)].

En el plano normativo, el Decreto 088 de 2022 obliga a las autoridades a adoptar y aplicar la guía de digitalización y automatización de trámites contenida en su Anexo 1 [@colombia2022decreto088, art. 2.2.20.4]. Según esa guía, las iniciativas de digitalización deben incorporarse en el PETI y, cuando generan un beneficio directo al ciudadano, registrarse además como acciones de racionalización en el plan anticorrupción [@colombia2022decreto088, Anexo 1, num. 2.3.2]. Asimismo, el Decreto Ley 019 de 2012 y el Decreto 620 de 2020 respaldan que la entidad consulte la información que posee o que reposa en otras entidades en lugar de solicitarla [@colombia2012decreto019, art. 9; @colombia2020decreto620, art. 2.2.17.4.7, num. 8]. Por ello, el estudio formula su propuesta en el formato de una iniciativa del PETI, con acciones que puedan registrarse también en el PTEP.

En el plano tecnológico, el estudio aplica la formación del autor en ingeniería de sistemas a un problema de datos: identificar qué información exigen los trámites, quién la produce y dónde se encuentra, para proponer qué conexiones entre bases de datos permitirían que la entidad la consulte en lugar de pedirla. El análisis se realiza a partir de información pública, como los requisitos registrados en el SUIT y el catálogo de trámites de la entidad. Por tanto, no sustituye el conocimiento de los sistemas internos, pero puede orientar su priorización.

En el plano académico, el estudio puede aportar un caso documentado sobre la interoperabilidad de datos como condición para la digitalización de trámites en una entidad territorial colombiana [FALTA FUENTE: estado de la literatura sobre interoperabilidad y carga documental en trámites; depende de la revisión de literatura]. Finalmente, el estudio responde a la exigencia de que el trabajo sea de interés para el Departamento y guarde concordancia con el plan de desarrollo departamental (Secretaría de Educación, Gobernación del Huila, comunicación personal, 10 de marzo de 2026).

## Objetivos

[DATO PENDIENTE: objetivos propuestos el 2026-10-21; por ratificar por el autor (P-018)]

### Objetivo general

Diseñar una propuesta de interoperabilidad de datos para los trámites de la Gobernación del Huila que permita reducir la solicitud a los ciudadanos de documentos que la entidad posee o puede consultar en línea.

### Objetivos específicos

1. Identificar los documentos que exigen los trámites de la Gobernación del Huila y clasificarlos según quién los expide (la propia Gobernación, otra entidad pública o el ciudadano), a partir de los requisitos registrados en el SUIT y del catálogo de trámites de la entidad.

2. Relacionar los documentos expedidos por la Gobernación o por otras entidades públicas con las bases de datos de la entidad y con los mecanismos de intercambio de información disponibles.

3. Diseñar la propuesta de interoperabilidad, indicando qué datos conectar, con qué trámites y en qué orden, en el formato de una iniciativa del PETI y sin estimación de costos.

4. Evaluar la propuesta con criterios de coherencia normativa y factibilidad mediante revisión documental.

## Alcance y delimitación

[DATO PENDIENTE: alcance y límites del estudio; propuesta en la ficha del libro (P-018)]

## Organización del documento

[DATO PENDIENTE: organización del documento; se redacta al cerrar la estructura]

---

## Informe de entrega (no forma parte del texto)

**Hechos usados:**
- Verificados: H-054, H-064, H-051, H-053, H-056, H-058, H-068 y H-001.
- Verificados en la ronda 1: H-077, H-078 (existencia, conteo de 467 y periodo), H-080 (DL 019 art. 9) y H-081 (Decreto 620). Pendientes, marcados [CONFIRMAR]: clasificación por emisor y vigencia de los requisitos (H-078, H-082) y trámite de certificados del portal (H-079).

**Marcas abiertas:**
- 3 [CONFIRMAR].
- 1 [FALTA FUENTE]: literatura.
- 5 [DATO PENDIENTE]: pregunta, objetivos, alcance, organización y anclaje al Programa 4599.

**Decisiones para Santiago:**
- Ratificar la pregunta y los objetivos (P-018).
- Exportar el CSV del SUIT (P-035).

**Versión anterior:** `historial/01_introduccion_2026-10-21_tramites_v2.md`.

**Documentos y términos explicados:**
- **Interoperabilidad:** que los sistemas se pasen datos entre sí, para que la entidad consulte la información en vez de pedirla al ciudadano.
- **SUIT:** el registro nacional de trámites de Función Pública. Allí cada entidad publica los requisitos de cada trámite.
- **Datos abiertos (datos.gov.co):** el portal nacional donde el Estado publica bases de datos. Allí está la tabla del SUIT con los requisitos.
- **PTEP:** el plan anual contra la corrupción y para la atención al ciudadano. Su diagnóstico de 2026 es el que plantea el problema.
