from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverSedveg(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_sedveg"
        self.class_name = "Simul"
        self.short_name = "sedveg"

        self.classes.Output.module_name = "fluidsimfoam_sedveg.output"
        self.classes.Output.class_name = "OutputSedveg"


class Simul(SimulFoam):
    InfoSolver = InfoSolverSedveg
