# decomposeParDict

We study decomposeParDict files in OpenFOAM tutorials. The results can be obtained by
running

```sh
cd dev/study_OF_examples
./study_1_filename.py decomposeParDict check
# or (faster)
./study_1_filename.py decomposeParDict
```

Here are the results:

```
nb_examples = 327
{'Empty file': 0, 'parser error': 0, 'wrong files': 0}

{
 'numberOfSubdomains': 327,
 'method': 327,
 'coeffs': 218,
 'regions': 15,
 'constraints': 12,
 'distributed': 6,
 'roots': 6,
 'scotchCoeffs': 6
}

names_level1:
{'coeffs/n': 215}

FoamInfo classes:
{'dictionary': 327}

```
