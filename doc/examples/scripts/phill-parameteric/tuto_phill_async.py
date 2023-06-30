import argparse

from fluidsimfoam_phill import Simul


parser = argparse.ArgumentParser(
    prog="phill",
    description="Run a flow over periodic hills simulation",
)

parser.add_argument(
    "-g",
    "--geometry",
    default="sinus",
    type=str,
    help="choose one of these geometries: 'sinus', '2d_phill','3d_phill'",
)
parser.add_argument(
    "-nsave",
    default=2,
    type=int,
    help="Number of save output to ﬁle.",
)
parser.add_argument(
    "-nmesh",
    default=10000,
    type=int,
    help="Number of mesh",
)
parser.add_argument("--end-time", default=20.0, type=float)

args = parser.parse_args()


params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = args.geometry
params.block_mesh_dict.geometry = args.geometry

params.init_fields.buoyancy_frequency = 0.001
params.constant.transport.nu = 0.01
params.constant.transport.pr = 10

params.control_dict.end_time = args.end_time
params.control_dict.write_interval = args.end_time / args.nsave

if args.geometry == "sinus":
    params.block_mesh_dict.geometry = "sinus"
    params.block_mesh_dict.lx = 2000
    params.block_mesh_dict.ly = 2000
    params.block_mesh_dict.ly_porosity = 3000
    # geometry parameters
    params.block_mesh_dict.h_max = 80

    default_nmesh = 1400
    params.block_mesh_dict.nx = int(20 * (args.nmesh / default_nmesh) ** (1 / 2))
    params.block_mesh_dict.ny = int(50 * (args.nmesh / default_nmesh) ** (1 / 2))
    params.block_mesh_dict.n_porosity = int(
        20 * (args.nmesh / default_nmesh) ** (1 / 2)
    )
elif args.geometry == "2d_phill":
    params.block_mesh_dict.lx = 6
    params.block_mesh_dict.ly = 1
    params.block_mesh_dict.lz = 0.01
    params.block_mesh_dict.ly_porosity = 1
    # geometry parameters
    params.block_mesh_dict.l_hill = 0.9
    params.block_mesh_dict.hill_start = 0.6
    params.block_mesh_dict.h_max = 0.2
    params.block_mesh_dict.sigma = 0.2

    default_nmesh = 9000
    params.block_mesh_dict.nx = int(200 * (args.nmesh / default_nmesh) ** (1 / 2))
    params.block_mesh_dict.ny = int(30 * (args.nmesh / default_nmesh) ** (1 / 2))
    params.block_mesh_dict.nz = 1
    params.block_mesh_dict.n_porosity = int(
        15 * (args.nmesh / default_nmesh) ** (1 / 2)
    )
elif args.geometry == "3d_phill":
    params.block_mesh_dict.lx = 10
    params.block_mesh_dict.ly = 10
    params.block_mesh_dict.lz = 10
    params.block_mesh_dict.ly_porosity = 10
    # geometry parameters
    params.block_mesh_dict.h_max = 3
    params.block_mesh_dict.sigma = 0.2
    default_nmesh = 162500
    params.block_mesh_dict.nx = int(50 * (args.nmesh / default_nmesh) ** (1 / 3))
    params.block_mesh_dict.ny = int(50 * (args.nmesh / default_nmesh) ** (1 / 3))
    params.block_mesh_dict.nz = int(50 * (args.nmesh / default_nmesh) ** (1 / 3))
    params.block_mesh_dict.n_porosity = int(
        15 * (args.nmesh / default_nmesh) ** (1 / 3)
    )

    params.constant.g.value = [0, 0, -9.81]


else:
    print("Select an available geometry!")


params.fv_options.momentum_source.active = False
params.fv_options.atm_coriolis_u_source.active = True
params.fv_options.porosity.active = True
params.fv_options.atm_coriolis_u_source.omega = [0, 0, 7.2921e-5]

sim = Simul(params)

sim.make.exec("run")
