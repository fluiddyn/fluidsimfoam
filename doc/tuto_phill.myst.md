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

+++ {"user_expressions": []}

# Flow over Periodic Hill (`fluidsimfoam-phill` solver)

Fluidsimfoam repository contains a
[simple example solver](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-phill)
for the flow over Periodic Hill. In a brief simulation, we'll demonstrate how it may be
utilized.

## Run simulations by executing scripts

There are three different geometeries available for this solver. We will run the
simulation by executing these three scripts:

- [doc/examples/scripts/tuto_phill_3d.py](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/tuto_phill_3d.py)
- [doc/examples/scripts/tuto_phill_2d.py](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/tuto_phill_2d.py)
- [doc/examples/scripts/tuto_phill_sinus.py](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/scripts/tuto_phill_sinus.py)

### 3D PHill

At first, we start with '3d_phill' geometery and its scripts which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill_3d.py
```

Generally, we would just execute this script with something like `python tuto_phill_3d.py`. In this case we added some options to this script:

* **-nx:** number of mesh grid in x direction
* **--end-time:** end time
* **-nsave:** number of outputs saving during run

```{code-cell} ipython3
command = "python3 examples/scripts/tuto_phill_3d.py -nx 20 --end-time 100 -nsave 5"
```

+++ {"user_expressions": []}

However, we require a little bit more code in this notebook. You may merely glance at the output of this cell since the way we execute this command is extremely peculiar to this tutorial provided as notebook.

```{code-cell} ipython3
---
jupyter:
  source_hidden: true
tags: [hide-input]
---
from subprocess import run, PIPE, STDOUT
from time import perf_counter

