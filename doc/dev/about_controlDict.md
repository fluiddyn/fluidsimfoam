# controlDict

We study controlDict files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_controldict.py check
# or (faster)
python study_controldict.py
```

Here are the results:

```
nb_examples = 358
{'Empty file': 0, 'parser error': 13, 'wrong files': 0}

{
 'vertices': 345,
 'blocks': 345,
 'scale': 339,
 'boundary': 310,
 'edges': 287,
 'mergePatchPairs': 194,
 'patches': 35,
 'nx': 20,
 'ny': 20,
 'nz': 20,
 'defaultPatch': 14,
 'zMax': 12,
 'zMin': 12,
 'mergeType': 11,
 'y1': 11,
 'xMin': 11,
 'xMax': 11,
 'yMin': 11,
 'yMax': 11,
 'y2': 10,
 'alpha': 10,
 'yExpansion': 10,
 'sin0': 10,
 'cos0': 10,
 'xMindx': 10,
 'xMaxdx': 10,
 'yMaxdy': 10,
 'L': 9,
 'negY': 8,
 'posY': 8,
 'posYR': 8,
 'H': 8,
 'x1': 7,
 'x2': 7
 }

FoamInfo classes:
{'dictionary': 345}

```
