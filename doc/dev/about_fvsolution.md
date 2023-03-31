# fvSolution

We study fvSolution files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_fvsolution.py check
# or (faster)
python study_fvsolution.py
```

Here are the results:

```
nb_examples = 541
Fluidsimfoam issues: (saved in tmp_issues.txt)

{'Empty file': 9, 'parser error': 0, 'wrong files': 1}
{'solvers': 515,
 'relaxationFactors': 325,
 'PIMPLE': 316,
 'SIMPLE': 166,
 'cache': 37,
 'PISO': 27,
 'potentialFlow': 22,
 'nNonOrthCorr': 2,
 '_simpleFoam': 2,
 '#remove': 2,
 'stressAnalysis': 2,
 'relaxationFactors-SIMPLE': 1,
 'relaxationFactors-PIMPLE': 1,
 'BPISO': 1}
FoamInfo classes:
{'dictionary': 531}

```
