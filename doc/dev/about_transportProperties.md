# transportProperties

We study transportProperties files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
./study_1_filename.py transportProperties check
# or (faster)
./study_1_filename.py transportProperties
```

Here are the results:

```
nb_examples = 254
{'Empty file': 0, 'parser error': 0, 'wrong files': 0}

{
 'nu': 145,
 'transportModel': 133,
 'phases': 83,
 'sigma': 72,
 'water': 72,
 'air': 62,
 'DT': 21,
 'Prt': 9,
 '".*"': 8,
 'vapour': 8,
 'rhoInf': 7,
 'beta': 7,
 'TRef': 7,
 'Pr': 7,
 'continuousPhase': 7,
 'rho.air': 7,
 'sigmas': 7
}

names_level1:
{
 'water/transportModel': 72,
 'water/nu': 72,
 'water/rho': 72,
 'air/transportModel': 62,
 'air/nu': 62,
 'air/rho': 62
}

FoamInfo classes:
{'dictionary': 254}

No parser issue for transportProperties!

```
