from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/tgv"

sim = Simul(params)
