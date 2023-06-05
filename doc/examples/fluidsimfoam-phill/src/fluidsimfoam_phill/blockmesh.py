import numpy as np

from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    Point,
    SimpleGrading,
)

possible_geometries = ("sinus", "2d_phill", "3d_phill")


def make_code_blockmesh(bmd_params):
    if bmd_params.geometry not in possible_geometries:
        raise ValueError(
            f"{bmd_params.geometry = } not in {possible_geometries = }"
        )
    func = globals()["make_code_" + bmd_params.geometry]
    return func(bmd_params)


def make_spline_points_sin(nx, lx, h_max, z):
    x = np.linspace(0, lx, nx)
    fx = (h_max / 2) * (1 - np.cos(2 * np.pi * abs((x - (lx / 2)) / lx)))
    return [Point(x, y, z) for x, y in zip(x, fx)]


def make_spline_points_gaussian(
    n_points, mu, sigma, curve_start, curve_end, h_max, plane, offset
):
    """n_points: number of points to generate spline
    mu: mean of gaussian distribution value (center of hill)
    sigma: standard deviation of gaussian distribution divided by mu
    curve_start: starting point of curve(hill)
    curve_end: end point of curve(hill)
    h_max: maximum height of hill
    plane: the plane that curve is in it, like: 'xy', 'xz' and 'yz'
    offset: location of plane on the other coordinate"""
    sigma *= mu
    length = np.abs(curve_end - curve_start)
    x = np.linspace(0, length, n_points)

    fx = np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sigma, 2.0))) * h_max

    x = np.linspace(curve_start, curve_end, n_points)

    if plane == "yz":
        return [Point(offset, y, z) for y, z in zip(x, fx)]
    elif plane == "xz":
        return [Point(x, offset, z) for x, z in zip(x, fx)]
    elif plane == "xy":
        return [Point(x, y, offset) for x, y in zip(x, fx)]
    else:
        raise NotImplementedError(f"{plane = } is not implemented!")


