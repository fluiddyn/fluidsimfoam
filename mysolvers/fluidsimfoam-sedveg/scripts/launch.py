import numpy as np
from fluidsimfoam_sedveg import Simul

params = Simul.create_default_params()

params.output.sub_directory = "doc_fluidsimfoam/sedveg"
params.short_name_type_run = "tuto"

params.control_dict.end_time = 2
params.control_dict.write_interval = 1
params.constant.twophase_ras.sus = 1

# create a simulation directory
sim = Simul(params)

# start the simulation
sim.make.exec("run")