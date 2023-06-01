from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "sin_3d"

params.init_fields.buoyancy_frequency = 0.001
params.constant.transport.nu = 0.01
params.constant.transport.pr = 0.01

hour = 3600
day = 24 * hour
params.control_dict.end_time = day
params.control_dict.write_interval = 2 * hour
params.control_dict.delta_t = 10

# Units are in kilometer:
params.block_mesh_dict.geometry = "3d_phill"
params.block_mesh_dict.lx = 10
params.block_mesh_dict.ly = 10
params.block_mesh_dict.lz = 10
params.block_mesh_dict.h_max = 3  # hill height
params.block_mesh_dict.ly_porosity = 10  # sponge layer height

params.block_mesh_dict.sig = 0.2  # hill sharpness

params.block_mesh_dict.nx = 20
params.block_mesh_dict.ny = 20
params.block_mesh_dict.nz = 20
params.block_mesh_dict.n_porosity = 15

params.constant.g.value = [0, 0, -9.81]

params.fv_options.momentum_source.active = False
params.fv_options.atm_coriolis_u_source.active = True
params.fv_options.porosity.active = True
params.fv_options.atm_coriolis_u_source.omega = [0, 0, 7.2921e-5]

sim = Simul(params)

sim.make.exec("run")
