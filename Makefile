LATEX=pdflatex
LATEXOPT=--shell-escape
NONSTOP=--interaction=nonstopmode

LATEXMK=latexmk
LATEXMKOPT=-pdf
#CONTINUOUS=-pvc		# Used to update pdf in viewer
CONTINUOUS=


MAIN=answer-sheet
SOURCES=$(MAIN).tex Makefile
FIGURES := $(shell find data/*.pdf diag/*.pdf -type f)


all: show


show: $(MAIN).pdf
	vupdf $(MAIN).pdf


.refresh:
	touch .refresh


$(MAIN).pdf: $(MAIN).tex .refresh $(SOURCES) $(FIGURES) ciit-survey.sty sdaps.cls
		$(LATEXMK) $(LATEXMKOPT) $(CONTINUOUS) -pdflatex="$(LATEX) $(LATEXOPT) $(NONSTOP) %O %S" $(MAIN)

force:
		touch .refresh
		rm $(MAIN).pdf
		$(LATEXMK) $(LATEXMKOPT) $(CONTINUOUS) \
			-pdflatex="$(LATEX) $(LATEXOPT) %O %S" $(MAIN)

clean:
		$(LATEXMK) -C $(MAIN)
		rm -f $(MAIN).pdfsync
		rm -rf *~ *.tmp
		rm -f *.fmt *.bbl *.blg *.aux *.end *.fls *.log *.out *.fdb_latexmk
		rm -f *.eps *-converted-to.pdf
		rm -f *.bib

once:
		$(LATEXMK) $(LATEXMKOPT) -pdflatex="$(LATEX) $(LATEXOPT) %O %S" $(MAIN)

debug:
		$(LATEX) $(LATEXOPT) $(MAIN)

.PHONY: clean force once all show
# Source: https://drewsilcock.co.uk/using-make-and-latexmk
