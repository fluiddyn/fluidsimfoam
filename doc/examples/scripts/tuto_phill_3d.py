import argparse

from fluidsimfoam_phill import Simul

parser = argparse.ArgumentParser(
    prog="phill",
    description="Run a flow over periodic hills simulation",
)

parser.add_argument(
    "-nsave",
    default=2,
    type=int,
    help="Number of save output to ﬁle.",
)
parser.add_argument(
    "-nx",
    default=50,
    type=int,
    help="Number of grids in x-direction",
)
parser.add_argument("--end-time", default=20.0, type=float)

args = parser.parse_args()

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "3d_phill"
params.block_mesh_dict.geometry = "3d_phill"

params.init_fields.buoyancy_frequency = 0.001
params.constant.transport.nu = 0.01
params.constant.transport.pr = 10

params.control_dict.end_time = args.end_time
params.control_dict.write_interval = args.end_time / args.nsave

params.block_mesh_dict.lx = 10
params.block_mesh_dict.ly = 10
params.block_mesh_dict.lz = 10
params.block_mesh_dict.ly_porosity = 10
# geometry parameters
params.block_mesh_dict.h_max = 3
params.block_mesh_dict.sigma = 0.2

params.block_mesh_dict.nx = args.nx
params.block_mesh_dict.ny = args.nx
params.block_mesh_dict.nz = args.nx
params.block_mesh_dict.n_porosity = int(args.nx * 15 / 50)

params.constant.g.value = [0, 0, -9.81]

params.fv_options.momentum_source.active = False
params.fv_options.porosity.active = True

# not supported by OpenFOAM 1912...
# params.fv_options.atm_coriolis_u_source.active = True
# params.fv_options.atm_coriolis_u_source.omega = [0, 0, 7.2921e-5]

sim = Simul(params)

sim.make.exec("run")
