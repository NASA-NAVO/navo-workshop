# Configuration file for the Sphinx documentation builder.
#
# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'NASA-NAVO Workshop Notebooks'
copyright = '2018-2024, NASA-NAVO developers'
author = 'NASA-NAVO developers'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_nb',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'notes', '.tox', '.tmp', '.pytest_cache', 'README.md']

# MyST-NB configuration
nb_execution_timeout = 900
nb_scroll_outputs = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'
html_title = 'NASA-NAVO Workshops Notebooks'
#html_logo = '_static/navo_logo.gif'
#html_favicon = '_static/favicon.ico'
html_theme_options = {
    "github_url": "https://github.com/NASA-NAVO/navo-workshop",
    "repository_url": "https://github.com/NASA-NAVO/navo-workshop",
    "repository_branch": "main",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",

    },
    "home_page_in_toc": True,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# myst configurations
myst_heading_anchors = 4

nb_execution_excludepatterns = []

# Excluding knowingly broken notebook until
# https://github.com/NASA-NAVO/navo-workshop/issues/197 is fixed
nb_execution_excludepatterns += ['hr_diagram_solution.md',]
