"""Console script functions

"""

from functools import partial

from fluidsimfoam.next_fluidsim_core import (
    start_ipython_load_sim as _start_ipython_load_sim,
)
from fluidsimfoam.solvers import available_solvers


def print_versions():
    import fluiddyn
    import fluidsim_core
    import fluidsimfoam

    versions = {"Package": "Version", "-------": "-------"}

    packages = [fluidsimfoam, fluiddyn, fluidsim_core]
    for package in packages:
        versions[package.__name__] = package.__version__

    for pkg_name, version in versions.items():
        print(f"{pkg_name.ljust(15)} {version}")

    names = sorted(set([entry_point.name for entry_point in available_solvers()]))
    print("\nInstalled solvers: " + ", ".join(names))


start_ipython_load_sim = partial(
    _start_ipython_load_sim, load_import="from fluidsimfoam import load"
)
