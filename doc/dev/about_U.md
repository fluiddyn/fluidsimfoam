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
{'Empty file': 38, 'parser error': 0, 'wrong files': 3}

{
 'dimensions': 328,
 'boundaryField': 328,
 'internalField': 326,
 '#include "include/initialConditions"': 16,
 'Uinlet': 6
}

names_level1:
{
 'boundaryField/outlet': 139,
 'boundaryField/inlet': 128,
 'boundaryField/walls': 69,
 'boundaryField/frontAndBack': 68,
 'boundaryField/#includeEtc "caseDicts/setConstraintTypes"': 55
}

names_level2:
{
 'boundaryField/outlet/type': 138,
 'boundaryField/inlet/type': 128,
 'boundaryField/outlet/value': 102
}

FoamInfo classes:
{'volVectorField': 328}

No parser issue for U!

```
