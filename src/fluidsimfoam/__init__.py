"""
Fluidsimfoam API reference

.. rubric:: Sub-packages

.. autosummary::
   :toctree:

   foam_input_files
   output
   resources
   solvers
   util

.. rubric:: Modules

.. autosummary::
   :toctree:

   info
   init_fields
   log
   make
   next_fluidsim_core
   operators
   tasks

"""
import importlib.metadata

from fluidsim_core.params import Parameters

from .next_fluidsim_core import path_try_from_fluidsim_path

__version__ = importlib.metadata.version(__package__ or __name__)
__all__ = ["load", "load_simul", "load_params"]


def load_simul(path_dir="."):
    """Loads a simulation

    Parameters
    ----------
    path_dir: str or path-like
        Path to a directory containing a simulation. If not provided the
        current directory is used.

    """

    from fluidsimfoam.solvers import get_solver_short_name, import_cls_simul

    path_dir = path_try_from_fluidsim_path(path_dir)

    short_name = get_solver_short_name(path_dir)
    Simul = import_cls_simul(short_name)

    path_params = path_dir / "params_simul.xml"
    if not path_params.exists():
        path_params = path_dir / ".data_fluidsim/params_simul.xml"

    params = Parameters(path_file=path_params)

    # Modify parameters prior to loading
    params.NEW_DIR_RESULTS = False
    params.output.HAS_TO_SAVE = False
    params.path_run = path_dir

    return Simul(params)


def load_params(path_dir="."):
    """Load a :class:`fluidsim_core.params.Parameters` instance from `path_dir`.

    Parameters
    ----------
    path_dir : str or path-like
        Path to a simulation directory.

    Returns
    -------
    params: :class:`fluidsim_core.params.Parameters`

    """
    path_dir = path_try_from_fluidsim_path(path_dir)
    return Parameters(path_file=path_dir / "params_simul.xml")


load = load_simul
