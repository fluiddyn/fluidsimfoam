# fvSolution

We study fvSolution files in OpenFOAM tutorials. The results can be obtained by running

```sh
cd dev/study_OF_examples
./study_1_filename.py check
# or (faster)
./study_1_filename.py
```

Here are the results:

```
nb_examples = 541

{'Empty file': 9, 'parser error': 0, 'wrong files': 1}

{
 'solvers': 515,
 'relaxationFactors': 325,
 'PIMPLE': 316,
 'SIMPLE': 166,
 'cache': 37,
 'PISO': 27,
 'potentialFlow': 22
 }

names_level1:
{
 'relaxationFactors/equations': 304,
 'PIMPLE/nNonOrthogonalCorrectors': 297,
 'PIMPLE/nCorrectors': 269,
 'PIMPLE/nOuterCorrectors': 194,
 'solvers/p_rgh': 193,
 'PIMPLE/momentumPredictor': 187,
 'solvers/p_rghFinal': 169,
 'SIMPLE/nNonOrthogonalCorrectors': 157,
 'solvers/p': 146,
 'relaxationFactors/fields': 137,
 'solvers/U': 111,
 'solvers/"pcorr.*"': 91,
 'solvers/pFinal': 88,
 'PIMPLE/pRefValue': 78,
 'PIMPLE/pRefCell': 62,
 'solvers/h': 58,
 'PIMPLE/correctPhi': 53
 }

names_level2:
{
 'solvers/p_rgh/tolerance': 193,
 'solvers/p_rgh/relTol': 193,
 'solvers/p_rgh/solver': 190,
 'solvers/p_rghFinal/relTol': 168,
 'solvers/p/relTol': 144,
 'solvers/p/tolerance': 143,
 'solvers/p/solver': 134,
 'solvers/p_rghFinal/$p_rgh': 129,
 'solvers/p_rgh/smoother': 124,
 'relaxationFactors/equations/".*"': 122,
 'solvers/U/solver': 111,
 'solvers/U/tolerance': 111,
 'solvers/U/relTol': 111
 }

FoamInfo classes:
{'dictionary': 531}

```
