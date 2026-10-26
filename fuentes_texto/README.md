# Texto de las fuentes

Texto extraído de los PDF de la carpeta del proyecto, con marcas `=== pN ===` al inicio de cada página (N = página del archivo PDF). Sirve para verificar cifras y citas con página (skill `libro-de-hechos`, agentes `verificador-de-fuentes` y `auditor-tribunal`). Generado el 2026-10-21.

| Archivo | Fuente (ID del libro) | Cómo se obtuvo |
|---|---|---|
| `F-001_oficio_condonacion.txt` | `respuestaGobernacion.pdf` | `herramientas/extraer_pdf.py` |
| `F-002_oficio_peti.txt` | `ecd5be2e27b98ffdc57ad3892feb38c6.pdf` | `herramientas/extraer_pdf.py` |
| `F-003_tesis_cobit.txt` | `PROYECTO_ULTIMATUS (7).pdf` | `herramientas/extraer_pdf.py` |
| `F-005_proyecto_ordenanza.txt` | `Proyecto_de_Ordenanza_Plan_de_Desarrollo_...pdf` | `herramientas/extraer_pdf.py` |
| `F-006_informe_seguimiento.txt` | `INFORME_DE_SEGUIMIENTO_PLAN_DE_DESARROLLO_CORTE_JUNIO_2026.pdf` | `herramientas/extraer_pdf.py` |
| `F-007_peti_ocr.txt` | `1. PETI_2026 V1 (1).pdf` (escaneado) | OCR de `PETI_imagenes/` con `herramientas/ocr_imagenes.swift` (macOS Vision) |
| `F-008_datos_maestros.txt` | `GOBERNACION_DEL_HUILA-Datos_Maestros-De_Referencia.pdf` | `herramientas/extraer_pdf.py` |

## Archivos nuevos
Desde el 2026-10-25 los documentos nuevos se incorporan con el skill `incorporar-fuente`
(`herramientas/incorporar_fuente.py`): el original queda en `fuentes_originales/<ID>_<slug>/`
(con `descarga.json` y huella SHA-256 en `fuentes_originales/manifiesto.md`) y su texto aquí,
como `<ID>_<slug>.txt`, con las mismas marcas `=== pN ===`.

## Advertencias
- El texto por OCR (F-007) puede tener errores de lectura: ratifica con la imagen antes de citar literalmente.
- Las tablas extraídas pueden perder el orden de columnas; confirma la cifra en el PDF cuando importe la posición.
- Aún no hay texto de F-004 (Plan de Desarrollo adoptado, escaneado), F-009, F-010 ni F-011.

## Regenerar
```
pip3 install --target /tmp/libs pypdf
python3 herramientas/extraer_pdf.py /tmp/libs "<archivo>.pdf" salida.txt
swiftc -O -o /tmp/ocr herramientas/ocr_imagenes.swift && /tmp/ocr PETI_imagenes salida.txt
```
