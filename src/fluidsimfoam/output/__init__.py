"""Base class for the ``sim.output`` object

.. autosummary::
   :toctree:

   base
   fields
   log
   dataframe_from_paths

"""

from fluidsim_core.paths import path_dir_results

from .base import Output
from .dataframe_from_paths import (
    get_dataframe_from_paths,
    get_mean_values_from_path,
)

__all__ = [
    "path_dir_results",
    "Output",
    "get_dataframe_from_paths",
    "get_mean_values_from_path",
]
