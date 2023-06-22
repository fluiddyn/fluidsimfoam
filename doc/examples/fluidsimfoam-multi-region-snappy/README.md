# Solver fluidsimfoam-multi-region-snappy

Solver produced with

```sh
fluidsimfoam-initiate-solver multi-region-snappy \
  -c $FOAM_TUTORIALS/heatTransfer/chtMultiRegionFoam/snappyMultiRegionHeater
```

See
https://www.xsim.info/articles/OpenFOAM/en-US/tutorials/heatTransfer-chtMultiRegionFoam-snappyMultiRegionHeater.html

## Installation

First install [fluidsimfoam] (see
https://fluidsimfoam.readthedocs.io/en/latest/install.html). Then:

```sh
pip install -e .
```

[fluidsimfoam]: https://foss.heptapod.net/fluiddyn/fluidsimfoam
