---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Breaking of a dam (`fluidsimfoam-dam` solver)

We created a solver `fluidsimfoam-dam` to reproduce the OpenFOAM tutorial
[Breaking of a dam](https://www.openfoam.com/documentation/tutorial-guide/4-multiphase-flow/4.1-breaking-of-a-dam).

```{code-cell} ipython3
from fluidsimfoam_dam import Simul
```

To run a sequential simulation:

```{code-cell} ipython3
params = Simul.create_default_params()
params.output.sub_directory = "doc_fluidsimfoam/dam"
params.control_dict.end_time = 1.0
sim = Simul(params)
```

```{code-cell} ipython3
sim.make.exec("polymesh")
```

```{code-cell} ipython3
sim.make.exec("run")
```

```{code-cell} ipython3
import pyvista
pyvista.set_jupyter_backend("static")

pyvista.global_theme.anti_aliasing = 'ssaa'
pyvista.global_theme.background = 'white'
pyvista.global_theme.font.color = 'black'
pyvista.global_theme.font.label_size = 12
pyvista.global_theme.font.title_size = 16
pyvista.global_theme.colorbar_orientation = 'vertical'
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=0.1);
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=0.4);
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=1);
```

To run the same simulation but in parallel:

```{code-cell} ipython3
params = Simul.create_default_params()
params.output.sub_directory = "doc_fluidsimfoam/dam"
params.control_dict.end_time = 1.0

params.parallel.method = "simple"
params.parallel.nsubdoms = 4
params.parallel.nsubdoms_xyz = [2, 2, 1]

sim = Simul(params)
```

```{code-cell} ipython3
sim.make.exec("run")
```

One can also try with a higher dam:

```{code-cell} ipython3
params.parallel.nsubdoms = 1

params.block_mesh_dict.height_dam *= 2
sim = Simul(params)
```

```{code-cell} ipython3
sim.make.exec("run")
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=0.1);
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=0.4);
```

```{code-cell} ipython3
sim.output.fields.plot_contour("alpha.water", time=1);
```
