import argparse

from fluidsimfoam_phill import Simul

parser = argparse.ArgumentParser(
    prog="phill",
    description="Run a flow over periodic hills simulation",
)

parser.add_argument(
    "-nsave",
    default=10,
    type=int,
    help="Number of save output to ﬁle.",
)

parser.add_argument(
    "-nx",
    default=200,
    type=int,
    help="Number of grids in x-direction",
)

parser.add_argument(
    "-ny",
    default=200,
    type=int,
    help="Number of grids in y-direction",
)

parser.add_argument("--end_time", default=20.0, type=float)

parser.add_argument(
    "-h_max",
    default=80,
    type=int,
    help="Maximum height of the hill",
)

parser.add_argument(
    "-np", "--nb-mpi-procs", type=int, default=4, help="Number of MPI processes"
)

args = parser.parse_args()

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.block_mesh_dict.geometry = "sinus"
params.short_name_type_run = "sinus"

params.parallel.method = "simple"
params.parallel.nsubdoms = args.nb_mpi_procs
params.parallel.nsubdoms_xyz = [
    int(args.nb_mpi_procs / 2),
    args.nb_mpi_procs - int(args.nb_mpi_procs / 2),
    1,
]

params.init_fields.buoyancy_frequency = 0.001
params.constant.transport.nu = 0.01
params.constant.transport.pr = 10

params.control_dict.end_time = args.end_time
params.control_dict.write_interval = args.end_time / args.nsave

params.block_mesh_dict.lx = 2000
params.block_mesh_dict.ly = 2000
params.block_mesh_dict.ly_porosity = 3000
# geometry parameters
params.block_mesh_dict.h_max = args.h_max

params.block_mesh_dict.nx = args.nx
params.block_mesh_dict.ny = int(args.ny * 0.8)
params.block_mesh_dict.n_porosity = int(args.ny * 0.2)

params.fv_options.momentum_source.active = False
params.fv_options.porosity.active = True

# not supported by OpenFOAM 1912...
# params.fv_options.atm_coriolis_u_source.active = True
# params.fv_options.atm_coriolis_u_source.omega = [0, 0, 7.2921e-5]

sim = Simul(params)

sim.make.exec("run")