print("Running the script tuto_phill_3d.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = process.stdout.split("\n")
```

```{code-cell} ipython3
---
jupyter:
  source_hidden: true
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

+++ {"user_expressions": []}

We can now load the simulation and process the output.

<!-- #endregion -->

```{code-cell} ipython3
:tags: [hide-input]

from fluidsimfoam import load

sim = load(path_run)
```

```{code-cell} ipython3
field_u = sim.output.fields.read_field("T")
arr_u = field_u.get_array()
arr_u.shape
```

+++ {"user_expressions": []}

## Pyvista output

With the `sim` object, one can simply visualize the simulation with few methods in
`sim.output.fields`, see [here](https://fluidsimfoam.readthedocs.io/en/latest/tuto_tgv.myst.html#pyvista-output). Some theme configuration for this notebook:

```{code-cell} ipython3
---
jupyter:
  source_hidden: true
tags: [hide-input]
---
import pyvista as pv
pv.set_jupyter_backend("static")
pv.global_theme.anti_aliasing = 'ssaa'
pv.global_theme.background = 'white'
pv.global_theme.font.color = 'black'
pv.global_theme.font.label_size = 12
pv.global_theme.font.title_size = 16
pv.global_theme.colorbar_orientation = 'vertical'
```

+++ {"user_expressions": []}

First, we can see an overview of the mesh by `plot_mesh`.

```{code-cell} ipython3
sim.output.fields.plot_mesh(color="black");
```

+++ {"user_expressions": []}

The `plot_boundary` can help with mesh explanation or demonstration. All these plot methods return plotter object, we can get this object and modify some properties and then plot it. Note that set `show=False` in this situation!

```{code-cell} ipython3
plotter = sim.output.fields.plot_boundary("bottom", color="grey", mesh_opacity=0.2, show=False);
plotter.show_grid()
plotter.camera.zoom(0.9)
plotter.show()
```

+++ {"user_expressions": []}

One can quickly produce contour plots with `plot_contour`, for example, variable *U* in
plane *y=0* and *time=20s*:

```{code-cell} ipython3
sim.output.fields.plot_contour(
    equation="y=0",
    variable="U",
    mesh_opacity=0.1,
    time=20,
);
```

+++ {"user_expressions": []}

Same contour in *time=100s*:

```{code-cell} ipython3
sim.output.fields.plot_contour(
    equation="y=0",
    variable="U",
    mesh_opacity=0.1,
    time=100,
);
```

+++ {"user_expressions": []}

In order to plot other components of a vector, just assign *component* to desired one,
for example here we added `component=2` for plotting "Uz". In addition, to apply the
contour filter over the plot, just use `contour=True`. For different *colormap*, change
`cmap`, for more information about colormap see
[here](https://matplotlib.org/stable/tutorials/colors/colormaps.html).

```{code-cell} ipython3
plotter = sim.output.fields.plot_contour(
    equation="y=0",
    mesh_opacity=0.2,
    variable="U",
    component=2,
    cmap="plasma",
    show=False,
);
plotter.view_isometric()
plotter.camera.zoom(0.9)
plotter.show_grid()
plotter.show()
```

+++ {"user_expressions": []}

One can plot a variable over a straight line, by providing two points. By setting
`show_line_in_domain=True`, you may first view the line in the domain for simplicity and
to confirm its location.

```{code-cell} ipython3
sim.output.fields.plot_profile(
    point0=[0.5, 0.5, 2],
    point1=[0.5, 0.5, 20],
    variable="U",
    ylabel="$U$(m/s)",
    title="Velocity Profile",
    show_line_in_domain=True,
);
```

+++ {"user_expressions": []}

### 2D PHill

Now we are going to run '2d_phill' geometery simulation, which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill_2d.py
```

```{code-cell} ipython3
command = "python3 examples/scripts/tuto_phill_2d.py -nx 200"

from subprocess import run, PIPE, STDOUT
from time import perf_counter

print("Running the script tuto_phill_2d.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = process.stdout.split("\n")
```

```{code-cell} ipython3
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
```

```{code-cell} ipython3
from fluidsimfoam import load

sim = load(path_run)
```

+++ {"user_expressions": []}

Similar to *3d_phill*, in order to plot the outputs, we are using `sim.output.fields`. We start by plot overall mesh and try to zoom it.

```{code-cell} ipython3
plotter = sim.output.fields.plot_mesh(color="black", show=False);
plotter.camera.zoom(1.3)
plotter.show()
```

+++ {"user_expressions": []}

This is the contour plot of variable 'U' with axes:

```{code-cell} ipython3
pv.global_theme.colorbar_orientation = 'horizontal'
plotter = sim.output.fields.plot_contour("U", cmap="plasma", time=20, show=False)
plotter.camera.zoom(1.2)
plotter.show_grid()
plotter.show()
```

+++ {"user_expressions": []}

For plotting temperature profile in a vertical line located in 'x=3', 'z=0', we can define each point like this:

- x0=3, x1=3
- z0=0, z1=0

And for **y**, y0 <= ymin and y1 >= ymax

As a result, points can be like this: point0 = [3, 0, 0], point1 = [3, 10, 0]

```{code-cell} ipython3
sim.output.fields.plot_profile(
    point0=[3, 0, 0],
    point1=[3, 10, 0],
    variable="T",
    ylabel="$T$(K)",
    title="Temperature Profile",
    show_line_in_domain=False,
    show=True
);
```

+++ {"user_expressions": []}

### Sinusoidal PHill

And finally for 'sinus_phill' geometery simulation, which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill_2d.py
```

```{code-cell} ipython3
---
jupyter:
  source_hidden: true
---
command = "python3 examples/scripts/tuto_phill_sinus.py -nx 120 --end_time 200"
from subprocess import run, PIPE, STDOUT
from time import perf_counter

print("Running the script tuto_phill_sinus.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = process.stdout.split("\n")
```

```{code-cell} ipython3
---
jupyter:
  source_hidden: true
---
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
```

+++ {"user_expressions": []}

And for getting the `sim` object we can load the simulation:

```{code-cell} ipython3
from fluidsimfoam import load

sim = load(path_run)
```

+++ {"user_expressions": []}

Let's see the grid!

```{code-cell} ipython3
sim.output.fields.plot_mesh(color="black");
```

+++ {"user_expressions": []}

For plotting 'Uz' component of velocity at `time=200s`:

```{code-cell} ipython3
pv.global_theme.colorbar_orientation = 'vertical'
sim.output.fields.plot_contour("U", time=200, component=2);
```

+++ {"user_expressions": []}

Temperature profile:

```{code-cell} ipython3
sim.output.fields.plot_profile(
    point0=[1000, 0, 0],
    point1=[1000, 2000, 0],
    variable="T",
    ylabel="$T$(K)",
    title="Temperature Profile",
    show_line_in_domain=False,
);
```
