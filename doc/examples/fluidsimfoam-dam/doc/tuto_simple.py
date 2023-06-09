from fluidsimfoam_dam import Simul

params = Simul.create_default_params()

params.output.sub_directory = "tuto_fluidsimfoam/dam"
params.control_dict.end_time = 4.0

params.parallel.method = "simple"
params.parallel.nsubdoms = 2
params.parallel.nsubdoms_xyz = [2, 1, 1]

params.block_mesh_dict.height_dam = 0.5
params.block_mesh_dict.width_dam = 0.2

params.constant.transport.water.nu = 2.0e-6

params.block_mesh_dict.nx = 80
params.block_mesh_dict.ny = 80

# creation of the simulation directory
sim = Simul(params)

# run the simulation (i.e. all necessary OpenFOAM commands)
sim.make.exec("run")
