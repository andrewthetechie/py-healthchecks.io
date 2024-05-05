"""Sphinx configuration."""

from datetime import datetime


project = "Py Healthchecks.Io"
author = "Andrew Herrington"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
autodoc_typehints = "description"
html_theme = "furo"
