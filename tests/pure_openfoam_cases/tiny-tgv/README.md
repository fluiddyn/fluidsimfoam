# OpenFOAM Taylor-Green Vortex Case

This repository contains the necessary files to set up and run a Taylor-Green vortex simulation using OpenFOAM.

## Requirements

To run this simulation, you will need:

- OpenFOAM
- ParaView (optional, for visualizing the results)
- Gnuplot (optional, for visualizing the results)

## Setup

Clone this repository to your computer:
    
https://foss.heptapod.net/fluiddyn/fluidsimfoam
    
Go to `tests/pure_openfoam_cases/tiny-tgv` directory. You can use this command:

`cd tests/pure_openfoam_cases/tiny-tgv/`
    
Use this command to clean any case data:

`foamCleanTutorials`
    
In order to generate mesh, you could use this command:

`blockMesh`
    
After generating the mesh you can run the simulation by just calling the model that used here.

`icoFoam`
    
    
## Visualization

To visualize the result, you can use some packages like ParaView and Gnuplot. If you want to load data with ParaView, you could try this command:

`paraFoam`
