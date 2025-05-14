#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Thomas Breitner
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys
import django
from django.conf import settings


sys.path.insert(0, os.path.abspath(".."))

# # Add node_modules/.bin path to path. Only used for mermaid cli atm.
# node_bin_path = os.path.abspath('../node_modules/.bin')
# sys.path.append(node_bin_path)

# A minimal .env with production settings is created for gitlab pages
# see .gitlab.ci.yml
os.environ["DJANGO_SETTINGS_MODULE"] = "rdml.settings.base"
django.setup()


# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    # 'sphinx.ext.autosectionlabel',  # sphinx WARNING: duplicate label foo other instance in bar
    "myst_parser",
    "sphinx_design",
    # 'linkify',
]

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 1

templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "RDML"
copyright = "2025, Thomas Breitner"
author = "Thomas Breitner"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# version = '1.0'

# The full version, including alpha/beta/rc tags.
# release = '0'

language = "en"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# html_css_files = [
#     "css/custom.css",
# ]

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]


html_theme_options = {
    "repository_url": "https://gitlab.gwdg.de/t.breitner/rdml",
    "use_repository_button": True,
    "show_toc_level": 3,
    "navigation_with_keys": True,
    "extra_footer": '<p>Questions? <a href="mailto:t.breitner@csl.mpg.de">📧 Thomas Breitner</a></p>',
}

html_title = "RDML Docs"
# html_logo = "path/to/logo.png"
# html_favicon = "path/to/favicon.ico"

base_url = getattr(settings, "RDML_BASE_URL")

_ip_ranges_allowed = getattr(settings, "RDML_EDIT_ALLOWED_IP_RANGES")
print(f"IP ranges allowed: {_ip_ranges_allowed}")
_ip_ranges_allowed_all = _ip_ranges_allowed == ["*"]

if _ip_ranges_allowed_all:
    ip_ranges_allowed = "All granted"
elif _ip_ranges_allowed:
    ip_ranges_allowed = ", ".join(_ip_ranges_allowed)

myst_substitutions = {
    "base_url": base_url,
    "ip_ranges_allowed": ip_ranges_allowed,
}


# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr', 'zh'
#
# html_search_language = 'en'


myst_enable_extensions = ["colon_fence", "substitution", "attrs_inline", "html_image"]
myst_heading_anchors = 6
