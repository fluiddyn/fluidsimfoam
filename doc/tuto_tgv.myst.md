---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"user_expressions": []}

# Demo Taylor-Green vortex (`fluidsimfoam-tgv` solver)

Fluidsimfoam repository contains a
[simple example solver](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-tgv)
for the Taylor-Green vortex flow. We are going to show how it can be used on a very small
and short simulation.

## Run a simulation by executing a script

We will run the simulation by executing the script
[doc/examples/scripts/tuto_tgv.py](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/tuto_tgv.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_tgv.py
```

In normal life, we would just execute this script with something like
`python tuto_tgv.py`.

```{code-cell} ipython3
command = "python3 examples/scripts/tuto_tgv.py"
```

+++ {"user_expressions": []}

However, in this notebook, we need a bit more code. How we execute this command is very
specific to these tutorials written as notebooks so you can just look at the output of
this cell.

```{code-cell} ipython3
---
tags: [hide-input]
---
from subprocess import run, PIPE, STDOUT
from time import perf_counter

print("Running the script tuto_tgv.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = process.stdout.split("\n")
```

+++ {"user_expressions": []}

To "load the simulation", i.e. to recreate a simulation object, we now need to extract
from the output the path of the directory of the simulation. This is also very specific
to these tutorials, so you don't need to focus on this code. In real life, we can just
read the log to know where the data has been saved.

```{code-cell} ipython3
---
tags: [hide-input]
---
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
```

```{code-cell} ipython3
path_run
```

```{code-cell} ipython3
!ls {path_run}
```

+++ {"user_expressions": []}

## Load the simulation

We can now load the simulation and process the output.

<!-- #endregion -->

```{code-cell} ipython3
from fluidsimfoam import load

sim = load(path_run)
```

+++ {"user_expressions": []}

```{admonition} Quickly start IPython and load a simulation
The command `fluidsimfoam-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

+++ {"user_expressions": []}

One can do many things with this `Simul` object. For example, a Numpy array corresponding
to the last saved time can be created with:

```{code-cell} ipython3
field_u = sim.output.fields.read_field("U")
arr_u = field_u.get_array()
arr_u.shape
```

```{code-cell} ipython3
x, y, z = sim.oper.get_cells_coords()
```

Data saved in the OpenFOAM log file can be loaded and plotted with the object
`sim.output.log`, an instance of the class {class}`fluidsimfoam.output.log.Log`:

```{code-cell} ipython3
sim.output.log.plot_residuals(tmin=0.03);
```

To know how long should run a simulation, one can use:

```{code-cell} ipython3
sim.output.log.plot_clock_times()
```

## Pyvista output

With the `sim` object, one can simply visualize the simulation with few methods in
`sim.output.fields`:

- {func}`fluidsimfoam.output.fields.Fields.plot_mesh`
- {func}`fluidsimfoam.output.fields.Fields.plot_boundary`
- {func}`fluidsimfoam.output.fields.Fields.plot_profile`
- {func}`fluidsimfoam.output.fields.Fields.plot_contour`

Let's now try them. For this tutorial which has to be rendered statically on our web
documentation, we use a static backend. For interactive figures, use instead the `trame`
backend.

```{code-cell} ipython3
import pyvista as pv
pv.set_jupyter_backend("static")
pv.global_theme.anti_aliasing = 'ssaa'
pv.global_theme.background = 'white'
pv.global_theme.font.color = 'black'
pv.global_theme.font.label_size = 12
pv.global_theme.font.title_size = 16
pv.global_theme.colorbar_orientation = 'vertical'
```

First, we can see an overview of the mesh.

```{code-cell} ipython3
sim.output.fields.plot_mesh(color="black")
```

One can see the boundries via this command:

```{code-cell} ipython3
sim.output.fields.plot_boundary("leftBoundary", color="red")
```

One can quickly produce contour plots with `plot_contour`, for example, variable `U` in
plane with equation `z=4`:

```{code-cell} ipython3
sim.output.fields.plot_contour(
        equation="z=4",
        variable="U",        
    )
```

In order to plot other components of a vector, just assign `component` to desired one,
for example here we added `component=2` for plotting `Uz`. In addition, to apply the
contour filter over the plot, just use `contour=True`.

```{code-cell} ipython3
sim.output.fields.plot_contour(
        equation="z=5",
        mesh_opacity=0.07,
        variable="U",
        contour=True,
        component=2,
        cmap="plasma",
    )
```

You can get variable names via this command:

```{code-cell} ipython3
sim.output.name_variables
```

We ploted `U` before, now we can plot `p` in another plane (x=2.3):

```{code-cell} ipython3
sim.output.fields.plot_contour(
        equation="x=2.3",
        variable="p",
        cmap="plasma",
    )
```

One can plot a variable over a straight line, by providing two points. For simplicity and
making sure about where is line located, you can first see the line in the domain by
setting `show_line_in_domain=True`.

```{code-cell} ipython3
sim.output.fields.plot_profile(
    point0=[1, 1, 0],
    point1=[1, 1, 7],
    variable="U",
    ylabel="$U(m/s)$",
    title="Velocity",
    show_line_in_domain=True,
)
```
