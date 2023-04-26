# blockMeshDict

We study blockMeshDict files in OpenFOAM tutorials. The results can be obtained by
running

```sh
cd dev/study_OF_examples
./study_1_filename.py blockMeshDict check
# or (faster)
./study_1_filename.py blockMeshDict

```

Here are the results:

```
nb_examples = 348
{'Empty file': 0, 'parser error': 0, 'wrong files': 0}

{
 'vertices': 348,
 'blocks': 346,
 'scale': 342,
 'boundary': 313,
 'edges': 292,
 'mergePatchPairs': 191,
 'patches': 33,
 'defaultPatch': 23,
 'nz': 20,
 'ny': 18,
 'y1': 15,
 'nx': 14,
 'mergeType': 11,
 'x1': 11,
 'zmin': 11,
 'y2': 10,
 'zmax': 10,
 'transform': 9,
 'x0': 9,
 'negY': 8,
 'posY': 8,
 'posYR': 8,
 'L': 8,
 'y0': 8,
 'x2': 7,
 'H': 7
}

FoamInfo classes:
{'dictionary': 348}

No parser issue for blockMeshDict!

```
