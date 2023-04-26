# controlDict

We study controlDict files in OpenFOAM tutorials. The results can be obtained by running

```sh
cd dev/study_OF_examples
./study_1_filename.py controlDict check
# or (faster)
./study_1_filename.py controlDict
```

Here are the results:

```
nb_examples = 425
{'Empty file': 0, 'parser error': 1, 'wrong files': 2}

{
 'application': 422,
 'startTime': 422,
 'stopAt': 422,
 'endTime': 422,
 'deltaT': 422,
 'writeControl': 422,
 'writeFormat': 422,
 'timeFormat': 422,
 'startFrom': 421,
 'writeInterval': 421,
 'purgeWrite': 421,
 'runTimeModifiable': 421,
 'writeCompression': 418,
 'timePrecision': 418,
 'writePrecision': 414,
 'adjustTimeStep': 246,
 'maxCo': 230,
 'functions': 191,
 'maxDeltaT': 181,
 'maxAlphaCo': 90,
 'libs': 55,
 'DebugSwitches': 27,
 'graphFormat': 26,
 'maxDi': 18,
 'maxAlphaDdt': 6
}

FoamInfo classes:
{'dictionary': 422}

Fluidsimfoam issues (0.24 % of files): (saved in tmp_issues.txt)

```
