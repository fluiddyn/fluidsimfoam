"""Base class for the ``sim`` object"""

from pathlib import Path
from time import sleep, time

from inflection import underscore

from fluiddyn.util import mpi  # noqa: F401
from fluidsim_core.solver import SimulCore
from fluidsimfoam.log import logger
from fluidsimfoam.params import Parameters


class SimulFoam(SimulCore):
    """Base OpenFOAM Fluidsim solver."""

    Parameters = Parameters

    @classmethod
    def _complete_params_with_default(cls, params):
        pass

    @classmethod
    def create_default_params(cls):
        # TODO: needed because abstract method in fluidsim-core=<0.7.2
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

        self.input_files = self.output.input_files

    def stop_time_loop(self, stop_at="writeNow", verbose=True):
        if verbose:
            print("Telling OpenFOAM to stop... (overwrite controlDict file)")
            t_stop = time()
        ctr_dict = self.input_files.control_dict.read()
        ctr_dict["stopAt"] = stop_at
        ctr_dict.overwrite()

        process = self.make.process

        if process is None:
            return

        while process.poll() is None:
            # touch needed (strange OpenFOAM bug?)
            (self.path_run / "system/controlDict").touch()
            sleep(0.05)
            if verbose:
                saved_directories = sorted(
                    path.name
                    for path in self.path_run.glob("*")
                    if path.name[0].isdigit()
                )
                print(f"\rsaved times {saved_directories}", end="")

        if verbose:
            print(
                f"\nSimulation stopped {time() - t_stop:.2f} s "
                f"after `stopAt = {stop_at}`"
            )
