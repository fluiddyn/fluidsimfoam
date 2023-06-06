from fluidsimfoam_dam import Simul

params = Simul.create_default_params()

params.output.sub_directory = "poster_fluidsimfoam/dam"
params.control_dict.end_time = 1.0

params.parallel.method = "simple"
params.parallel.nsubdoms = 4
params.parallel.nsubdoms_xyz = [2, 2, 1]

params.constant.transport.water.nu = 2.0e-6
...

# creation of the simulation directory
sim = Simul(params)

# run the simulation (i.e. all necessary OpenFOAM commands)
sim.make.exec("run")
