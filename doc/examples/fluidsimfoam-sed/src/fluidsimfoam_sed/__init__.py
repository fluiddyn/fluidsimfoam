from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverSED(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_sed"
        self.class_name = "Simul"
        self.short_name = "sed"

        self.classes.Output.module_name = "fluidsimfoam_sed.output"
        self.classes.Output.class_name = "OutputSED"


class Simul(SimulFoam):
    InfoSolver = InfoSolverSED
