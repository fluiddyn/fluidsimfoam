"""Base class for the ``sim.oper`` object"""

import shutil
from subprocess import PIPE, run

from fluidsimfoam.foam_input_files.fields import VolVectorField


class Operators:
    def __init__(self, sim):
        self.sim = sim

        if hasattr(sim.output.input_files, "block_mesh_dict"):
            assert (sim.output.path_run / "system/blockMeshDict").exists()

    def get_cells_coords(self):
        path_c = self.sim.path_run / "0/C"

        if not path_c.exists():
            path_polymesh = self.sim.path_run / "constant/polyMesh/points"

            if not path_polymesh.exists():
                self.sim.make.exec("polymesh", stdout=PIPE)

            if not path_polymesh.exists():
                raise RuntimeError(f"{path_polymesh} does not exists")

            path_postProcess = shutil.which("postProcess")

            if path_postProcess is None:
                raise RuntimeError("OpenFOAM not available")

            run(
                ["postProcess", "-func", "writeCellCentres"],
                cwd=self.sim.path_run,
                stdout=PIPE,
            )

        field = VolVectorField.from_path(path_c, skip_boundary_field=True)
        return field.get_components()
