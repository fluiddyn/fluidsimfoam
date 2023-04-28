from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam


class InfoSolverTGV(InfoSolver):
    """Contain the information on a :class:`fluidsimfoam_tgv.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_tgv.solver"
        self.class_name = "Simul"
        self.short_name = "tgv"

        self.classes.Output.module_name = "fluidsimfoam_tgv.output"
        self.classes.Output.class_name = "OutputTGV"


class SimulTGV(SimulFoam):
    InfoSolver = InfoSolverTGV


Simul = SimulTGV
