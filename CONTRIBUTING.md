# Contributing

## Installation for development

After installing [Poetry] (for example with something like `pip install poetry`), the
following commands should install and activate the virtual environment:

```sh
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
poetry install --all-extras
poetry shell
```

The `--all-extras` options installs more utilities for Fluidsimfoam developers.

## Version control

We use Mercurial and the development is hosted on
<https://foss.heptapod.net/fluiddyn/fluidsimfoam>. See
<https://fluiddyn.readthedocs.io/en/latest/advice_developers.html>

## Testing and coverage

We use pytest and ipdb (which are installed automatically by Poetry). The command
`make test` run the tests of the project. Here are some examples of other useful
commands:

```sh
pytest tests -x
alias pytest-ipdb=pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
pytest-ipdb -vv tests/test_constant_files.py::test_with_dict
```

To study the test coverage, one can run `make cov` or something like:

```sh
pytest tests doc/examples --cov --cov-report term --cov-report html
firefox htmlcov/index.html
```

## Formatting

We use Black and isort to format the Python code. One can run `make format` and
`make test` before committing.

## Documentation and tutorials

The [documentation](https://fluidsimfoam.readthedocs.io) is produced with Sphinx and
MyST. The source is in the `doc` directory and in the docstrings. The website is built
(for each push in the default branch) and hosted on ReadTheDocs.

To build the documentation locally:

```sh
cd doc
make
```

The tutorials are written in `.myst.md` files and executed during the build. `.ipynb`
files are never version controlled in the repository.

```{warning}

OpenFOAM (v1912) is installed on ReadTheDocs servers with the official Ubuntu
apt package. With this package no compilation for OpenFOAM simulation is
possible, so no `codeStream`. Fortunatelly, one can already do a lot of things
with Fluidsimfoam without compilation!

```

To write tutorials, one can modify the `.myst.md` files with your favorite editor or open
these files with JupyterLab: run `jupyter-lab` and then click right on the icon
representing the `.myst.md` file and click on `Open With > Notebook`. JupyterLab will
save the input of the notebook in the `.myst.md` file.

The source of the documentation should be formatted with `mdformat`. Running
`make format` from the `doc` directory should format all files.

[poetry]: https://python-poetry.org/docs/