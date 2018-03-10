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

# Declar the sdaps binary to use
# SDAPS=sdaps
SDAPS=~/applications/sdaps-1.2.1/sdaps.py


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
	$(SDAPS) $(SURVEY) setup_tex --add ciit-survey.sty --add comsats-logo.pdf answer-sheet.tex
#	# ciit-survey.sty and comsats-logo.pdf need to be added explicitly to survey/ for the compilation to work


# Create questionnaires with the specified Questionnaire IDs (in ids.txt)
questionnires:
	$(SDAPS) $(SURVEY) stamp -f ids.txt

# Convert scanned pdf to black-and-white monochrome tiff file for sdaps processing
convert:
	gs -sDEVICE=tiffg4 -dBATCH -dNOPAUSE -r600 -sOutputFile="scan.tif" scan.pdf

# Refresh the inner 'survey' file which basically removes ALL added and recognized pages
# Requires that survey/survey be copied to survey/survey.fresh IMMEDIATELY after the 'setup' step (fresh state)
refresh:
	cp survey/survey.fresh survey/survey

# Add the scanned and converted image to sdaps for processing
add:
	$(SDAPS) $(SURVEY) add scan.tif


# Perform OMR on the added data
recognize:
	$(SDAPS) $(SURVEY) recognize -r


# Run SDAPS gui to make manual corrections
gui:
	$(SDAPS) $(SURVEY) gui


# Generate report
report:
	$(SDAPS) $(SURVEY) report


# Generate csv file of recognized data
csv:
	$(SDAPS) $(SURVEY) csv export


.PHONY: clean force once all show setup convert add recognize gui report csv
# Source: https://drewsilcock.co.uk/using-make-and-latexmk
