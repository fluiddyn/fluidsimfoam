from pathlib import Path
from textwrap import dedent

from fluiddyn.io import FLUIDSIM_PATH

from .log import logger


def path_try_from_fluidsim_path(path_dir):
    """Converts to a :class:`pathlib.Path` object and if it does not exists,
    attempts a path relative to environment variable ``FLUIDSIM_PATH``.

    """
    path = Path(path_dir)

    if not path.exists():
        logger.info("Trying to open the path relative to $FLUIDSIM_PATH")
        path = Path(FLUIDSIM_PATH) / path_dir

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
