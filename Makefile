LATEX=pdflatex
LATEXOPT=--shell-escape
NONSTOP=--interaction=nonstopmode

LATEXMK=latexmk
LATEXMKOPT=-pdf
CONTINUOUS=


MAIN=answer-sheet
SOURCES=$(MAIN).tex Makefile
FIGURES := #$(shell find data/*.pdf diag/*.pdf -type f)

# Declare the folder where the sdaps will create questionnaire and store the results
SURVEY=survey


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

# SDAPS targets

setup:
	rm -rf $(SURVEY)/
	sdaps $(SURVEY) setup_tex --add ciit-survey.sty --add comsats-logo.pdf answer-sheet.tex
#	# ciit-survey.sty and comsats-logo.pdf need to be added explicitly to survey/ for the compilation to work

# Convert scanned pdf to black-and-white monochrome tiff file for sdaps processing
convert:
	gs -sDEVICE=tiffg4 -dBATCH -dNOPAUSE -r600 -sOutputFile="scan.tif" scan.pdf

# Add the scanned and converted image to sdaps for processing
add:
	sdaps $(SURVEY) add scan.tif


# Perform OMR on the added data
recognize:
	sdaps $(SURVEY) recognize


# Run SDAPS gui to make manual corrections
gui:
	sdaps $(SURVEY) gui


# Generate report
report:
	sdaps $(SURVEY) report


# Generate csv file of recognized data
csv:
	sdaps $(SURVEY) csv export


.PHONY: clean force once all show setup convert add recognize gui report csv
# Source: https://drewsilcock.co.uk/using-make-and-latexmk
