# SPDX-FileCopyrightText: 2024 Thomas Breitner <t.breitner@csl.mpg.de>
#
# SPDX-License-Identifier: EUPL-1.2


.PHONY: requirements frontend docs

help:
	@echo "requirements - Updates requirements.txt and requirements-dev.txt"
	@echo "assets - Build frontend assets"
	@echo "docs - generate Sphinx HTML documentation"

requirements:
	python3 -m pip install --upgrade pip-tools pip wheel setuptools
	python3 -m piptools compile --upgrade --strip-extras              -o requirements.txt      pyproject.toml
	python3 -m piptools compile --upgrade --strip-extras --extra dev  -o requirements-dev.txt  pyproject.toml

assets:
	npm run build

docs:
	make --directory=docs clean
	make --directory=docs html
