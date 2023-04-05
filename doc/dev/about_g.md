# g

We study the "g" files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_g.py check
# or (faster)
python study_g.py
```

Here are the results:

```
nb_examples = 224
{'Empty file': 0, 'parser error': 1, 'wrong files': 0}

{
 'dimensions': 223,
 'value': 223
}

FoamInfo classes:
{'uniformDimensionedVectorField': 223}
Fluidsimfoam issues (0.45 % of files): (saved in tmp_issues.txt)

```
