# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: CC0-1.0

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= --fresh-env
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = ../build/docs

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
