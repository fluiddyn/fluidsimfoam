# fvSchemes

We study fvSchemes files in OpenFOAM tutorials. The results can be obtained
by running

```sh
cd dev/study_OF_examples
./study_1_filename.py fvSchemes check
# or (faster)
./study_1_filename.py fvSchemes
```

Here are the results:

```
nb_examples = 504
{'Empty file': 0, 'parser error': 3, 'wrong files': 0}

{
 'gradSchemes': 501,
 'divSchemes': 501,
 'laplacianSchemes': 501,
 'ddtSchemes': 500,
 'snGradSchemes': 489,
 'interpolationSchemes': 488,
 'wallDist': 92,
 'fluxRequired': 48,
 'oversetInterpolation': 16,
 'oversetInterpolationSuppressed': 10,
 'fluxScheme': 8,
 'd2dt2Schemes': 6
}

names_level1:
{
 'ddtSchemes/default': 479,
 'gradSchemes/default': 475,
 'laplacianSchemes/default': 475,
 'interpolationSchemes/default': 467,
 'snGradSchemes/default': 464,
 'divSchemes/default': 395,
 'divSchemes/div(phi,U)': 240,
 'divSchemes/div(phi,k)': 209,
 'divSchemes/div(((rho*nuEff)*dev2(T(grad(U)))))': 205,
 'divSchemes/div(phi,epsilon)': 159,
 'divSchemes/div(phi,K)': 112,
 'divSchemes/turbulence': 102,
 'divSchemes/div(rhoPhi,U)': 96,
 'wallDist/method': 92,
 'divSchemes/div((nuEff*dev2(T(grad(U)))))': 89,
 'divSchemes/div(phi,alpha)': 70,
 'divSchemes/div(phi,h)': 68,
 'divSchemes/div(phirb,alpha)': 68,
 'divSchemes/div(phi,omega)': 63,
 'divSchemes/div(phi,R)': 58,
 'divSchemes/div(R)': 57
}

FoamInfo classes:
{'dictionary': 501}

Fluidsimfoam issues (0.60 % of files): (saved in tmp_issues.txt)

```
