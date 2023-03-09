---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Tutorials

```{admonition} Preliminary: introduction on OpenFOAM classical workflow

Let's recall that working with OpenFOAM involves:

- setting up a directory with different files defining a simulation, in
particular `system/controlDict`, `system/fsSolution`,
`constant/transportProperties` and files describing the initial conditions.

- running commands to create the mesh and launch the simulation.

To restart a simulation or create another simulation from a previous one, other
manual file manipulations are necessary.

Then, some output files can be analyzed and used to produce figures and movies.

Fluidsimfoam is a unified framework providing a Python API and shell commands to
help us for these different steps. These tutorials present how it works in
practice.

```

**Versions used in these tutorials:**

```{code-cell} ipython3
!fluidsimfoam-info
```

```{toctree}
---
maxdepth: 2
---
tuto_tgv.myst.md
```
