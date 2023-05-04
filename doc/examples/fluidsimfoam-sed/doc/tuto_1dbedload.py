from fluidsimfoam_sed import Simul

params = Simul.create_default_params()

params.output.sub_directory = "doc_fluidsimfoam/sed"
params.short_name_type_run = "tuto"

params.control_dict.end_time = 0.2

# create a simulation directory
sim = Simul(params)

# start the simulation
sim.make.exec("run")

# change some input parameters
params.control_dict.end_time = 0.4
# regenerate the control dict file
sim.input_files.control_dict.generate_file()
# restart the simulation
sim.make.exec("run")
