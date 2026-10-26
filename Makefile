LATEXMK = latexmk -pdf -outdir=build -interaction=nonstopmode -synctex=1

all:
	mkdir -p build && $(LATEXMK) main.tex

# Modo final: la compilación falla si queda cualquier \pendiente{...}
final: clean
	mkdir -p build && $(LATEXMK) -pretex='\def\modofinal{1}' -usepretex main.tex

clean:
	latexmk -C -outdir=build main.tex || true
	rm -rf build
