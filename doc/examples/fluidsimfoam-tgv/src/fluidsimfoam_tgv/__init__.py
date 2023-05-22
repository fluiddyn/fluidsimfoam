from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverTGV(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_tgv"
        self.class_name = "Simul"
        self.short_name = "tgv"

        self.classes.Output.module_name = "fluidsimfoam_tgv.output"
        self.classes.Output.class_name = "OutputTGV"


class Simul(SimulFoam):
    InfoSolver = InfoSolverTGV
