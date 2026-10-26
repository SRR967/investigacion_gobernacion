import Foundation
import Vision
import AppKit
let dir = CommandLine.arguments[1]
let out = CommandLine.arguments[2]
let files = try! FileManager.default.contentsOfDirectory(atPath: dir).filter{ $0.hasPrefix("pagina_") && $0.hasSuffix(".png") }.sorted()
var result = ""
for f in files {
  guard let img = NSImage(contentsOfFile: dir + "/" + f), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
  let req = VNRecognizeTextRequest()
  req.recognitionLevel = .accurate
  req.recognitionLanguages = ["es-ES"]
  let h = VNImageRequestHandler(cgImage: cg, options: [:])
  try? h.perform([req])
  let text = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
  let n = f.replacingOccurrences(of: "pagina_", with: "").replacingOccurrences(of: ".png", with: "")
  result += "\n=== p\(Int(n) ?? 0) ===\n" + text
}
try! result.write(toFile: out, atomically: true, encoding: .utf8)
