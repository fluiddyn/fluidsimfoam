from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"

sim = Simul(params)
