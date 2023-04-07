# turbulenceProperties

We study turbulenceProperties files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
./study_1_filename.py turbulenceProperties check
# or (faster)
./study_1_filename.py turbulenceProperties
```

Here are the results:

```
nb_examples = 334
{'Empty file': 0, 'parser error': 0, 'wrong files': 0}

{
 'simulationType': 333,
 'RAS': 162,
 'LES': 22
}

names_level1:
{
 'RAS/RASModel': 161,
 'RAS/turbulence': 155,
 'RAS/printCoeffs': 155
}

FoamInfo classes:
{'dictionary': 334}

```
