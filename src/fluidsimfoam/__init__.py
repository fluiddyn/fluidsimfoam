"""
Fluidsimfoam API reference

.. rubric:: Sub-packages

.. autosummary::
   :toctree:

   foam_input_files
   solvers
   output
   util
   resources

.. rubric:: Modules

.. autosummary::
   :toctree:

   info
   make
   init_fields
   operators
   log
   tasks
   testing
   params

"""
import importlib.metadata
import sys

from fluiddyn.io.redirect_stdout import stdout_redirected
from fluidsim_core.paths import find_path_result_dir
from fluidsimfoam.params import Parameters

__version__ = importlib.metadata.version(__package__ or __name__)
__all__ = ["load", "load_simul", "load_params"]


def load_simul(path_dir=".", hide_stdout=False):
    """Loads a simulation

    Parameters
    ----------
    path_dir: str or path-like
        Path to a directory containing a simulation. If not provided the
        current directory is used.

    """

    from fluidsimfoam.solvers import get_solver_short_name, import_cls_simul

    path_dir = find_path_result_dir(path_dir)

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

    with stdout_redirected(hide_stdout):
        sim = Simul(params)

    return sim


def load_params(path_dir="."):
    """Load a :class:`fluidsim_core.params.Parameters` instance from ``path_dir``

    Parameters
    ----------
    path_dir : str or path-like
        Path to a simulation directory.

    Returns
    -------
    params: :class:`fluidsim_core.params.Parameters`

    """
    path_dir = find_path_result_dir(path_dir)
    return Parameters(path_file=path_dir / "params_simul.xml")


load = load_simul


if any("pytest" in part for part in sys.argv):
    import pytest

    pytest.register_assert_rewrite("fluidsimfoam.testing")
