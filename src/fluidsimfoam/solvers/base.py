from pathlib import Path

from inflection import underscore

from fluiddyn.util import mpi  # noqa: F401
from fluidsim_core.solver import SimulCore
from fluidsimfoam.log import logger


class SimulFoam(SimulCore):
    """Base OpenFOAM solver."""

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("fv_solution", doc="""TODO""")
        params.fv_solution._set_child("solvers", doc="""TODO""")
        attribs = {
            "solver": "PCG",
            "preconditioner": "DIC",
            "tolerance": 1e-06,
            "relTol": 0.01,
        }

        params.fv_solution.solvers._set_child("p", attribs=attribs)
        params.fv_solution.solvers._set_child("pFinal", attribs=attribs)
        params.fv_solution.solvers.pFinal.relTol = 0
        params.fv_solution.solvers._set_child(
            "U",
            attribs={
                "solver": "PBiCGStab",
                "preconditioner": "DILU",
                "tolerance": 1e-08,
                "relTol": 0,
            },
        )
        params.fv_solution._set_child(
            "piso",
            attribs={
                "nCorrectors": 2,
                "nNonOrthogonalCorrectors": 1,
                "pRefPoint": "(0 0 0)",
                "pRefValue": 0,
            },
        )

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
