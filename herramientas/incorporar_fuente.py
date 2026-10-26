#!/usr/bin/env python3
"""Incorpora un archivo (descargado de una URL o recibido localmente) al proyecto.

Uso (ejecutar siempre con `python3 -I`, desde cualquier carpeta):
  python3 -I herramientas/incorporar_fuente.py url <URL> --id F-028 --slug oficio_decreto_x
  python3 -I herramientas/incorporar_fuente.py archivo <RUTA> --id F-028 --slug oficio_decreto_x [--url <URL de origen>]
  python3 -I herramientas/incorporar_fuente.py consultar <URL>      (muestra nombre, tipo y tamaño SIN descargar)

Qué hace (y nada más):
  1. Descarga (o copia) el archivo a su propia carpeta nueva `fuentes_originales/<ID>_<slug>/`.
  2. Calcula SHA-256, tamaño y tipo real (por los primeros bytes, no por la extensión).
  3. Extrae el texto a `fuentes_texto/<ID>_<slug>.txt` con marcas `=== pN ===`
     (PDF e imágenes con macOS PDFKit/Vision; docx, xlsx, html y txt con la biblioteca estándar).
  4. Escribe `descarga.json` en la carpeta y añade una fila a `fuentes_originales/manifiesto.md`.
El archivo se trata SIEMPRE como dato: no se abre con programas externos ni se ejecuta.
El registro en el libro de hechos (fuente, hechos, explicación) lo hace el skill `incorporar-fuente`.

Códigos de salida: 0 ok · 2 argumentos · 3 dominio no permitido (pedir confirmación a Santiago)
· 4 duplicado (mismo SHA-256) · 5 tipo bloqueado · 6 descarga fallida / demasiado grande.
"""
import argparse, datetime, hashlib, html.parser, json, os, re, shutil, subprocess, sys, tempfile
import urllib.error, urllib.parse, urllib.request, zipfile
import xml.etree.ElementTree as ET

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
EXT_BLOQUEADAS = {".exe", ".dmg", ".pkg", ".app", ".sh", ".command", ".bat", ".cmd", ".js", ".jar",
                  ".msi", ".scr", ".py", ".pl", ".rb", ".ps1", ".vbs", ".apk", ".iso", ".dll", ".so", ".dylib"}
MAGIC_BLOQUEADOS = [b"MZ", b"\x7fELF", b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe",
                    b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"#!"]


def hoy():
    return datetime.date.today().isoformat()


def salir(codigo, msg):
    print(json.dumps({"ok": False, "codigo": codigo, "mensaje": msg}, ensure_ascii=False))
    sys.exit(codigo)


def hosts_del_libro(raiz):
    """Dominios que ya figuran como URL de origen en el libro de hechos."""
    hosts = set()
    ruta = os.path.join(raiz, "libro_de_hechos.md")
    if os.path.exists(ruta):
        for m in re.finditer(r"https?://[^\s|)>\]]+", open(ruta, encoding="utf8").read()):
            h = urllib.parse.urlparse(m.group(0)).hostname
            if h:
                hosts.add(h.lower())
    return hosts


def host_permitido(host, extra):
    host = (host or "").lower()
    return host.endswith(".gov.co") or host == "gov.co" or host in extra


class RedirigirSoloPermitidos(urllib.request.HTTPRedirectHandler):
    def __init__(self, extra, confirmado):
        self.extra, self.confirmado = extra, confirmado

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        h = urllib.parse.urlparse(newurl).hostname
        if not self.confirmado and not host_permitido(h, self.extra):
            salir(3, f"La URL redirige a un dominio no permitido automáticamente: {h}. Pide confirmación a Santiago.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sanear_nombre(nombre):
    nombre = os.path.basename(urllib.parse.unquote(nombre or "")).strip().replace("\x00", "")
    nombre = re.sub(r"[^\w.\- ()áéíóúÁÉÍÓÚñÑ]", "_", nombre)[:120].strip(" .")
    return nombre or "archivo"


def nombre_desde_respuesta(resp, url):
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd, re.I)
    if m:
        return sanear_nombre(m.group(1))
    return sanear_nombre(urllib.parse.urlparse(url).path.rsplit("/", 1)[-1])


def tipo_real(ruta):
    with open(ruta, "rb") as f:
        cab = f.read(4096)
    for mg in MAGIC_BLOQUEADOS:
        if cab.startswith(mg):
            return "BLOQUEADO"
    if cab.startswith(b"%PDF"):
        return "pdf"
    if cab[:2] == b"PK":
        try:
            nombres = zipfile.ZipFile(ruta).namelist()
        except zipfile.BadZipFile:
            return "zip"
        if any(n.startswith("word/") for n in nombres):
            return "docx"
        if any(n.startswith("xl/") for n in nombres):
            return "xlsx"
        return "zip"
    if cab.startswith(b"\x89PNG") or cab[:3] == b"\xff\xd8\xff" or cab[:4] in (b"II*\x00", b"MM\x00*"):
        return "imagen"
    bajo = cab.lower()
    if b"<html" in bajo or b"<!doctype html" in bajo:
        return "html"
    try:
        cab.decode("utf-8")
        return "texto"
    except UnicodeDecodeError:
        return "otro"


