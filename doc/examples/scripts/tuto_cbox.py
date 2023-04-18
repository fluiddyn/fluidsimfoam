from fluidsimfoam_cbox import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/cbox"

sim = Simul(params)
