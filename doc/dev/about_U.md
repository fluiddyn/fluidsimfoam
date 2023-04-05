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
{'Empty file': 0, 'parser error': 48, 'wrong files': 0}

{
 'dimensions': 321,
 'internalField': 321,
 'boundaryField': 321,
 '#include "include/initialConditions"': 16,
 'Uinlet': 6
}

names_level1:
{
 'boundaryField/outlet': 137,
 'boundaryField/inlet': 126,
 'boundaryField/walls': 69,
 'boundaryField/frontAndBack': 67,
 'boundaryField/#includeEtc "caseDicts/setConstraintTypes"': 51
}

names_level2:
{
 'boundaryField/outlet/type': 136,
 'boundaryField/inlet/type': 126,
 'boundaryField/outlet/value': 101
}

FoamInfo classes:
{'volVectorField': 321}
Fluidsimfoam issues (13.01 % of files): (saved in tmp_issues.txt)

```