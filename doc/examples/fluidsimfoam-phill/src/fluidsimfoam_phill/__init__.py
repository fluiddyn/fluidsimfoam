from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverPHill(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_phill"
        self.class_name = "Simul"
        self.short_name = "phill"

        self.classes.Output.module_name = "fluidsimfoam_phill.output"
        self.classes.Output.class_name = "OutputPHill"


class Simul(SimulFoam):
    InfoSolver = InfoSolverPHill
