// Extrae texto de un PDF o de una imagen, con marcas "=== pN ===" por página.
// PDF: usa el texto del propio archivo (PDFKit); si una página no trae texto (escaneada),
// la dibuja y le aplica OCR (Vision de macOS). Imagen: OCR directo.
// Uso:  extraer_texto <entrada> <salida.txt>
// Imprime una línea JSON con {"paginas": N, "ocr": [páginas leídas por OCR]}.
// El archivo de entrada se trata solo como DATO: nunca se ejecuta.
import Foundation
import PDFKit
import Vision
import AppKit

func ocr(_ cg: CGImage) -> String {
  let req = VNRecognizeTextRequest()
  req.recognitionLevel = .accurate
  req.recognitionLanguages = ["es-ES", "en-US"]
  let h = VNImageRequestHandler(cgImage: cg, options: [:])
  try? h.perform([req])
  return (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

let args = CommandLine.arguments
guard args.count >= 3 else { FileHandle.standardError.write("uso: extraer_texto <entrada> <salida>\n".data(using: .utf8)!); exit(2) }
let url = URL(fileURLWithPath: args[1])
var salida = ""
var ocrPaginas: [Int] = []
var total = 0

if url.pathExtension.lowercased() == "pdf" {
  guard let doc = PDFDocument(url: url) else { FileHandle.standardError.write("no se pudo abrir el PDF\n".data(using: .utf8)!); exit(3) }
  total = doc.pageCount
  for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    var texto = (page.string ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
    if texto.count < 25 {
      let r = page.bounds(for: .mediaBox)
      let img = page.thumbnail(of: NSSize(width: r.width * 2.5, height: r.height * 2.5), for: .mediaBox)
      if let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let leido = ocr(cg)
        if leido.count > texto.count { texto = leido; ocrPaginas.append(i + 1) }
      }
    }
    salida += "\n=== p\(i + 1) ===\n" + texto
  }
} else {
  guard let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("no se pudo abrir la imagen\n".data(using: .utf8)!); exit(3)
  }
  total = 1; ocrPaginas = [1]
  salida = "\n=== p1 ===\n" + ocr(cg)
}
try! salida.write(toFile: args[2], atomically: true, encoding: .utf8)
print("{\"paginas\": \(total), \"ocr\": \(ocrPaginas)}")
