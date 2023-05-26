from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "sin_2d"

params.init_fields.buoyancy_frequency = 0.001
params.transport_properties.nu = 0.01
params.transport_properties.pr = 10

params.control_dict.end_time = 86000
params.control_dict.delta_t = 10
params.control_dict.write_interval = 5000

params.block_mesh_dict.geometry = "2d_phill"
params.block_mesh_dict.lx = 6
params.block_mesh_dict.ly = 1
params.block_mesh_dict.lz = 0.01
params.block_mesh_dict.ly_porosity = 1

params.block_mesh_dict.nx = 60
params.block_mesh_dict.ny = 30
params.block_mesh_dict.nz = 1

params.fv_options.momentum_source.active = False
params.fv_options.atm_coriolis_u_source.active = False
params.fv_options.porosity.active = False

sim = Simul(params)

sim.make.exec("run")
