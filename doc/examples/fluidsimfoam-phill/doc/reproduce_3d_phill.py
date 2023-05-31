from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "sin_3d"

params.init_fields.buoyancy_frequency = 0.001
params.transport_properties.nu = 0.01
params.transport_properties.pr = 10

params.control_dict.end_time = 86000
params.control_dict.delta_t = 10
params.control_dict.write_interval = 1000

params.block_mesh_dict.geometry = "3d_phill"
params.block_mesh_dict.lx = 10
params.block_mesh_dict.ly = 10
params.block_mesh_dict.lz = 10
params.block_mesh_dict.h_max = 3
params.block_mesh_dict.ly_porosity = 10

params.block_mesh_dict.nx = 20
params.block_mesh_dict.ny = 20
params.block_mesh_dict.nz = 20
params.block_mesh_dict.nz_p = 10

params.g.value = [0, 0, -9.81]

params.fv_options.momentum_source.active = False
params.fv_options.atm_coriolis_u_source.active = True
params.fv_options.porosity.active = True

sim = Simul(params)

sim.make.exec("run")