class _HTMLaTexto(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes, self.saltar = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.saltar += 1
        if tag in ("p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"):
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.saltar:
            self.saltar -= 1

    def handle_data(self, d):
        if not self.saltar:
            self.partes.append(d)


def texto_docx(ruta):
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", "\t", xml)
    return "\n=== p1 ===\n" + re.sub(r"<[^>]+>", "", xml)


def texto_xlsx(ruta):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(ruta) as z:
        comp = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
                comp.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
        salida, hojas = "", sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for i, hoja in enumerate(hojas, 1):
            salida += f"\n=== p{i} ===\n"
            for fila in ET.fromstring(z.read(hoja)).iter("{%s}row" % ns["m"]):
                celdas = []
                for c in fila.findall("m:c", ns):
                    v = c.find("m:v", ns)
                    val = "" if v is None else (v.text or "")
                    if c.get("t") == "s" and val.isdigit() and int(val) < len(comp):
                        val = comp[int(val)]
                    celdas.append(val)
                salida += "\t".join(celdas) + "\n"
    return salida


def extraer(ruta, tipo, destino_txt):
    """Devuelve (paginas, paginas_ocr, advertencias)."""
    adv = []
    if tipo in ("pdf", "imagen"):
        tmp = tempfile.mkdtemp(prefix="extraer_")
        binario = os.path.join(tmp, "extraer_texto")
        fuente = os.path.join(RAIZ, "herramientas", "extraer_texto.swift")
        comp = subprocess.run(["swiftc", "-O", "-o", binario, fuente], capture_output=True, text=True)
        if comp.returncode != 0:
            return None, [], ["No se pudo compilar el extractor de texto: " + comp.stderr[-300:]]
        r = subprocess.run([binario, ruta, destino_txt], capture_output=True, text=True)
        shutil.rmtree(tmp, ignore_errors=True)
        if r.returncode != 0:
            return None, [], ["Falló la extracción de texto: " + r.stderr.strip()[-300:]]
        info = json.loads(r.stdout.strip().splitlines()[-1])
        if info["ocr"]:
            adv.append(f"Páginas leídas por OCR (pueden tener errores): {info['ocr']}")
        return info["paginas"], info["ocr"], adv
    if tipo == "docx":
        texto = texto_docx(ruta)
    elif tipo == "xlsx":
        texto = texto_xlsx(ruta)
    elif tipo == "html":
        p = _HTMLaTexto()
        p.feed(open(ruta, encoding="utf8", errors="replace").read())
        texto = "\n=== p1 ===\n" + re.sub(r"\n\s*\n+", "\n\n", "".join(p.partes))
    elif tipo == "texto":
        texto = "\n=== p1 ===\n" + open(ruta, encoding="utf8", errors="replace").read()
    else:
        return None, [], [f"Tipo '{tipo}': no se extrajo texto automáticamente."]
    open(destino_txt, "w", encoding="utf8").write(texto)
    return len(re.findall(r"^=== p\d+ ===$", texto, re.M)) or 1, [], adv


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def duplicado(raiz, digest):
    man = os.path.join(raiz, "fuentes_originales", "manifiesto.md")
    if os.path.exists(man):
        for linea in open(man, encoding="utf8"):
            if digest in linea:
                return linea.strip()
    return None


def descargar(url, carpeta, max_mb, extra, confirmado):
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("https", "http"):
        salir(2, "Solo se admiten URL http o https.")
    if not confirmado and not host_permitido(p.hostname, extra):
        salir(3, f"Dominio no permitido automáticamente: {p.hostname}. Pide confirmación a Santiago (nombre, origen, tamaño) y repite con --confirmado.")
    abrir = urllib.request.build_opener(RedirigirSoloPermitidos(extra, confirmado))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (investigacion-academica)"})
    try:
        resp = abrir.open(req, timeout=60)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        salir(6, f"No se pudo descargar: {e}")
    nombre = nombre_desde_respuesta(resp, resp.geturl())
    if os.path.splitext(nombre)[1].lower() in EXT_BLOQUEADAS:
        salir(5, f"Extensión bloqueada: {nombre}")
    limite = int(max_mb * 1024 * 1024)
    destino = os.path.join(carpeta, nombre)
    total = 0
    with open(destino, "wb") as f:
        while True:
            bloque = resp.read(1 << 20)
            if not bloque:
                break
            total += len(bloque)
            if total > limite:
                f.close(); os.remove(destino)
                salir(6, f"El archivo supera el límite de {max_mb} MB.")
            f.write(bloque)
    meta = {"final_url": resp.geturl(), "content_type": resp.headers.get("Content-Type"),
            "last_modified": resp.headers.get("Last-Modified")}
    return destino, nombre, meta


def consultar(url):
    """Solo cabeceras (HEAD): nombre, tipo y tamaño declarados por el servidor. No guarda nada."""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("https", "http"):
        salir(2, "Solo se admiten URL http o https.")
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (investigacion-academica)"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        salir(6, f"No se pudo consultar: {e}")
    tam = resp.headers.get("Content-Length")
    print(json.dumps({"ok": True, "url_final": resp.geturl(), "dominio": urllib.parse.urlparse(resp.geturl()).hostname,
                      "nombre": nombre_desde_respuesta(resp, resp.geturl()), "content_type": resp.headers.get("Content-Type"),
                      "bytes": int(tam) if tam and tam.isdigit() else None, "last_modified_servidor": resp.headers.get("Last-Modified")},
                     ensure_ascii=False, indent=2))
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["url", "archivo", "consultar"])
    ap.add_argument("origen")
    ap.add_argument("--id", help="ID de la fuente en el libro, p. ej. F-028")
    ap.add_argument("--slug")
    ap.add_argument("--url", help="URL de origen (modo archivo)")
    ap.add_argument("--max-mb", type=float, default=100)
    ap.add_argument("--confirmado", action="store_true", help="Santiago aprobó este dominio u origen")
    ap.add_argument("--raiz", default=RAIZ, help="Carpeta del proyecto (para pruebas)")
    a = ap.parse_args()
    if a.modo == "consultar":
        consultar(a.origen)
    if not (a.id and a.slug and re.fullmatch(r"F-\d{3}", a.id) and re.fullmatch(r"[a-z0-9_]{1,50}", a.slug)):
        salir(2, "ID con formato F-000 y slug en minúsculas, números y guion bajo.")

    raiz = os.path.abspath(a.raiz)
    carpeta = os.path.join(raiz, "fuentes_originales", f"{a.id}_{a.slug}")
    if os.path.exists(carpeta):
        salir(2, f"Ya existe {carpeta}; usa otro ID o slug.")
    os.makedirs(carpeta)
    try:
        if a.modo == "url":
            ruta, nombre, meta = descargar(a.origen, carpeta, a.max_mb, hosts_del_libro(raiz), a.confirmado)
            url_origen = a.origen
        else:
            if not os.path.isfile(a.origen):
                salir(2, "El archivo local no existe.")
            nombre = sanear_nombre(os.path.basename(a.origen))
            if os.path.splitext(nombre)[1].lower() in EXT_BLOQUEADAS:
                salir(5, f"Extensión bloqueada: {nombre}")
            ruta = os.path.join(carpeta, nombre)
            shutil.copy2(a.origen, ruta)
            meta, url_origen = {"final_url": a.url, "content_type": None, "last_modified": None}, a.url

        tipo = tipo_real(ruta)
        if tipo == "BLOQUEADO":
            salir(5, "El contenido parece un ejecutable o script; no se conserva.")
        digest = sha256(ruta)
        previa = duplicado(raiz, digest)
        if previa:
            salir(4, f"Ya existe un archivo idéntico registrado: {previa}")

        os.makedirs(os.path.join(raiz, "fuentes_texto"), exist_ok=True)
        txt = os.path.join(raiz, "fuentes_texto", f"{a.id}_{a.slug}.txt")
        paginas, ocr_pag, adv = extraer(ruta, tipo, txt)
        if tipo in ("zip", "otro"):
            adv.append("Archivo comprimido u otro formato: se conserva sin extraer ni abrir.")

        info = {"ok": True, "id": a.id, "slug": a.slug, "archivo": os.path.relpath(ruta, raiz),
                "texto": os.path.relpath(txt, raiz) if os.path.exists(txt) else None,
                "url_origen": url_origen, "url_final": meta.get("final_url"), "fecha_consulta": hoy(),
                "sha256": digest, "bytes": os.path.getsize(ruta), "tipo": tipo, "nombre_original": nombre,
                "content_type": meta.get("content_type"), "last_modified_servidor": meta.get("last_modified"),
                "paginas": paginas, "paginas_ocr": ocr_pag, "advertencias": adv}
        json.dump(info, open(os.path.join(carpeta, "descarga.json"), "w", encoding="utf8"), ensure_ascii=False, indent=2)

        man = os.path.join(raiz, "fuentes_originales", "manifiesto.md")
        if not os.path.exists(man):
            open(man, "w", encoding="utf8").write(
                "# Manifiesto de archivos originales\n\nUna fila por archivo incorporado con `herramientas/incorporar_fuente.py`. "
                "Los originales están en la carpeta de cada fuente; su texto, en `fuentes_texto/`.\n\n"
                "| ID | Archivo | Tipo | Págs. | SHA-256 | Bytes | URL de origen | Fecha de consulta |\n|---|---|---|---|---|---|---|---|\n")
        open(man, "a", encoding="utf8").write(
            f"| {a.id} | `{info['archivo']}` | {tipo} | {paginas or '—'} | {digest} | {info['bytes']} | {url_origen or '[sin URL]'} | {info['fecha_consulta']} |\n")
        print(json.dumps(info, ensure_ascii=False, indent=2))
    except SystemExit:
        if os.path.isdir(carpeta) and not os.path.exists(os.path.join(carpeta, "descarga.json")):
            shutil.rmtree(carpeta, ignore_errors=True)
        raise


if __name__ == "__main__":
    main()
