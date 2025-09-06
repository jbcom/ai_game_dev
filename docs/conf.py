"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
from pathlib import Path

# Add the source directory to the Python path
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
project = 'AI Game Development'
copyright = '2025, AI Game Dev Team'
author = 'AI Game Dev Team'
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'autodoc2',                     # Modern auto-generation from static analysis
    'sphinx.ext.doctest',           # Test code examples in docs
    'sphinx.ext.intersphinx',       # Link to other projects' docs
    'sphinx.ext.todo',              # Support for todos
    'sphinx.ext.coverage',          # Coverage of documentation
    'sphinx.ext.mathjax',           # Math support
    'sphinx.ext.ifconfig',          # Conditional inclusion of content
    'sphinx.ext.viewcode',          # Links to highlighted source code
    'sphinx.ext.githubpages',       # Publish to GitHub Pages
    'myst_parser',                  # MyST Markdown parser
]

# Autodoc2 settings for automatic API documentation
autodoc2_packages = [
    {
        "path": "../src/ai_game_dev",
        "exclude_files": [
            "__pycache__",
            "*.pyc",
            "tests",
        ],
    },
]

# Autodoc2 configuration
autodoc2_render_plugin = "myst"
autodoc2_output_dir = "api"
autodoc2_index_template = None
autodoc2_sort_names = True
autodoc2_class_docstring = "merge"
autodoc2_module_all_regexes = [
    r".*", 
]
autodoc2_skip_module_regexes = [
    r".*\.tests.*",
    r".*\.test_.*",
]

# Support for both RST and MyST docstrings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# The master toctree document.
master_doc = 'index'

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',
    
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    
    # Additional stuff for the LaTeX preamble.
    'preamble': '',
    
    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'ai-game-dev.tex', 'AI Game Development Documentation',
     'AI Game Dev Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'ai-game-dev', 'AI Game Development Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'ai-game-dev', 'AI Game Development Documentation',
     author, 'ai-game-dev', 'Revolutionary AI-powered game development library.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'langchain': ('https://python.langchain.com/docs', None),
    'pydantic': ('https://docs.pydantic.dev/latest', None),
    'pygame': ('https://www.pygame.org/docs', None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Options for coverage extension ------------------------------------------
coverage_show_missing_items = True

# Source file encoding
source_encoding = 'utf-8-sig'

# Default language for syntax highlighting
highlight_language = 'python'

# Maximum depth for table of contents
toctree_maxdepth = 3

# Show "Edit on GitHub" links
html_context = {
    "display_github": True,
    "github_user": "ai-game-dev",
    "github_repo": "ai-game-dev",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Custom sidebar templates
html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
        'localtoc.html',
    ]
}