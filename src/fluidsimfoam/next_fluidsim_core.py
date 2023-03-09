from pathlib import Path

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
