import numpy as np

from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    Point,
    SimpleGrading,
    Vertex,
)

possible_geometries = ("sinus", "2d_phill")


def make_code_blockmesh(bmd_params):
    if bmd_params.geometry not in possible_geometries:
        raise ValueError(
            f"{bmd_params.geometry = } not in {possible_geometries = }"
        )
    func = globals()["make_code_" + bmd_params.geometry]
    return func(bmd_params)


def make_spline_points_sin(nx, lx, h_max, z):
    x_dot = np.linspace(0, lx, nx)
    y_dot = []
    for x in x_dot:
        y_dot.append(
            (h_max / 2)
            * (1 - np.cos(2 * np.pi * min(abs((x - (lx / 2)) / lx), 1)))
        )

    return [Point(x_dot[dot], y_dot[dot], z) for dot in range(nx)]


def make_spline_points_gaussian(n_points, mu, sig, h_max, hill_start, z):
    dx = (mu / n_points) * 2
    x_dot = np.linspace(0, 2 * mu, n_points)
    y_dot = np.exp(-np.power(x_dot - mu, 2.0) / (2 * np.power(sig, 2.0)))

    x_dot *= h_max
    y_dot *= h_max
    x_dot += hill_start

    return [Point(x_dot[dot], y_dot[dot], z) for dot in range(n_points)]


def make_code_sinus(bmd_params):
    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    ny_porosity = bmd_params.ny_porosity

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity

    h_max = bmd_params.h_max  # hill height

    x_expansion_ratio = 1
    y_expansion_ratio = [[0.1, 0.25, 41.9], [0.9, 0.75, 1]]
    z_expansion_ratio = 1

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    basevs = [
        Vertex(0, h_max, lz, "v-bot-inlet"),
        Vertex(lx, h_max, lz, "v-bot-outlet"),
        Vertex(lx, ly, lz, "v-top-outlet"),
        Vertex(lx, ly + ly_p, lz, "v-sponge-outlet"),
        Vertex(0, ly + ly_p, lz, "v-sponge-inlet"),
        Vertex(0, ly, lz, "v-top-inlet"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, v.y, 0, v.name + "-z0")
    for v in basevs:
        bmd.add_vertex(v.x, v.y, v.z, v.name + "-z")

    b0 = bmd.add_hexblock(
        (
            "v-bot-inlet-z0",
            "v-bot-outlet-z0",
            "v-top-outlet-z0",
            "v-top-inlet-z0",
            "v-bot-inlet-z",
            "v-bot-outlet-z",
            "v-top-outlet-z",
            "v-top-inlet-z",
        ),
        (nx, ny, nz),
        "hill",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b1 = bmd.add_hexblock(
        (
            "v-top-inlet-z0",
            "v-top-outlet-z0",
            "v-sponge-outlet-z0",
            "v-sponge-inlet-z0",
            "v-top-inlet-z",
            "v-top-outlet-z",
            "v-sponge-outlet-z",
            "v-sponge-inlet-z",
        ),
        (nx, ny_porosity, nz),
        "porosity",
        SimpleGrading(1, 1, 1),
    )

    bmd.add_splineedge(
        ["v-bot-inlet-z0", "v-bot-outlet-z0"],
        "spline-z0",
        make_spline_points_sin(nx, lx, h_max, 0),
    )
    bmd.add_splineedge(
        ["v-bot-inlet-z", "v-bot-outlet-z"],
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
    mu = 5
    sig = 0.5
    n_points = 50

    h_max = 0.2
    hill_start = 0.6
    hill_end = mu * 2 * h_max + hill_start

    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity

    ny_porosity = bmd_params.ny_porosity

    nx_up_stream = int(nx * hill_start / lx)
    nx_hill = int(nx * (hill_end - hill_start) / lx)
    nx_down_stream = nx - nx_hill - nx_up_stream

    x_expansion_ratio = 1
    y_expansion_ratio = [[0.1, 0.25, 41.9], [0.9, 0.75, 1]]
    z_expansion_ratio = 1

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    basevs = [
        Vertex(0, 0, lz, "v-bot-inlet"),
        Vertex(hill_start, 0, lz, "v-bot-hill_start"),
        Vertex(hill_end, 0, lz, "v-bot-hill_end"),
        Vertex(lx, 0, lz, "v-bot-outlet"),
        Vertex(lx, ly, lz, "v-top-outlet"),
        Vertex(hill_end, ly, lz, "v-top-hill_end"),
        Vertex(hill_start, ly, lz, "v-top-hill_start"),
        Vertex(0, ly, lz, "v-top-inlet"),
        Vertex(lx, ly + ly_p, lz, "v-sponge-outlet"),
        Vertex(0, ly + ly_p, lz, "v-sponge-inlet"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, v.y, 0, v.name + "-z0")
        bmd.add_vertex(v.x, v.y, v.z, v.name + "-z")

    b0 = bmd.add_hexblock(
        (
            "v-bot-inlet-z0",
            "v-bot-hill_start-z0",
            "v-top-hill_start-z0",
            "v-top-inlet-z0",
            "v-bot-inlet-z",
            "v-bot-hill_start-z",
            "v-top-hill_start-z",
            "v-top-inlet-z",
        ),
        (nx_up_stream, ny, nz),
        "b-up_stream",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b1 = bmd.add_hexblock(
        (
            "v-bot-hill_start-z0",
            "v-bot-hill_end-z0",
            "v-top-hill_end-z0",
            "v-top-hill_start-z0",
            "v-bot-hill_start-z",
            "v-bot-hill_end-z",
            "v-top-hill_end-z",
            "v-top-hill_start-z",
        ),
        (nx_hill, ny, nz),
        "b-hill",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )

    b2 = bmd.add_hexblock(
        (
            "v-bot-hill_end-z0",
            "v-bot-outlet-z0",
            "v-top-outlet-z0",
            "v-top-hill_end-z0",
            "v-bot-hill_end-z",
            "v-bot-outlet-z",
            "v-top-outlet-z",
            "v-top-hill_end-z",
        ),
        (nx_down_stream, ny, nz),
        "b-down_stream",
        SimpleGrading(x_expansion_ratio, y_expansion_ratio, z_expansion_ratio),
    )
    b3 = bmd.add_hexblock(
        (
            "v-top-inlet-z0",
            "v-top-outlet-z0",
            "v-sponge-outlet-z0",
            "v-sponge-inlet-z0",
            "v-top-inlet-z",
            "v-top-outlet-z",
            "v-sponge-outlet-z",
            "v-sponge-inlet-z",
        ),
        (nx, int(ny * 0.5), nz),
        "porosity",
        SimpleGrading(1, 1, 1),
    )

    bmd.add_splineedge(
        ["v-bot-hill_start-z0", "v-bot-hill_end-z0"],
        "spline-z0",
        make_spline_points_gaussian(n_points, mu, sig, h_max, hill_start, 0),
    )

    bmd.add_splineedge(
        ["v-bot-hill_start-z", "v-bot-hill_end-z"],
        "spline-z",
        make_spline_points_gaussian(n_points, mu, sig, h_max, hill_start, lz),
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
