<div align="center">

# Fluidsimfoam

[![PyPI](https://img.shields.io/pypi/v/fluidsimfoam)](https://pypi.org/project/fluidsimfoam/)
[![Documentation Status](https://readthedocs.org/projects/fluidsimfoam/badge/?version=latest)](https://fluidsimfoam.readthedocs.io/en/latest/?badge=latest)

Python framework for [OpenFOAM]

</div>

<!-- start-intro -->

[OpenFOAM] is a very popular open-source C++ [CFD] framework. With
Fluidsimfoam, we try to **design and propose a new workflow for OpenFOAM
based on Python**. However, experienced OpenFOAM users won't be lost because
Fluidsimfoam produces in the end standard OpenFOAM cases and it's always
possible to come back to the standard OpenFOAM workflow.

Fluidsimfoam can be seen as a workflow manager for OpenFOAM or a Python
wrapper around OpenFOAM. It only uses OpenFOAM commands on the background
and is thus NOT a rewrite of OpenFOAM!

Fluidsimfoam should be especially useful for:

- automatisation of simulation launching for example for parametric studies or optimization,
- programmatic generation of complex and parametrized input files (for example `blockMeshDict`) and initial conditions,
- programmatic control of a simulation at runtime (an example
  [here](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/2023sed-parametric)).

However, Fluidsimfoam is not restricted to these usages and should be
convenient, especially for people knowing Python, for any OpenFOAM usages for
which C++ programming is not needed.

Working with OpenFOAM implies writting and modifying a lot of input files
describing a simulation. The method described in the official OpenFOAM
documentations is to copy an existing simulation directory and to modify the
input files by hand.

With Fluidsimfoam, we introduce the possibility to describe not only one case
(as shown in the [OpenFOAM tutorials]), but sets of similar simulations. The
description of one set of simulations is done in Python (and possibly with
[Jinja] templates) in a small Python package that we call a "[Fluidsim] solver".

```{warning}

"[Fluidsim] solver" and "OpenFOAM solvers" are very different things. A
Fluidsim solver is a small Python package describing a set of simulations.
Fluidsimfoam allows one to write Fluidsim solvers based for the simulations
on OpenFOAM.

```

As shown in [our tutorials], with a Fluidsimfoam solver, it becomes very easy to

- launch/restart simulations with Python scripts and terminal commands,
- load simulations, read the associated parameters/data and produce nice figures/movies.

There are open-source solvers (some of them [are included in our main
repository](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples))
and it is not be difficult to write your own solver based on your OpenFOAM
cases. For example, to produce a solver from an existing case, one can run

```sh
fluidsimfoam-initiate-solver cylinder -c $FOAM_TUTORIALS/basic/potentialFoam/cylinder
```

This command creates a solver `fluidsimfoam-cylinder` that can be used to run
the simulation described in the [Flow around a
cylinder](https://www.openfoam.com/documentation/tutorial-guide/2-incompressible-flow/2.2-flow-around-a-cylinder)
tutorial. But this solver can very easily be improved to be parametrized and to
produce some input files programmatically. For example, the mesh of this
tutorial is produced with the `blockMesh` OpenFOAM utility and the
`blockMeshDict` is quite complex and contains a `#codeStream` directive (which
implies writting C++ and compilations). With Fluidsimfoam, you can avoid this
step and produce the `blockMeshDict` programmatically with a nice Python API
and a nice mechanism to add and store parameters.

The best way to use Fluidsimfoam is to write or use a solver adapted for your
particular use case. However, one can also use Python functions and classes
provided by Fluidsimfoam for some common tasks, like parsing/writting input
files, modifying field files, writting `blockMeshDict` files, etc.

Fluidsimfoam is now usable but still in quite early development. There are
still very low hangling fruits not yet implemented (for example, [restart
utilities](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues/40),
[production of figures and
movies](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues/38), etc.) and
our documentation does not reflect what people can and will be able to do with
this tool. One goal is to get the equivalent of [Snek5000], our Fluidsim
framework for the [CFD] code [Nek5000]. Looking at the [Snek5000] tutorials
should give a good idea of what Fluidsimfoam will soon allow.

```{admonition} Contributing

This project is young and we need any kind of feedback and [contributions].
Don't be afraid that the project is not hosted on Github. If you think that
this project is interesting please *star* [our repository on
Heptapod](https://foss.heptapod.net/fluiddyn/fluidsimfoam) and/or [open
issues](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/issues) with
feedback, feature requests or bug reports. Moreover, we would be very happy to
welcome new core developers, so if you like OpenFOAM and Python, do not
hesitate!

```

For our examples, we currently target OpenFOAM v2206 but it should be possible
to write Fluidsimfoam solvers targeting any recent OpenFOAM versions.

[fluiddyn]: https://fluiddyn.readthedocs.io
[fluidsim]: https://fluidsim.readthedocs.io
[fluidfoam]: https://fluidfoam.readthedocs.io
[openfoam]: https://openfoam.org/
[OpenFOAM tutorials]: https://www.openfoam.com/documentation/tutorial-guide
[nek5000]: https://nek5000.mcs.anl.gov/
[snek5000]: https://snek5000.readthedocs.io
[Jinja]: https://jinja.palletsprojects.com
[contributions]: https://fluidsimfoam.readthedocs.io/en/latest/CONTRIBUTING.html
[our tutorials]: https://fluidsimfoam.readthedocs.io/en/latest/tutorials.html
[CFD]: https://en.wikipedia.org/wiki/Computational_fluid_dynamics

<!-- end-intro -->

See more in [Fluidsimfoam documentation](https://fluidsimfoam.readthedocs.org).

## Install

<!-- start-install -->

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

For better user experience with Matplotlib figures, you can also install with
`poetry install --extra qt`.

[Poetry]: https://python-poetry.org/docs/

<!-- end-install -->

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
[PythonFlu]: http://pythonflu.wikidot.com/
[Swak4Foam]: https://openfoamwiki.net/index.php/Contrib/swak4Foam
