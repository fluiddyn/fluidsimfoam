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
{'Empty file': 0, 'parser error': 6, 'wrong files': 0}

{
 'vertices': 342,
 'blocks': 342,
 'scale': 336,
 'boundary': 309,
 'edges': 288,
 'mergePatchPairs': 187,
 'patches': 33,
 'defaultPatch': 19,
 'nx': 14,
 'ny': 14,
 'nz': 14,
 'mergeType': 11,
 'y1': 11,
 'y2': 10,
 'transform': 9,
 'negY': 8,
 'posY': 8,
 'posYR': 8,
 'L': 8,
 'x1': 7,
 'x2': 7,
 'H': 7
 }

FoamInfo classes:
{'dictionary': 342}

```
