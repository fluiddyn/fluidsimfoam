from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam


class InfoSolverSED(InfoSolver):
    """Contain the information on a :class:`fluidsimfoam_sed.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_sed.solver"
        self.class_name = "Simul"
        self.short_name = "sed"

        self.classes.Output.module_name = "fluidsimfoam_sed.output"
        self.classes.Output.class_name = "OutputSED"


class SimulSED(SimulFoam):
    InfoSolver = InfoSolverSED


Simul = SimulSED
