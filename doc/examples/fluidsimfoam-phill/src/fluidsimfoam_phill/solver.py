from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam


class InfoSolverPHill(InfoSolver):
    """Contain the information on a :class:`fluidsimfoam_phill.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_phill.solver"
        self.class_name = "Simul"
        self.short_name = "phill"

        self.classes.Output.module_name = "fluidsimfoam_phill.output"
        self.classes.Output.class_name = "OutputPHill"


class SimulPHill(SimulFoam):
    """A solver which compiles and runs using a Snakefile."""

    InfoSolver = InfoSolverPHill


Simul = SimulPHill
