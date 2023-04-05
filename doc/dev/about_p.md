# p

We study the "p" files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_p.py check
# or (faster)
python study_p.py
```

Here are the results:

```
nb_examples = 303
{'Empty file': 0, 'parser error': 8, 'wrong files': 0}

{
 'dimensions': 295,
 'internalField': 295,
 'boundaryField': 295,
 '#include "include/initialConditions"': 14
}

names_level1:
{
 'boundaryField/outlet': 136,
 'boundaryField/inlet': 125,
 'boundaryField/walls': 66,
 'boundaryField/frontAndBack': 58,
 'boundaryField/#includeEtc "caseDicts/setConstraintTypes"': 55
}

names_level2:
{
 'boundaryField/outlet/type': 135,
 'boundaryField/inlet/type': 124,
 'boundaryField/outlet/value': 118
}

FoamInfo classes:
{'volScalarField': 295}
Fluidsimfoam issues (2.64 % of files): (saved in tmp_issues.txt)

```
