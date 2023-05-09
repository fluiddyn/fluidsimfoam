# Sidewall convection cases (cbox)

This directory contains the files necessary to set up and run simulations of the
flow in a buoyancy-driven rectangular cavity (sidewall convection in a "convective
box").

## Requirements

To run this simulation, you will need:

- OpenFOAM
- ParaView (optional, for visualizing the results)

## Setup and run the simulations

```sh
cd sim0
foamCleanTutorials
blockMesh
buoyantBoussinesqPimpleFoam
```

## Visualization

To load data with ParaView, run:

```sh
paraFoam
```
