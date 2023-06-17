from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam

__all__ = ["Simul"]


class InfoSolverMultiRegionSnappy(InfoSolver):
    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_multi_region_snappy"
        self.class_name = "Simul"
        self.short_name = "multi-region-snappy"

        self.classes.Output.module_name = (
            "fluidsimfoam_multi_region_snappy.output"
        )
        self.classes.Output.class_name = "OutputMultiRegionSnappy"


class Simul(SimulFoam):
    InfoSolver = InfoSolverMultiRegionSnappy
