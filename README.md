<div align="center">

# Fluidsimfoam

[![PyPI](https://img.shields.io/pypi/v/fluidsimfoam)](https://pypi.org/project/fluidsimfoam/)
[![Documentation Status](https://readthedocs.org/projects/fluidsimfoam/badge/?version=latest)](https://fluidsimfoam.readthedocs.io/en/latest/?badge=latest)

Python framework for [OpenFOAM]

</div>

<!-- badges -->

[OpenFOAM] is a very popular open-source C++ CFD framework. Working with [OpenFOAM]
implies writting and modifying a lot of input files describing a simulation.
The method described in the official [OpenFOAM] documentations is to copy an
existing simulation directory and to modify the input files by hand.
Fluidsimfoam is a Python package designed to improve the life of [OpenFOAM]
users.

Fluidsimfoam allows one to write [Fluidsim] solvers based for the simulations
on [OpenFOAM]. There are open-source solvers (in particular [fluidsimfoam-tgv],
[fluidsimfoam-cbox] and [fluidsimfoam-sed]) and it is not be difficult to write
your own solver based on your [OpenFOAM] cases.

With a Fluidsimfoam solver, it becomes very easy to

- launch/restart simulations with Python scripts and terminal commands,
- load simulations, read the associated parameters/data and produce nice figures/movies.

Fluidsimfoam can be seen as a workflow manager for [OpenFOAM] or a Python
wrapper around [OpenFOAM]. It uses [OpenFOAM] on the background and is thus NOT
a rewrite of [OpenFOAM]!

The best way to use Fluidsimfoam is to write or use a solver adapted for your
particular use case. However, one can also use Python objects provided by
Fluidsimfoam for some common tasks, like parsing/writting input files,
modifying field files, writting `blockMeshDict` files, etc.

Fluidsimfoam is now in quite early development. The goal is to get the
equivalent of [Snek5000], our Fluidsim framework for [Nek5000]. Looking at the
[Snek5000] tutorials should give a good idea of what Fluidsimfoam will soon
allow.

For our examples, we currently target OpenFOAM v2206 but it should be possible
to write Fluidsimfoam solvers targeting any recent OpenFOAM versions.

See more in [Fluidsimfoam documentation](https://fluidsimfoam.readthedocs.org).

## Install

Currently, it still makes sense to install Fluidsimfoam like we, the
fluidsimfoam developers, install it, i.e. in a dedicated controlled virtual
environment created by [Poetry]. After installing [Poetry] (for example with
something like `pip install poetry`), the following commands should install and
activate the virtual environment:

```sh
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
cd fluidsimfoam
poetry install
poetry shell
```

## Related projects

- [Fluidfoam] Another [Fluiddyn] package (like Fluidsimfoam) to use/plot OpenFOAM
  data. Will be used by Fluidsimfoam.

- [PyFoam] ([PyPI package](https://pypi.org/project/PyFoam/),
  [hg repo](http://hg.code.sf.net/p/openfoam-extend/PyFoam)) Python utilities for
  OpenFOAM. GNU GPL. Still maintained.

- [PythonFlu] ([wiki](https://openfoamwiki.net/index.php/Contrib_pythonFlu))

- [Swak4Foam] Popular set of utilities for OpenFOAM. Can be used in
  Fluidsimfoam solvers.

[PyFoam]: https://openfoamwiki.net/index.php/Contrib/PyFoam
[fluiddyn]: https://fluiddyn.readthedocs.io
[fluidsim]: https://fluidsim.readthedocs.io
[fluidfoam]: https://fluidfoam.readthedocs.io
[fluidsimfoam-tgv]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-tgv
[fluidsimfoam-cbox]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-cbox
[fluidsimfoam-sed]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-sed
[openfoam]: https://openfoam.org/
[nek5000]: https://nek5000.mcs.anl.gov/
[snek5000]: https://snek5000.readthedocs.io
[PythonFlu]: http://pythonflu.wikidot.com/
[Swak4Foam]: https://openfoamwiki.net/index.php/Contrib/swak4Foam
[Poetry]: https://python-poetry.org/docs/