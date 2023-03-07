# Fluidsimfoam

<!-- badges -->

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

## Related projects

- [PyFoam] ([PyPI package](https://pypi.org/project/PyFoam/),
  [hg repo](http://hg.code.sf.net/p/openfoam-extend/PyFoam)) Python utilities for
  OpenFOAM. GNU GPL. Still maintained. Should be used by Fluidsimfoam.

- [Fluidfoam] Another Fluiddyn package (like Fluidsimfoam) to use/plot OpenFOAM
  data. Will be used by Fluidsimfoam.

- [PythonFlu] ([wiki](https://openfoamwiki.net/index.php/Contrib_pythonFlu))

- [Swak4Foam]

[PyFoam]: https://openfoamwiki.net/index.php/Contrib/PyFoam
[fluidsim]: https://fluidsim.readthedocs.io
[fluidfoam]: https://fluidfoam.readthedocs.io
[openfoam]: https://openfoam.org/
[nek5000]: https://nek5000.mcs.anl.gov/
[snek5000]: https://snek5000.readthedocs.io
[PythonFlu]: http://pythonflu.wikidot.com/
[Swak4Foam]: https://openfoamwiki.net/index.php/Contrib/swak4Foam
