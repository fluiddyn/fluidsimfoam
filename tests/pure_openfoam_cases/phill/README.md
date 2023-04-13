# OpenFOAM Periodic Hills (Phill) Case

This repository contains the necessary files to set up and run a flow over Periodic Hills (Phill) using OpenFOAM. For now there are two phill cases, laminar and turbulent cases.

## Requirements

To run this simulation, you will need:

- OpenFOAM
- ParaView (optional, for visualizing the results)
- Gnuplot (optional, for visualizing the results)
- coriofoam solver

## Setup

Clone this repository to your computer:

https://foss.heptapod.net/fluiddyn/fluidsimfoam

You can use this command if you are using the Mercurial:

```
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
```

For installing the coriofoam you see [here](https://gricad-gitlab.univ-grenoble-alpes.fr/coriofoam/coriofoam), or just follow this procedure, clone the repository:
```
hg clone git@gricad-gitlab.univ-grenoble-alpes.fr:coriofoam/coriofoam.git
```
In order to install the solver, you can go to the `coriofoam` directory and install it:
```
cd coriofoam
make
```
After installing the coriofoam solver, go to fluidsimfoam directory and the `tests/pure_openfoam_cases/phill` directory. You can use this command to go to the turbulent case:

```
cd tests/pure_openfoam_cases/phill/sim_turb/
```
Or this for laminar case:
```
cd tests/pure_openfoam_cases/phill/sim_lam/
```
Use this command to clean any case data:

```
foamCleanTutorials
```

In order to generate mesh and setup the topology, you could use these commands:

```
blockMesh
topoSet
setsToZones
```
The funkySetFields is used to modify the initial state funkySetFields take the file `system/funkySetFieldsDict` as input and modify the directory 0:
```
funkySetFields -time 0
```

After generating the mesh you can run the simulation by just calling the model that is used here.

```
coriofoam
```


## Visualization

To visualize the result, you can use some packages like ParaView and Gnuplot. If you want to load data with ParaView, you could try this command:

```
paraFoam
```
