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

# Demo Taylor-Green vortex (`fluidsimfoam-tgv` solver)

Fluidsimfoam repository contains a [simple example
solver](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-tgv)
for the Taylor-Green vortex flow. We are going to show how it can be used on a
very small and short simulation.

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

## Load the simulation

We can now load the simulation and process the output.

<!-- #endregion -->

```{code-cell} ipython3
from fluidsimfoam import load

sim = load(path_run)
```

```{admonition} Quickly start IPython and load a simulation
The command `fluidsimfoam-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

```{code-cell} ipython3
field_u = sim.output.fields.read_field("U")
arr_u = field_u.get_array()
arr_u.shape
```

```{code-cell} ipython3
sim.output.log.plot_residuals(tmin=0.03);
```

```{code-cell} ipython3
sim.output.log.plot_clock_times()
```
