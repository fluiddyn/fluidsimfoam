from fluidsimfoam_phill import Simul

params = Simul.create_default_params()
params.short_name_type_run = "sin_2d"
params.init_fields.buoyancy_frequency = 0.001
params.transport_properties.nu = 0.01
params.transport_properties.pr = 10
params.control_dict.end_time = 1200000
params.control_dict.delta_t = 10
params.block_mesh_dict.lx = 2000
params.block_mesh_dict.ly = 5000
params.block_mesh_dict.nx = 20
params.block_mesh_dict.ny = 50

params.output.sub_directory = "examples_fluidsimfoam/phill"

sim = Simul(params)

sim.make.exec("run")
