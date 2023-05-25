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


def make_spline_points_sin(nx, ny, z, lx, ly, h_max):
    dots = []
    for dot in range(nx):
        x_dot = dot * lx / (nx - 1)
        y_dot = (h_max / 2) * (
            1 - np.cos(2 * np.pi * min(abs((x_dot - (lx / 2)) / lx), 1))
        )
        dots.append([x_dot, y_dot])

    return [Point(dot[0], dot[1], z) for dot in dots]


def make_spline_points_gaussian(n_points, mu, sig, h, hill_start, z):
    dx = (mu / n_points) * 2
    gauss = np.zeros((n_points + 1, 2))

    for dot in range(n_points + 1):
        x_dot = dot * dx
        y_dot = np.exp(-np.power(x_dot - mu, 2.0) / (2 * np.power(sig, 2.0)))
        gauss[dot, :] = [x_dot, y_dot]

    gauss[:, :] = gauss[:, :] * h
    gauss[:, 0] = gauss[:, 0] + hill_start

    return [Point(dot[0], dot[1], z) for dot in gauss]


def make_code_sinus(bmd_params):
    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    ny_porosity = bmd_params.ny_porosity

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity

    h_max = bmd_params.h_max

    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    basevs = [
        Vertex(0, h_max, lz, "v0"),
        Vertex(lx, h_max, lz, "v1"),
        Vertex(lx, ly, lz, "v2"),
        Vertex(lx, ly + ly_p, lz, "v3"),
        Vertex(0, ly + ly_p, lz, "v4"),
        Vertex(0, ly, lz, "v5"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, v.y, 0, v.name + "-0")
    for v in basevs:
        bmd.add_vertex(v.x, v.y, v.z, v.name + "+z")

    b0 = bmd.add_hexblock(
        ("v0-0", "v1-0", "v2-0", "v5-0", "v0+z", "v1+z", "v2+z", "v5+z"),
        (nx, ny, nz),
        "b0",
        SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
    )

    b1 = bmd.add_hexblock(
        ("v5-0", "v2-0", "v3-0", "v4-0", "v5+z", "v2+z", "v3+z", "v4+z"),
        (nx, ny_porosity, nz),
        "porosity",
        SimpleGrading(1, 1, 1),
    )

    bmd.add_splineedge(
        ["v0-0", "v1-0"],
        "spline0",
        make_spline_points_sin(nx, ny, 0, lx, ly, h_max),
    )
    bmd.add_splineedge(
        ["v0+z", "v1+z"],
        "spline1",
        make_spline_points_sin(nx, ny, lz, lx, ly, h_max),
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
    sig = 1
    n_points = 30

    h = 0.174
    hill_start = 0.6
    hill_end = mu * 2 * h + hill_start

    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    ly_p = bmd_params.ly_porosity

    ny_porosity = bmd_params.ny_porosity

    nx_up_stream = int(nx * hill_start / lx)
    nx_hill = int(nx * 0.33)
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
        (nx, ny, nz),
        "porosity",
        SimpleGrading(1, 1, 1),
    )

    bmd.add_splineedge(
        ["v-bot-hill_start-z0", "v-bot-hill_end-z0"],
        "spline-z0",
        make_spline_points_gaussian(n_points, mu, sig, h, hill_start, 0),
    )

    bmd.add_splineedge(
        ["v-bot-hill_start-z", "v-bot-hill_end-z"],
        "spline-z",
        make_spline_points_gaussian(n_points, mu, sig, h, hill_start, lz),
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
