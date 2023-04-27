from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam


class InfoSolverCBox(InfoSolver):
    """Contain the information on a :class:`fluidsimfoam_cbox.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_cbox.solver"
        self.class_name = "Simul"
        self.short_name = "cbox"

        self.classes.Output.module_name = "fluidsimfoam_cbox.output"
        self.classes.Output.class_name = "OutputCBox"


class SimulCBox(SimulFoam):

    InfoSolver = InfoSolverCBox


Simul = SimulCBox
