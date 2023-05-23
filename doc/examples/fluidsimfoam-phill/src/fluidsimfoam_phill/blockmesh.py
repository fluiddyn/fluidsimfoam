from math import cos, pi

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

    dots = []
    for dot in range(nx):
        x_dot = dot * lx / (nx - 1)
        y_dot = (h_max / 2) * (
            1 - cos(2 * pi * min(abs((x_dot - (lx / 2)) / lx), 1))
        )
        dots.append([x_dot, y_dot])

    bmd.add_splineedge(
        ["v0-0", "v1-0"],
        "spline0",
        [Point(dot[0], dot[1], 0) for dot in dots],
    )
    bmd.add_splineedge(
        ["v0+z", "v1+z"],
        "spline1",
        [Point(dot[0], dot[1], lz) for dot in dots],
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
    nx = bmd_params.nx
    ny = bmd_params.ny
    nz = bmd_params.nz
    nx = 50
    ny = 100
    nz = 1

    lx = bmd_params.lx
    ly = bmd_params.ly
    lz = bmd_params.lz
    lx = ly = 1
    lz = 0.05
    bmd = BlockMeshDict()
    bmd.set_scale(bmd_params.scale)

    basevs = [
        Vertex(0, ly, 0, "v0"),
        Vertex(0.5, ly, 0, "v1"),
        Vertex(1.5, ly, 0, "v2"),
        Vertex(6, ly, 0, "v3"),
        Vertex(6, ly, lz, "v4"),
        Vertex(1.5, ly, lz, "v5"),
        Vertex(0.5, ly, lz, "v6"),
        Vertex(0, ly, lz, "v7"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, 0, v.z, v.name + "-0")
        bmd.add_vertex(v.x, v.y, v.z, v.name + "+y")

    b0 = bmd.add_hexblock(
        ("v0-0", "v1-0", "v1+y", "v0+y", "v7-0", "v6-0", "v6+y", "v7+y"),
        (nx, ny, nz),
        "b0",
        SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
    )

    b1 = bmd.add_hexblock(
        ("v1-0", "v2-0", "v2+y", "v1+y", "v6-0", "v5-0", "v5+y", "v6+y"),
        (nx, ny, nz),
        "b1",
        SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
    )

    b2 = bmd.add_hexblock(
        ("v2-0", "v3-0", "v3+y", "v2+y", "v5-0", "v4-0", "v4+y", "v5+y"),
        (225, ny, nz),
        "b2",
        SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
    )

    bmd.add_splineedge(
        ["v1-0", "v2-0"],
        "spline0",
        [
            Point(0.6, 0.0124, 0),
            Point(0.7, 0.0395, 0),
            Point(0.8, 0.0724, 0),
            Point(0.9, 0.132, 0),
            Point(1, 0.172, 0),
            Point(1.1, 0.132, 0),
            Point(1.2, 0.0724, 0),
            Point(1.3, 0.0395, 0),
            Point(1.4, 0.0124, 0),
        ],
    )
    bmd.add_splineedge(
        ["v6-0", "v5-0"],
        "spline1",
        [
            Point(0.6, 0.0124, lz),
            Point(0.7, 0.0395, lz),
            Point(0.8, 0.0724, lz),
            Point(0.9, 0.132, lz),
            Point(1, 0.172, lz),
            Point(1.1, 0.132, lz),
            Point(1.2, 0.0724, lz),
            Point(1.3, 0.0395, lz),
            Point(1.4, 0.0124, lz),
        ],
    )

    bmd.add_boundary("wall", "top", [b0.face("n"), b1.face("n"), b2.face("n")])
    bmd.add_boundary("wall", "bottom", [b0.face("s"), b1.face("s"), b2.face("s")])
    bmd.add_cyclic_boundaries("outlet", "inlet", b2.face("e"), b0.face("w"))
    bmd.add_boundary(
        "empty",
        "frontandbackplanes",
        [
            b0.face("b"),
            b1.face("b"),
            b2.face("b"),
            b0.face("t"),
            b1.face("t"),
            b2.face("t"),
        ],
    )

    return bmd.format()
