from pathlib import Path

from inflection import underscore

from fluiddyn.util import mpi  # noqa: F401
from fluidsim_core.solver import SimulCore
from fluidsimfoam.log import logger


class SimulFoam(SimulCore):
    """Base OpenFOAM solver."""

    @classmethod
    def _complete_params_with_default(cls, params):
        pass

    @classmethod
    def create_default_params(cls):
        # TODO: needed because abstract method in fluidsim-core
        params = super().create_default_params()
        return params

    def __init__(self, params):
        super().__init__(params)

        self._objects_to_print = "{:28s}{}\n".format("sim: ", type(self))
        dict_classes = self.info_solver.import_classes()

        # initialize objects
        for cls_name, Class in dict_classes.items():
            # only initialize if Class is not the Simul class
            if isinstance(self, Class):
                continue

            obj_name = underscore(cls_name)
            setattr(self, obj_name, Class(self))
            self._objects_to_print += "{:28s}{}\n".format(
                f"sim.{obj_name}: ", Class
            )

        if "Output" in dict_classes:
            if not params.NEW_DIR_RESULTS:
                self.path_run = self.output.path_run = Path(params.path_run)
            else:
                # path_run would be initialized by the Output instance if available
                # See self.output._init_name_run()
                self.path_run = Path(self.output.path_run)

            self.output.post_init()
        else:
            self.path_run = None
            if mpi.rank == 0:
                logger.warning("No output class initialized!")
