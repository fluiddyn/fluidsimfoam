from fluidsimfoam.foam_input_files.polymesh import get_cells_coords


class Operators:
    def __init__(self, sim):
        self.sim = sim

        if hasattr(sim.output.input_files, "block_mesh_dict"):
            assert (sim.output.path_run / "system/blockMeshDict").exists()

    def get_cells_coords(self):
        path_points = self.sim.path_run / "constant/polyMesh/points"

        if not path_points.exists():
            self.sim.make.exec("polymesh")

        if not path_points.exists():
            raise RuntimeError(f"{path_points} does not exists")

        return get_cells_coords(path_points)
