# Fluidsimfoam solver for periodic hills (phill)

This [Fluidsimfoam] solver demonstrates how to write a solver for the simulation of the flow over periodic hills (phill).

## Install
You can install this solver using this command:

```sh
pip install fluidsimfoam-phill
```

## Run
After installing this solver you can use this script to run a phill case.
```sh
python3 doc/examples/scripts/tuto_phill.py
```
## Customized Run

The first step to run a simulation is to create a `params` object with default parameters:
```sh
from fluidsimfoam_phill import Simul

params = Simul.create_default_params()
```

## Modifying the parameters


Of course, the parameters can be modified. For instance, let's change the default 2D flow over 2D topography to a 3D flow over a 2D topography by just changing the number of elements in the z-direction in the blochMeshDict:

```sh
params.block_mesh_dict.lz = 0.5
params.block_mesh_dict.nz = 50
```

Or you can change the subdirectory:

```sh
params.output.sub_directory = "tests_fluidsimfoam/phill/"
```
We are able to change other parameters in the controlDict or some other files in order to run different simulations, for instance:
```sh
params.control_dict.end_time = 0.5
params.control_dict.delta_t = 0.01
params.control_dict.start_from = 'startTime'
params.turbulence_properties.simulation_type = "RAS"
```
After you assign or change all parameters you need, you could create the simulation object.

## Creation of the simulation object and directory

Now let’s create the simulation object (We usually use the name `sim`):
```sh
sim = Simul(params)
```
Information is given about the structure of the sim object (which has attributes sim.oper, sim.output and sim.make corresponding to different aspects of the simulation) and about the creation of some files. When you create this object, you have made a directory for your case that contains all necessary directories (`0`, `system`, `constant`) and files (`fvSolution`, `fvSchemes`, `blockMeshDict` and etc). This directory is accessible by using this command:

```sh
sim.path_run
```

Or you can easily see the list of contents of this directory:

```sh
ls {sim.path_run}
```
Something like this:
```sh
0/  constant/  info_solver.xml  params_simul.xml  system/  tasks.py
```

## Run Control

Now, you have the case ready to start the simulation. You can run this case by this command:

```sh
sim.make.exec("run")
```
Or if you want to clean this case even polyMesh:
```sh
sim.make.exec("clean")
```
If you want to see the run command list:

```sh
sim.make.list()
```

```sh
Available tasks:

  block-mesh
  clean
  funky-set-fields
  run
  sets-to-zones
  topo-set
```
If you want to use any of these commands like making blockMeshDict you can easily use this:
```sh
sim.make.exec("block-mesh")
```




For more details, see https://fluidsimfoam.readthedocs.io/en/latest/install.html

[fluidsimfoam]: https://foss.heptapod.net/fluiddyn/fluidsimfoam
