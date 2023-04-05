# controlDict

We study controlDict files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
python study_controldict.py check
# or (faster)
python study_controldict.py
```

Here are the results:

```
nb_examples = 425
{'Empty file': 0, 'parser error': 5, 'wrong files': 0}

{
 'application': 420,
 'startTime': 420,
 'stopAt': 420,
 'endTime': 420,
 'deltaT': 420,
 'writeControl': 420,
 'writeFormat': 420,
 'timeFormat': 420,
 'startFrom': 419,
 'writeInterval': 419,
 'purgeWrite': 419,
 'runTimeModifiable': 419,
 'writeCompression': 416,
 'timePrecision': 416,
 'writePrecision': 412,
 'adjustTimeStep': 244,
 'maxCo': 229,
 'functions': 189,
 'maxDeltaT': 180,
 'maxAlphaCo': 90,
 'libs': 55,
 'graphFormat': 26,
 'DebugSwitches': 26,
 'maxDi': 17,
 'maxAlphaDdt': 6
 }

FoamInfo classes:
{'dictionary': 420}
Fluidsimfoam issues (1.18 % of files): (saved in tmp_issues.txt)
```