def make_code_sinus(bmd_params):
    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    n_porosity = bmd_params.n_porosity

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity

    h_max = bmd_params.h_max

    x_expansion_ratio = 1
    y_expansion_ratio = [[0.1, 0.25, 41.9], [0.9, 0.75, 1]]
    z_expansion_ratio = 1

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    for x_y_z_name in (
        (0, h_max, 0, "v-bot-inlet"),
        (lx, h_max, 0, "v-bot-outlet"),
        (lx, ly, 0, "v-top-outlet"),
        (lx, ly + ly_p, 0, "v-sponge-outlet"),
        (0, ly + ly_p, 0, "v-sponge-inlet"),
        (0, ly, 0, "v-top-inlet"),
    ):
        bmd.add_vertex(*x_y_z_name)

    bmd.replicate_vertices_further_z(lz)

    b0 = bmd.add_hexblock_from_2d(
        ["v-bot-inlet", "v-bot-outlet", "v-top-outlet", "v-top-inlet"],
        [nx, ny, nz],
        "hill",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b1 = bmd.add_hexblock_from_2d(
        ["v-top-inlet", "v-top-outlet", "v-sponge-outlet", "v-sponge-inlet"],
        [nx, n_porosity, nz],
        "porosity",
    )

    bmd.add_splineedge(
        ["v-bot-inlet", "v-bot-outlet"],
        "spline-z0",
        make_spline_points_sin(nx, lx, h_max, 0),
    )
    bmd.add_splineedge(
        ["v-bot-inlet_dz", "v-bot-outlet_dz"],
        "spline-z",
        make_spline_points_sin(nx, lx, h_max, lz),
    )

    bmd.add_boundary("wall", "top", [b1.face("n")])
    bmd.add_boundary("wall", "bottom", [b0.face("s")])
    bmd.add_cyclic_boundaries(
        "outlet",
        "inlet",
        [b0.face("e"), b1.face("e")],
        [b0.face("w"), b1.face("w")],
    )
    bmd.add_boundary(
        "empty",
        "frontandbackplanes",
        [
            b0.face("b"),
            b1.face("b"),
            b0.face("t"),
            b1.face("t"),
        ],
    )

    return bmd.format(sort_vortices="as_added")


def make_code_2d_phill(bmd_params):
    # number of points for making gaussian distribution
    n_points = 50

    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    n_porosity = bmd_params.n_porosity

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity
    l_hill = bmd_params.l_hill
    hill_start = bmd_params.hill_start
    h_max = bmd_params.h_max

    hill_end = hill_start + l_hill

    # variance of gaussian distribution
    sigma = bmd_params.sigma

    # mean of gaussian distribution
    mu = 0.5 * l_hill

    nx_up_stream = int(nx * hill_start / lx)
    nx_hill = int(nx * l_hill / lx)
    nx_down_stream = nx - nx_hill - nx_up_stream

    x_expansion_ratio = 1
    y_expansion_ratio = [[0.1, 0.25, 41.9], [0.9, 0.75, 1]]
    z_expansion_ratio = 1

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    for x_y_z_name in (
        (0, 0, 0, "v-bot-inlet"),
        (hill_start, 0, 0, "v-bot-hill_start"),
        (hill_end, 0, 0, "v-bot-hill_end"),
        (lx, 0, 0, "v-bot-outlet"),
        (lx, ly, 0, "v-top-outlet"),
        (hill_end, ly, 0, "v-top-hill_end"),
        (hill_start, ly, 0, "v-top-hill_start"),
        (0, ly, 0, "v-top-inlet"),
        (lx, ly + ly_p, 0, "v-sponge-outlet"),
        (0, ly + ly_p, 0, "v-sponge-inlet"),
    ):
        bmd.add_vertex(*x_y_z_name)

    bmd.replicate_vertices_further_z(lz)

    b0 = bmd.add_hexblock_from_2d(
        ["v-bot-inlet", "v-bot-hill_start", "v-top-hill_start", "v-top-inlet"],
        [nx_up_stream, ny, nz],
        "b-up_stream",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b1 = bmd.add_hexblock_from_2d(
        [
            "v-bot-hill_start",
            "v-bot-hill_end",
            "v-top-hill_end",
            "v-top-hill_start",
        ],
        [nx_hill, ny, nz],
        "b-hill",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b2 = bmd.add_hexblock_from_2d(
        ["v-bot-hill_end", "v-bot-outlet", "v-top-outlet", "v-top-hill_end"],
        [nx_down_stream, ny, nz],
        "b-down_stream",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b3 = bmd.add_hexblock_from_2d(
        ["v-top-inlet", "v-top-outlet", "v-sponge-outlet", "v-sponge-inlet"],
        [nx, n_porosity, nz],
        "porosity",
    )

    bmd.add_splineedge(
        ["v-bot-hill_start", "v-bot-hill_end"],
        "spline-z0",
        make_spline_points_gaussian(
            n_points, mu, sigma, hill_start, hill_end, h_max, "xy", 0
        ),
    )

    bmd.add_splineedge(
        ["v-bot-hill_start_dz", "v-bot-hill_end_dz"],
        "spline-z",
        make_spline_points_gaussian(
            n_points, mu, sigma, hill_start, hill_end, h_max, "xy", lz
        ),
    )

    bmd.add_boundary("wall", "top", b3.face("n"))
    bmd.add_boundary("wall", "bottom", [b0.face("s"), b1.face("s"), b2.face("s")])
    bmd.add_cyclic_boundaries(
        "outlet",
        "inlet",
        [b2.face("e"), b3.face("e")],
        [b0.face("w"), b3.face("w")],
    )
    bmd.add_boundary(
        "empty",
        "frontandbackplanes",
        [
            b0.face("b"),
            b1.face("b"),
            b2.face("b"),
            b3.face("b"),
            b0.face("t"),
            b1.face("t"),
            b2.face("t"),
            b3.face("t"),
        ],
    )
    bmd.add_boundary(
        "patch",
        "interface_top",
        [
            b0.face("n"),
            b1.face("n"),
            b2.face("n"),
        ],
    )
    bmd.add_boundary(
        "patch",
        "interface_sponge",
        [
            b3.face("s"),
        ],
    )
    bmd.add_merge_patch_pairs("interface_sponge", "interface_top")

    return bmd.format()


def make_code_3d_phill(bmd_params):
    # number of points for making gaussian distribution
    n_points = 50

    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    n_porosity = bmd_params.n_porosity

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    h_max = bmd_params.h_max
    l_p = bmd_params.ly_porosity

    # variance of gaussian distribution
    sigma = bmd_params.sigma

    x_expansion_ratio = 1
    y_expansion_ratio = 1
    z_expansion_ratio = 1.1

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    for x_y_z_name in (
        (-lx / 2, -ly / 2, 0, "v-sw"),
        (0, -ly / 2, 0, "v-s"),
        (lx / 2, -ly / 2, 0, "v-se"),
        (lx / 2, 0, 0, "v-e"),
        (lx / 2, ly / 2, 0, "v-ne"),
        (0, ly / 2, 0, "v-n"),
        (-lx / 2, ly / 2, 0, "v-nw"),
        (-lx / 2, 0, 0, "v-w"),
        (0, 0, h_max, "v-c"),
    ):
        bmd.add_vertex(*x_y_z_name)

    vnames = list(bmd.vertices.keys())

    bmd.replicate_vertices_further_z(lz, suffix="_dz1", vnames=vnames)
    bmd.replicate_vertices_further_z(lz + l_p, suffix="_dz2", vnames=vnames)

    b0 = bmd.add_hexblock_from_2d(
        ["v-sw", "v-s", "v-c", "v-w"],
        [nx, ny, nz],
        "sw",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
        suffix_zp="_dz1",
    )

    b1 = bmd.add_hexblock_from_2d(
        ["v-s", "v-se", "v-e", "v-c"],
        [nx, ny, nz],
        "se",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
        suffix_zp="_dz1",
    )

    b2 = bmd.add_hexblock_from_2d(
        ["v-c", "v-e", "v-ne", "v-n"],
        [nx, ny, nz],
        "ne",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
        suffix_zp="_dz1",
    )

    b3 = bmd.add_hexblock_from_2d(
        ["v-w", "v-c", "v-n", "v-nw"],
        [nx, ny, nz],
        "nw",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
        suffix_zp="_dz1",
    )

    b4 = bmd.add_hexblock_from_2d(
        ["v-sw", "v-se", "v-ne", "v-nw"],
        [2 * nx, 2 * ny, n_porosity],
        "porosity",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
        suffix_zm="_dz1",
        suffix_zp="_dz2",
    )

    bmd.add_splineedge(
        ["v-s", "v-c"],
        "spline-s",
        make_spline_points_gaussian(
            n_points, ly / 2, sigma, -ly / 2, 0, h_max, "yz", 0
        ),
    )

    bmd.add_splineedge(
        ["v-e", "v-c"],
        "spline-e",
        make_spline_points_gaussian(
            n_points, lx / 2, sigma, lx / 2, 0, h_max, "xz", 0
        ),
    )

    bmd.add_splineedge(
        ["v-n", "v-c"],
        "spline-n",
        make_spline_points_gaussian(
            n_points, ly / 2, sigma, ly / 2, 0, h_max, "yz", 0
        ),
    )

    bmd.add_splineedge(
        ["v-w", "v-c"],
        "spline-w",
        make_spline_points_gaussian(
            n_points, lx / 2, sigma, -lx / 2, 0, h_max, "xz", 0
        ),
    )

    bmd.add_boundary("wall", "top", [b4.face("t")])
    bmd.add_boundary(
        "wall", "bottom", [b0.face("b"), b1.face("b"), b2.face("b"), b3.face("b")]
    )
    bmd.add_cyclic_boundaries(
        "outlet",
        "inlet",
        [b1.face("e"), b2.face("e"), b4.face("e")],
        [b0.face("w"), b3.face("w"), b4.face("w")],
    )
    bmd.add_cyclic_boundaries(
        "front",
        "back",
        [b0.face("s"), b1.face("s"), b4.face("s")],
        [b2.face("n"), b3.face("n"), b4.face("n")],
    )
    bmd.add_boundary(
        "patch",
        "interface_top",
        [
            b0.face("t"),
            b1.face("t"),
            b2.face("t"),
            b3.face("t"),
        ],
    )
    bmd.add_boundary(
        "patch",
        "interface_sponge",
        [
            b4.face("b"),
        ],
    )
    bmd.add_merge_patch_pairs("interface_sponge", "interface_top")
    return bmd.format(sort_vortices="as_added")
