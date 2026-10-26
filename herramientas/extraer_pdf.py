import sys
sys.path.insert(0, sys.argv[1])
from pypdf import PdfReader
r=PdfReader(sys.argv[2]); print("PAGES",len(r.pages))
out=open(sys.argv[3],'w')
for i,p in enumerate(r.pages):
    out.write(f"\n=== p{i+1} ===\n"+(p.extract_text() or ''))
