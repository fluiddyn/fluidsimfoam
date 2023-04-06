# U

We study the "U" files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_u.py check
# or (faster)
python study_u.py
```

Here are the results:

```
nb_examples = 369
{'Empty file': 38, 'parser error': 2, 'wrong files': 3}

{
 'dimensions': 326,
 'boundaryField': 326,
 'internalField': 324,
 '#include "include/initialConditions"': 16,
 'Uinlet': 6
}

names_level1:
{
 'boundaryField/outlet': 139,
 'boundaryField/inlet': 128,
 'boundaryField/walls': 69,
 'boundaryField/frontAndBack': 68,
 'boundaryField/#includeEtc "caseDicts/setConstraintTypes"': 53
}

names_level2:
{
 'boundaryField/outlet/type': 138,
 'boundaryField/inlet/type': 128,
 'boundaryField/outlet/value': 102
}

FoamInfo classes:
{'volVectorField': 326}

Fluidsimfoam issues (0.54 % of files): (saved in tmp_issues.txt)

```
