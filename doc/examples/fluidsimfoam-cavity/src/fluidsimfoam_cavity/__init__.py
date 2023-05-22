from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverCavity(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_cavity"
        self.class_name = "Simul"
        self.short_name = "cavity"

        self.classes.Output.module_name = "fluidsimfoam_cavity.output"
        self.classes.Output.class_name = "OutputCavity"


class Simul(SimulFoam):
    InfoSolver = InfoSolverCavity
