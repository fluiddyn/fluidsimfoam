# OpenFOAM Input Files in Tutorials

OpenFOAM input files are typically text files that contain configuration and setup
parameters for various OpenFOAM utilities and solvers. These input files are organized
into a directory structure that corresponds to the simulation case being run. The input
files for a tutorial can usually be found in the tutorial's directory, under
subdirectories named system, constant, and 0.

The system directory typically contains files that define the numerical schemes and
solvers used by the solver, as well as the simulation control parameters, such as:
fvSolution, fvSchemes, controlDict and blockMeshDict. The constant directory typically
contains files that define the physical properties of the fluid being simulated, such as
its density and viscosity related to laminar and turbulent cases. Finally, the 0
directory typically contains files that define the initial conditions for the
simulation, such as the initial velocity and pressure fields.

## Results

The following information is the result of a python script which looped over OpenFOAM
tutorials (version: 2112):

```
nb_examples = 445
{'system/fvSolution': 437,
 'system/controlDict': 436,
 'system/fvSchemes': 434,
 'system/blockMeshDict': 349,
 'constant/turbulenceProperties': 317,
 '0.orig/U': 275,
 'system/decomposeParDict': 272,
 'constant/transportProperties': 256,
 'constant/g': 225,
 '0.orig/p': 221,
 '0.orig/p_rgh': 167,
 '0.orig/nut': 157,
 '0.orig/k': 143,
 'system/setFieldsDict': 131,
 '0.orig/T': 118,
 'constant/thermophysicalProperties': 116,
 '0.orig/epsilon': 101,
 'constant/dynamicMeshDict': 99,
 'system/topoSetDict': 91,
 '0.orig/alpha.water': 84,
 '0.orig/alphat': 66,
 '0/p': 60,
 '0/U': 54,
 'constant/combustionProperties': 44,
 'system/snappyHexMeshDict': 42,
 'constant/chemistryProperties': 38,
 'constant/phaseProperties': 37,
 '0.orig/nuTilda': 36,
 '0.orig/omega': 35,
 'constant/radiationProperties': 34,
 'constant/adjointRASProperties': 34,
 'system/optimisationDict': 34,
 '0.orig/pointDisplacement': 33,
 'constant/fvOptions': 33,
 '0/T': 31,
 'system/createPatchDict': 31,
 '0.orig/pa': 31,
 '0.orig/Ua': 30,
 'constant/thermophysicalProperties.air': 30,
 'constant/turbulenceProperties.air': 28,
 'system/surfaceFeatureExtractDict': 27,
 'system/meshQualityDict': 26,
 '0/nut': 26,
 '0.orig/alpha.air': 26,
 '0/k': 25,
 'system/blockMeshDict.m4': 25,
 'constant/thermophysicalProperties.water': 25,
 '0.orig/N2': 24,
 '0.orig/O2': 24,
 'constant/reactingCloud1Properties': 24,
 '0.orig/U.air': 24,
 'constant/reactions': 23,
 '0.orig/T.air': 21,
 '0/epsilon': 20,
 '0.orig/U.water': 20,
 '0.orig/zoneID': 19,
 '0.orig/alpha.liquid': 19,
 'constant/regionProperties': 18,
 '0.orig/H2O': 18,
 '0.orig/T.water': 18,
 'constant/thermophysicalProperties.liquid': 18,
 '0.orig/include/initialConditions': 17,
 '0/alphat': 16,
 '0.orig/nuaTilda': 16,
 'constant/thermophysicalProperties.gas': 16,
 'constant/waveProperties': 16,
 'constant/turbulenceProperties.water': 16,
 'constant/kinematicCloudProperties': 15,
 '0.orig/Ydefault': 15,
 '0.orig/alpha.gas': 15,
 '0.orig/Theta': 15,
 'constant/thermo.compressibleGas': 14,
 '0.orig/G': 14,
 'system/faSchemes': 14,
 'system/faSolution': 14,
 'constant/boundaryRadiationProperties': 13,
 'system/faMeshDefinition': 13,
 'system/fvOptions': 12,
 'constant/surfaceFilmProperties': 11,
 'system/extrudeMeshDict': 11,
 '0.orig/include/fixedInlet': 10,
 'system/createBafflesDict': 10,
 '0/nuTilda': 10,
 '0.orig/k.air': 10,
 '0.orig/nut.air': 10,
 'constant/turbulenceProperties.liquid': 10,
 '0.orig/alpha.mercury': 10,
 '0.orig/alpha.oil': 10,
 'constant/leftSolid/radiationProperties': 9,
 'constant/leftSolid/thermophysicalProperties': 9,
 'system/leftSolid/fvSchemes': 9,
 'system/leftSolid/fvSolution': 9,
 'system/changeDictionaryDict': 9,
 'system/extrudeToRegionMeshDict': 9,
 'system/refineMeshDict': 9,
 '0.orig/CH4': 9,
 'constant/MRFProperties': 9,
 '0/p_rgh': 9,
 'constant/foam.dat': 9,
 'constant/foam.inp': 9,
 'constant/thermo.incompressiblePoly': 9,
 'system/setAlphaFieldDict': 9,
 'constant/turbulenceProperties.gas': 9,
 '0.orig/epsilon.air': 9,
 'system/leftSolid/changeDictionaryDict': 8,
 'chemkin/transportProperties': 8,
 'validation/plot': 8,
 '0.orig/IDefault': 8,
 'constant/hRef': 8,
 'constant/rightSolid/radiationProperties': 8,
 'constant/rightSolid/thermophysicalProperties': 8,
 'constant/topAir/radiationProperties': 8,
 'constant/topAir/turbulenceProperties': 8,
 'constant/topAir/thermophysicalProperties': 8,
 'system/leftSolid/decomposeParDict': 8,
 'system/rightSolid/decomposeParDict': 8,
 'system/rightSolid/fvSchemes': 8,
 'system/rightSolid/fvSolution': 8,
 'system/topAir/decomposeParDict': 8,
 'system/topAir/fvSchemes': 8,
 'system/topAir/fvSolution': 8,
 '0.orig/T.gas': 8,
 '0.orig/T.liquid': 8,
 '0.orig/U.gas': 8,
 '0.orig/U.liquid': 8,
 'constant/kinematicCloudPositions': 7,
 '0/H2O': 7,
 '0/N2': 7,
 '0/O2': 7,
 'system/sample': 7,
 'system/sampling': 7,
 'constant/heater/radiationProperties': 7,
 'constant/heater/thermophysicalProperties': 7,
 'system/heater/changeDictionaryDict': 7,
 'system/heater/decomposeParDict': 7,
 'system/heater/fvSchemes': 7,
 'system/heater/fvSolution': 7,
 'system/rightSolid/changeDictionaryDict': 7,
 'system/topAir/changeDictionaryDict': 7,
 '0.orig/alphat.air': 7,
 'chemkin/chem.inp': 6,
 'chemkin/therm.dat': 6,
 'constant/additionalControls': 6,
 'constant/pyrolysisZones': 6,
 'constant/reactionsGRI': 6,
 'constant/thermo.compressibleGasGRI': 6,
 '0/CH4': 6,
 '0/CO2': 6,
 '0/Ydefault': 6,
 'system/cuttingPlane': 6,
 'system/vtkWrite': 6,
 '0.orig/rho': 6,
 'plot': 6,
 '0/U.air': 6,
 'constant/parcelInjectionProperties': 6,
 'system/topoSetDict.1': 6,
 'system/topoSetDict.2': 6,
 '0.orig/air.gas': 6,
 '0.orig/alphat.gas': 6,
 '0.orig/epsilon.gas': 6,
 '0.orig/k.gas': 6,
 '0.orig/nut.gas': 6,
 '0.orig/nut.water': 6,
 '0.orig/qPlant': 6,
 '0.orig/include/frontBackUpperPatches': 5,
 'chemkin/senk.inp': 5,
 'chemkin/senk.out': 5,
 'constant/initialConditions': 5,
 '0/omega': 5,
 '0.orig/solid/T': 5,
 '0.orig/solid/p': 5,
 'constant/solid/thermophysicalProperties': 5,
 'system/solid/decomposeParDict': 5,
 'system/solid/fvSchemes': 5,
 'system/solid/fvSolution': 5,
 'system/bottomAir/fvSchemes': 5,
 'system/bottomAir/fvSolution': 5,
 '0/Ua': 5,
 '0/pa': 5,
 'system/mapFieldsDict': 5,
 'system/streamLines': 5,
 '0.orig/air': 5,
 'system/topoSetDict.3': 5,
 '0.orig/alphat.liquid': 5,
 '0.orig/epsilon.liquid': 5,
 '0.orig/k.liquid': 5,
 '0.orig/nut.liquid': 5,
 '0.orig/alphat.water': 5,
 '0.orig/epsilon.water': 5,
 '0.orig/k.water': 5}
```