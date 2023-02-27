from fluidsim_core.solver import SimulCore


class SimulFoam(SimulCore):
    """Base OpenFOAM solver."""

    @classmethod
    def _complete_params_with_default(cls, params):
        pass

    def __init__(self, params):
        super().__init__(params)
