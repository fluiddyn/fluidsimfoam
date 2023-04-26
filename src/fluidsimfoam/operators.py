class Operators:
    def __init__(self, sim):
        self.sim = sim

        if hasattr(sim.output.input_files, "block_mesh_dict"):
            assert (sim.output.path_run / "system/blockMeshDict").exists()
