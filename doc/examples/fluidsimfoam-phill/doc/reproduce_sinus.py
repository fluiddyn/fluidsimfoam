from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "sin_2d"

params.init_fields.buoyancy_frequency = 0.001
params.constant.transport.nu = 0.01
params.constant.transport.pr = 10

hour = 3600
day = 24 * hour
params.control_dict.end_time = day
params.control_dict.delta_t = 10
params.control_dict.write_interval = 2 * hour

# lengths are in meters
params.block_mesh_dict.geometry = "sinus"
params.block_mesh_dict.lx = 2000
params.block_mesh_dict.ly = 2000
params.block_mesh_dict.ly_porosity = 3000

params.block_mesh_dict.h_max = 80

params.block_mesh_dict.nx = 20
params.block_mesh_dict.ny = 50
params.block_mesh_dict.n_porosity = 20

params.fv_options.momentum_source.active = True
params.fv_options.momentum_source.ubar = "(0.1 0 0)"
params.fv_options.atm_coriolis_u_source.active = True
params.fv_options.porosity.active = True

sim = Simul(params)

sim.make.exec("run")
