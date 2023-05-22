from math import cos, pi

from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    Point,
    SimpleGrading,
    Vertex,
)

possible_geometries = ("sinus",)


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
