from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverCBox(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_cbox"
        self.class_name = "Simul"
        self.short_name = "cbox"

        self.classes.Output.module_name = "fluidsimfoam_cbox.output"
        self.classes.Output.class_name = "OutputCBox"


class Simul(SimulFoam):
    InfoSolver = InfoSolverCBox
