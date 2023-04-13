# OpenFOAM Sidewall Convection Case

This repository contains the OpenFOAM necessary files to set up and run a Buoyancy-driven Cavity or (Sidewall Convection) that we call it `Cbox`.

## Requirements

To run this simulation, you will need:

- OpenFOAM
- ParaView (optional, for visualizing the results)
- Gnuplot (optional, for visualizing the results)

## Setup

Clone this repository to your computer:

https://foss.heptapod.net/fluiddyn/fluidsimfoam

You can use this command if you are using the Mercurial:

```
hg clone https://foss.heptapod.net/fluiddyn/fluidsimfoam
```

After clone the fluidsimfoam repository, go to fluidsimfoam directory and the `tests/pure_openfoam_cases/cbox` directory. You can use this command to go to the first case:

```
cd tests/pure_openfoam_cases/cbox/sim0/
```

Use this command to clean any case data:

```
foamCleanTutorials
```

In order to generate the mesh, you could use this command:

```
blockMesh
```

After generating the mesh you can run the simulation by just calling the model that is used here.

```
buoyantBoussinesqPimpleFoam
```


## Visualization

To visualize the result, you can use some packages like ParaView and Gnuplot. If you want to load data with ParaView, you could try this command:

```
paraFoam
```
