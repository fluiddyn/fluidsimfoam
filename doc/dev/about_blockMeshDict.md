# blockMeshDict

We study blockMeshDict files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_blockmeshdict.py check
# or (faster)
python study_blockmeshdict.py
```

Here are the results:

```
nb_examples = 348
{'Empty file': 0, 'parser error': 2, 'wrong files': 0}

{
 'vertices': 346,
 'blocks': 346,
 'scale': 340,
 'boundary': 313,
 'edges': 292,
 'mergePatchPairs': 191,
 'patches': 33,
 'defaultPatch': 23,
 'ny': 18,
 'nz': 18,
 'nx': 14,
 'mergeType': 11,
 'y1': 11,
 'y2': 10,
 'transform': 9,
 'zmin': 9,
 'negY': 8,
 'posY': 8,
 'posYR': 8,
 'L': 8,
 'zmax': 8,
 'x1': 7,
 'x2': 7,
 'H': 7
}

FoamInfo classes:
{'dictionary': 346}

Fluidsimfoam issues (0.57 % of files): (saved in tmp_issues.txt)

```
