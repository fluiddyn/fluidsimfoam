from fluidsimfoam.info import InfoSolver
from fluidsimfoam.solvers.base import SimulFoam


class InfoSolverCBOX(InfoSolver):
    """Contain the information on a :class:`fluidsimfoam_cbox.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "fluidsimfoam_cbox.solver"
        self.class_name = "Simul"
        self.short_name = "cbox"

        self.classes.Output.module_name = "fluidsimfoam_cbox.output"
        self.classes.Output.class_name = "OutputCBOX"


class SimulCBOX(SimulFoam):
    """A solver which compiles and runs using a Snakefile."""

    InfoSolver = InfoSolverCBOX

    @classmethod
    def create_default_params(cls):
        """Set default values of parameters as given in reference
        implementation.

        """
        params = super().create_default_params()
        # Re-define default values for parameters here, if necessary

        ...

        return params


Simul = SimulCBOX
