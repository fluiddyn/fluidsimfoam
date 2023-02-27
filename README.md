# Fluidsimfoam

Python framework for [OpenFOAM]

Fluidsimfoam is a Python package which **will** allow one to write [Fluidsim]
solvers based for the simulations on the C++ CFD code [OpenFOAM]. There
**will** be open-source solvers (in particular fluidsimfoam-phill and
fluidsimfoam-tgv) and it **will** not be difficult to write your own solver
based on your [OpenFOAM] cases.

With a Fluidsimfoam solver, it **will** becomes very easy to

- launch/restart simulations with Python scripts and terminal commands,
- load simulations, read the associated parameters/data and produce nice figures/movies.

Fluidsimfoam can be seen as a workflow manager for [OpenFOAM] or a Python
wrapper around [OpenFOAM]. It uses [OpenFOAM] on the background and is thus NOT
a rewrite of [OpenFOAM]!

Fluidsimfoam is now in very early development. The goal is to get the
equivalent of [Snek5000], our Fluidsim framework for [Nek5000].

[fluidsim]: https://fluidsim.readthedocs.io
[openfoam]: https://openfoam.org/
[nek5000]: https://nek5000.mcs.anl.gov/
[snek5000]: https://snek5000.readthedocs.io
