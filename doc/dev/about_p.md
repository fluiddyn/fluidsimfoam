# p

We study the "p" files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
./study_1_filename.py p check
# or (faster)
./study_1_filename.py p
```

Here are the results:

```
nb_examples = 303
{'Empty file': 0, 'parser error': 0, 'wrong files': 2}

{
 'dimensions': 301,
 'internalField': 301,
 'boundaryField': 301,
 '#include "include/initialConditions"': 14
}

names_level1:
{
 'boundaryField/outlet': 136,
 'boundaryField/inlet': 130,
 'boundaryField/walls': 66,
 'boundaryField/frontAndBack': 58,
 'boundaryField/#includeEtc "caseDicts/setConstraintTypes"': 56
}

names_level2:
{
 'boundaryField/outlet/type': 135,
 'boundaryField/inlet/type': 129,
 'boundaryField/outlet/value': 118
}

FoamInfo classes:
{'volScalarField': 301}

No parser issue for p!

```
