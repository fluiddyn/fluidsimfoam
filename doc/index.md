# Fluidsimfoam documentation

Fluidsimfoam is a Python package and a thin interface over [OpenFOAM]. It provides a
framework to (i) describe in Python sets of similar simulations, (ii) organize
parameters, (iii) launch/restart multiple simulations and (iv) load simulations to read
the associated parameters/data and produce nice figures/movies.

```{list-table}
* - Repository
  - <https://foss.heptapod.net/fluiddyn/fluidsimfoam>

* - Version
  - [{{ release}}](https://pypi.org/project/fluidsimfoam/)
```

```{toctree}
---
caption: User guide
maxdepth: 1
---
intro
install
tutorials
```

```{toctree}
---
caption: Python API
maxdepth: 1
---
autosum.rst
```

```{toctree}
---
caption: Help & Reference
maxdepth: 1
---
CHANGELOG
CONTRIBUTING
AUTHORS
dev/index.md
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`

[openfoam]: https://openfoam.org/
