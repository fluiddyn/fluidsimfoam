# Periodic hills (phill) cases

This directory contains the files necessary to set up and run simulations of the
flow over periodic hills (phill) using OpenFOAM. There are two phill cases,
laminar and turbulent.

## Requirements

To run this simulation, you will need:

- OpenFOAM
- Coriofoam solver
- ParaView (optional, for visualizing the results)

## Setup and run

Install
[Coriofoam](https://gricad-gitlab.univ-grenoble-alpes.fr/coriofoam/coriofoam):

```sh
hg clone git@gricad-gitlab.univ-grenoble-alpes.fr:coriofoam/coriofoam.git
cd coriofoam
make
```

In one of the case directory (`sim_turb` or `sim_lam`), you can run:

```sh
foamCleanTutorials
blockMesh
topoSet
setsToZones
```

`funkySetFields` is used to modify the initial state funkySetFields take the file
`system/funkySetFieldsDict` as input and modify the directory 0:

```sh
funkySetFields -time 0
```

After generating the mesh you can run the simulation by just calling the model
that is used here.

```sh
coriofoam
```

## Visualization

To visualize the result, you can use some packages like ParaView and Gnuplot. If
you want to load data with ParaView, you could try this command:

```sh
paraFoam
```
