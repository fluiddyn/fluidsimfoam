"""Code that should be part of the next ``fluidsim_core`` release"""

from pathlib import Path
from textwrap import dedent
from typing import Union

from fluiddyn.io import FLUIDSIM_PATH

path_dir_results = Path(FLUIDSIM_PATH)


def find_path_result_dir(thing: Union[str, Path, None] = None):
    """Return the path of a result directory.

    thing: str or Path, optional

      Can be an absolute path, a relative path, or even simply just
      the name of the directory under $FLUIDSIM_PATH.

    """
    if thing is None:
        return Path.cwd()

    if not isinstance(thing, Path):
        path = Path(thing)
    else:
        path = thing

    path = path.expanduser()

    if path.is_dir():
        return path.absolute()

    if not path.is_absolute():
        path = path_dir_results / path

    if not path.is_dir():
        raise ValueError(f"Cannot find a path corresponding to {thing}")

    return path


def start_ipython_load_sim(load_import="from fluidsim import load"):
    """Start IPython and load a simulation"""
    from IPython import start_ipython

    argv = ["--matplotlib", "-i", "-c"]
    code = dedent(
        f"""
        import numpy as np
        import matplotlib.pyplot as plt
        import pandas as pd
        {load_import}
        print("Loading simulation")
        sim = load()
        params = sim.params
        print("`sim`, `params`, `np`, `plt` and `pd` variables are available")
    """
    )
    argv.append("; ".join(code.strip().split("\n")))
    start_ipython(argv=argv)
