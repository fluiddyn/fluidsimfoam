# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import runpy

import fluidsimfoam

project = "Fluidsimfoam"
copyright = "2023, Pierre Augier, Pooria Danaeifar"
author = "Pierre Augier, Pooria Danaeifar"
release = fluidsimfoam.__version__

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_inline_tabs",
    "IPython.sphinxext.ipython_console_highlighting",
    # "recommonmark",
    # "myst_parser",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

myst_substitutions = {"release": release}

nb_execution_mode = "cache"
nb_execution_excludepatterns = ["**/*.ipynb"]
nb_execution_raise_on_error = True
nb_execution_show_tb = True
nb_execution_timeout = 300
nb_merge_streams = True

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "examples/**/README.md",
    ".pytest_cache/*",
    "**/.pytest_cache/*",
    "*.ipynb",
    "posters/*/*.md",
]

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": None,
    ".md": "myst-nb",
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
# html_static_path = ["_static"]

# -- Options for Intersphinx -------------------------------------------------
intersphinx_mapping = runpy.run_path("ls_intersphinx_targets.py")[
    "intersphinx_mapping"
]

# -- Other options ------------------------------------------------------------
autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    #  'special-members': '__init__',
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "inherited-members": False,
}
autodoc_mock_imports = ["IPython"]

todo_include_todos = True

napoleon_numpy_docstring = True

# -- Custom functions --------------------------------------------------------


# def autodoc_skip_member(app, what, name, obj, skip, options):
#     # return True if (skip or exclude) else None
#     # Can interfere with subsequent skip functions.
#     if what == "function" and name == "load" and obj is fluidsimfoam.load:
#         return True


# def setup(app):
#     app.connect("autodoc-skip-member", autodoc_skip_member)
