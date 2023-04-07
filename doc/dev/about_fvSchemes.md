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
{'Empty file': 0, 'parser error': 7, 'wrong files': 0}

{
 'gradSchemes': 497,
 'divSchemes': 497,
 'laplacianSchemes': 497,
 'ddtSchemes': 496,
 'snGradSchemes': 485,
 'interpolationSchemes': 484,
 'wallDist': 90,
 'fluxRequired': 45,
 'oversetInterpolation': 13,
 'oversetInterpolationSuppressed': 8,
 'fluxScheme': 8,
 'd2dt2Schemes': 6
 }

names_level1:
{
 'ddtSchemes/default': 475,
 'gradSchemes/default': 471,
 'laplacianSchemes/default': 471,
 'interpolationSchemes/default': 463,
 'snGradSchemes/default': 460,
 'divSchemes/default': 391,
 'divSchemes/div(phi,U)': 236,
 'divSchemes/div(phi,k)': 205,
 'divSchemes/div(((rho*nuEff)*dev2(T(grad(U)))))': 202,
 'divSchemes/div(phi,epsilon)': 156,
 'divSchemes/div(phi,K)': 109,
 'divSchemes/turbulence': 100,
 'divSchemes/div(rhoPhi,U)': 96,
 'wallDist/method': 90,
 'divSchemes/div((nuEff*dev2(T(grad(U)))))': 87,
 'divSchemes/div(phi,alpha)': 70,
 'divSchemes/div(phirb,alpha)': 68,
 'divSchemes/div(phi,h)': 66,
 'divSchemes/div(phi,omega)': 61,
 'divSchemes/div(phi,R)': 56,
 'divSchemes/div(R)': 55
 }

FoamInfo classes:
{'dictionary': 497}
Fluidsimfoam issues (1.39 % of files): (saved in tmp_issues.txt)

```
