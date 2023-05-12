# Contributing

## Installation for development

After installing [Poetry] (for example with something like `pip install
poetry`), the following commands should install and activate the virtual
environment:

```sh
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
poetry install
poetry shell
```

For better user experience with Matplotlib figures, you can also install with
`poetry install --extra qt`.

[Poetry]: https://python-poetry.org/docs/

## Version control

We use Mercurial and the development is hosted on
https://foss.heptapod.net/fluiddyn/fluidsimfoam. See
https://fluiddyn.readthedocs.io/en/latest/advice_developers.html

## Testing and coverage

We use pytest and ipdb (which are installed automatically by Poetry). The
command `make test` run the tests of the project. Here are some examples of
other useful commands:

```sh
pytest tests -x
alias pytest-ipdb=pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
pytest-ipdb -vv tests/test_constant_files.py::test_with_dict
```

To study the test coverage, one can run something like that:

```sh
pytest tests doc/examples -vv --cov --cov-report term --cov-report html
firefox htmlcov/index.html
```

## Formatting

We use Black and isort to format the Python code. One can run `make format` and
`make test` before committing.
