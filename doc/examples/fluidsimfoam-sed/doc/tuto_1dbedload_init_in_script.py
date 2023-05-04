import numpy as np
from fluidsimfoam_sed import Simul

params = Simul.create_default_params()

params.output.sub_directory = "doc_fluidsimfoam/sed"
params.short_name_type_run = "tuto"

params.control_dict.end_time = 0.2

# create a simulation directory
sim = Simul(params)

# set any initial conditions
x, y, z = sim.oper.get_cells_coords()
field_alpha = sim.input_files.alpha_a.read()
field_alpha.set_values(0.305 * (1.0 + np.tanh((0.075 - y) / 0.01)))
field_alpha.overwrite()

# start the simulation
sim.make.exec("run")
