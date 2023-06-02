# For a parametric study with SedFoam

- `tuto_sed_async.py` is a parametric script (see `./tuto_sed_async.py -h`) launching a
  simulation and controlling it from Python.

- `submit_simuls.py` submits on a LEGI cluster few simulations for different parameters.

- `make_dataframe.py` creates a Pandas DataFrame from the saved simulation results. The
  computations are only done when needed since there is a cache mechanism.
