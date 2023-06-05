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
# time step mentioned in https://www.theses.fr/2020GRALU022
params.control_dict.delta_t = 10
params.control_dict.write_interval = 2 * hour

# lengths are in meters
params.block_mesh_dict.geometry = "2d_phill"
params.block_mesh_dict.lx = 6
params.block_mesh_dict.ly = 1
params.block_mesh_dict.lz = 0.01
params.block_mesh_dict.ly_porosity = 1

# geometry parameters
params.block_mesh_dict.l_hill = 0.9
params.block_mesh_dict.hill_start = 0.6
params.block_mesh_dict.h_max = 0.2
params.block_mesh_dict.sigma = 0.2

params.block_mesh_dict.nx = 200
params.block_mesh_dict.ny = 30
params.block_mesh_dict.nz = 1
params.block_mesh_dict.n_porosity = 15

params.fv_options.momentum_source.active = False
params.fv_options.atm_coriolis_u_source.active = True
params.fv_options.porosity.active = True

sim = Simul(params)

sim.make.exec("run")
