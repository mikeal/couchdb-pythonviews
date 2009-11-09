# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
CLEANUP       = "/Users/mikeal/Documents/git/couchdb-wsgi/cleanup.py"

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d dirbuild/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html dirhtml pickle json htmlhelp qthelp latex changes linkcheck doctest

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  dirhtml   to make HTML files named index.html in directories"
	@echo "  pickle    to make pickle files"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  qthelp    to make HTML files and a qthelp project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo "  doctest   to run all doctests embedded in the documentation (if enabled)"

clean:
	-rm -rf dirbuild/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) .
	@echo
	@echo "Build finished. The HTML pages are in ."
	$(CLEANUP)

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) dirbuild/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in dirbuild/dirhtml."

pickle:
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) dirbuild/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

json:
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) dirbuild/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) dirbuild/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in dirbuild/htmlhelp."

qthelp:
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS) dirbuild/qthelp
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in dirbuild/qthelp, like this:"
	@echo "# qcollectiongenerator dirbuild/qthelp/couchdb-wsgi.qhcp"
	@echo "To view the help file:"
	@echo "# assistant -collectionFile dirbuild/qthelp/couchdb-wsgi.qhc"

latex:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) dirbuild/latex
	@echo
	@echo "Build finished; the LaTeX files are in dirbuild/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) dirbuild/changes
	@echo
	@echo "The overview file is in dirbuild/changes."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) dirbuild/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in dirbuild/linkcheck/output.txt."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) dirbuild/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in dirbuild/doctest/output.txt."
