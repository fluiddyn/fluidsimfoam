# Contributing

The project is hosted on <https://foss.heptapod.net>. Don't look for a fork button
because it does not exist. To contribute, the first step is to open an issue on
[our bug tracker](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues) so that we
give you the needed rights on the repo.

## Installation for development

After installing [PDM] (for example with something like `pipx install pdm`, but
check [the other recommended install
methods](https://pdm-project.org/latest/#installation)), the following commands
should install and activate the virtual environment:

```sh
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
pdm install
pdm venv activate
```

```{admonition} Note on installing OpenFOAM on Ubuntu/Debian
---
class: dropdown
---
The official Ubuntu/Debian packages (installed with `sudo apt install
openfoam`) are quite broken but work better when the environment variable
`WM_PROJECT_DIR` is set to `/usr/share/openfoam`. If you can, use
<https://www.openfoam.com/news/main-news/openfoam-v2212>, which works much
better.

```

````{admonition} Note on activating OpenFOAM with Xonsh
---
class: dropdown
---
To activate OpenFOAM installed from
[openfoam.com](https://www.openfoam.com/news/main-news/openfoam-v2212), one
needs to run something like this horrible line:
```sh
source-bash /usr/lib/openfoam/openfoam2212/etc/bashrc -n --seterrprevcmd "" --suppress-skip-message
```

````

## Version control

We use Mercurial and the development is hosted on
<https://foss.heptapod.net/fluiddyn/fluidsimfoam>. See
<https://fluiddyn.readthedocs.io/en/latest/advice_developers.html>

## Testing and coverage

We use pytest and ipdb (which are installed automatically by pdm). The command
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

## Debugging

[ipdb](https://github.com/gotcha/ipdb) is quite convenient. Export the environment
variable `PYTHONBREAKPOINT` (for example add `export PYTHONBREAKPOINT=ipdb.set_trace` in
your `.bashrc`) and add `breakpoint()` somewhere in the code.

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

## Release

For now, we push on PyPI manually:

```sh
hg pull
hg up default
hg tag 0.0.7
hg push
rm -rf dist
python -m build
twine upload dist/*
```

[pdm]: https://pdm-project.org
