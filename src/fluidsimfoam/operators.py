"""Base class for the ``sim.oper`` object"""

import shutil
from subprocess import run

from fluidsimfoam.foam_input_files.fields import VolScalarField


class Operators:
    def __init__(self, sim):
        self.sim = sim

        if hasattr(sim.output.input_files, "block_mesh_dict"):
            assert (sim.output.path_run / "system/blockMeshDict").exists()

    def get_cells_coords(self):
        path_cx = self.sim.path_run / "0/Cx"

        if not path_cx.exists():
            path_polymesh = self.sim.path_run / "constant/polyMesh/points"

            if not path_polymesh.exists():
                self.sim.make.exec("polymesh")

            if not path_polymesh.exists():
                raise RuntimeError(f"{path_polymesh} does not exists")

            path_postProcess = shutil.which("postProcess")

            if path_postProcess is None:
                raise RuntimeError("OpenFOAM not available")

            run(
                ["postProcess", "-func", "writeCellCentres"],
                cwd=self.sim.path_run,
            )

        def get_arr(path):
            field = VolScalarField.from_path(path)
            return field.get_array()

        path_cy = path_cx.with_name("Cy")
        path_cz = path_cx.with_name("Cz")

        return get_arr(path_cx), get_arr(path_cy), get_arr(path_cz)
