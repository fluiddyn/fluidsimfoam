from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverDam(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_dam"
        self.class_name = "Simul"
        self.short_name = "dam"

        self.classes.Output.module_name = "fluidsimfoam_dam.output"
        self.classes.Output.class_name = "OutputDam"


class Simul(SimulFoam):
    InfoSolver = InfoSolverDam
