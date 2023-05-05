"""
To see the coverage, run as:

```
pytest tests/test_blockmesh.py -vv --cov --cov-report term --cov-report html
firefox htmlcov/index.html
```
"""

import math
from pathlib import Path

import pytest

from fluidsimfoam.foam_input_files import dump, parse
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    EdgeGrading,
    Point,
    SimpleGrading,
    SimpleGradingElement,
    Vertex,
)


def create_code_example():
    wedgedegree = 5.0
    radius_x = 0.19
    lz = 1.1

    bmd = BlockMeshDict()
    bmd.set_metric("m")

    # base vertices which are rotated +- 2.5 degrees
    basevs = [
        Vertex(0, 0, 0, "v0"),
        Vertex(radius_x, 0, 0, "v1"),
        Vertex(radius_x, 0, lz, "v2"),
        Vertex(0, 0, lz, "v3"),
    ]

    # for coverage
    assert basevs[0] != basevs[1]

    # rotate wedgedegree/2 around z axis
    # rotated vertices are named with '-y' or '+y' suffix.
    # these verteces are added to BlockMeshDict instence to be referred
    # by following blocks and faces...
    cosd = math.cos(math.radians(wedgedegree / 2.0))
    sind = math.sin(math.radians(wedgedegree / 2.0))
    for v in basevs:
        bmd.add_vertex(v.x * cosd, -v.x * sind, v.z, v.name + "-y")
        bmd.add_vertex(v.x * cosd, v.x * sind, v.z, v.name + "+y")

    # v0+y and v3+y have same coordinate as v0-y and v3-y, respectively.
    bmd.merge_vertices()

    def vnamegen(x0z0, x1z0, x1z1, x0z1):
        return (
            x0z0 + "-y",
            x1z0 + "-y",
            x1z0 + "+y",
            x0z0 + "+y",
            x0z1 + "-y",
            x1z1 + "-y",
            x1z1 + "+y",
            x0z1 + "+y",
        )

    b0 = bmd.add_hexblock(
        vnamegen("v0", "v1", "v2", "v3"),
        (19, 1, 300),
        "b0",
        grading=SimpleGrading(
            0.1, ((0.2, 0.3, 4), (0.6, 0.4, 1), (0.2, 0.3, 1.0 / 4.0)), 1
        ),
    )

    bmd.add_boundary("wedge", "front", [b0.face("s")])
    bmd.add_boundary("wedge", "back", [b0.face("n")])
    bmd.add_boundary("wall", "tankWall", [b0.face("e")])
    bmd.add_boundary("patch", "inlet", [b0.face("b")])
    bmd.add_boundary("patch", "outlet", [b0.face("t")])
    bmd.add_boundary("empty", "axis", [b0.face("w")])

    return bmd.format()


def create_code_cbox():
    nx = ny = 80
    nz = 1
    lx = ly = 1.0
    lz = 0.1

    bmd = BlockMeshDict()
    bmd.set_metric("m")

    basevs = [
        Vertex(0, 0, lz, "v0"),
        Vertex(lx, 0, lz, "v1"),
        Vertex(lx, ly, lz, "v2"),
        Vertex(0, ly, lz, "v3"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, v.y, 0, v.name + "-0")
        bmd.add_vertex(v.x, v.y, v.z, v.name + "+z")

    vertex_names = [
        f"v{index}{post}" for post in ("-0", "+z") for index in range(4)
    ]

    b0 = bmd.add_hexblock(vertex_names, (nx, ny, nz), name="")

    bmd.add_boundary("wall", "frontAndBack", [b0.face("s"), b0.face("n")])
    bmd.add_boundary("wall", "topAndBottom", [b0.face("t"), b0.face("b")])
    bmd.add_boundary("wall", "hot", b0.face("e"))
    bmd.add_boundary("wall", "cold", b0.face("w"))

    return bmd.format(sort_vortices=False)


def create_code_tgv():
    nx = ny = nz = 40
    lx = ly = lz = 1.0

    bmd = BlockMeshDict()
    bmd.set_scale(6.28318530718)

    basevs = [
        Vertex(0, 0, lz, "v0"),
        Vertex(lx, 0, lz, "v1"),
        Vertex(lx, ly, lz, "v2"),
        Vertex(0, ly, lz, "v3"),
    ]

    for v in basevs:
        bmd.add_vertex(v.x, v.y, 0, v.name + "-z")
        bmd.add_vertex(v.x, v.y, v.z, v.name + "+z")

    # utility to to generate vertex names
    def vnamegen(x0z0, x1y0, x1y1, x0z1):
        return (
            x0z0 + "-z",
            x1y0 + "-z",
            x1y1 + "-z",
            x0z1 + "-z",
            x0z0 + "+z",
            x1y0 + "+z",
            x1y1 + "+z",
            x0z1 + "+z",
        )

    b0 = bmd.add_hexblock(
        vnamegen("v0", "v1", "v2", "v3"),
        (nx, ny, nz),
        "",
    )

    bmd.add_cyclic_boundaries(
        "upperBoundary", "lowerBoundary", b0.face("n"), b0.face("s")
    )
    bmd.add_cyclic_boundaries(
        "leftBoundary", "rightBoundary", b0.face("w"), b0.face("e")
    )
    bmd.add_cyclic_boundaries(
        "frontBoundary", "backBoundary", b0.face("t"), b0.face("b")
    )

    return bmd.format(sort_vortices=False)


path_data = Path(__file__).absolute().parent / "data_blockmesh"


@pytest.mark.parametrize(
    "name",
    ["example", "cbox", "tgv"],
)
def test_blockmesh(name):
    create_blockmesh = globals()["create_code_" + name]
    code_from_py = create_blockmesh()

    if name == "cbox":
        path_saved_file = (
            path_data.parent
            / "pure_openfoam_cases/cbox/sim0/system/blockMeshDict"
        )
    elif name == "tgv":
        path_saved_file = (
            path_data.parent / "pure_openfoam_cases/tiny-tgv/system/blockMeshDict"
        )
    else:
        path_saved_file = path_data / ("blockmesh_" + name)

    code_saved = path_saved_file.read_text()

    tree_saved_file = parse(code_saved)
    tree_from_py = parse(code_from_py)

    assert dump(tree_saved_file).strip() == dump(tree_from_py).strip()


def test_edge_grading():
    eg = EdgeGrading(*list(range(12)))
    assert eg.format() == "edgeGrading (0 1 2 3 4 5 6 7 8 9 10 11)"


def test_grading():
    SimpleGrading(*[SimpleGradingElement(i) for i in range(3)])
    EdgeGrading(*[SimpleGradingElement(i) for i in range(12)])


def test_arc_edge():
    vertices = {
        name: Vertex(index * 0.1, index * 0.2, index * 0.3, name, index=index)
        for index, name in enumerate("abc")
    }

    bmd = BlockMeshDict()

    for v in vertices.values():
        bmd.add_vertex(v)

    edge = bmd.add_arcedge(list("abc"), "edgename", vertices["b"])

    assert (
        edge.format(vertices)
        == "arc 0 1 2 (               0.1                0.2                0.3) // edgename (a b c)"
    )

    bmd.assign_vertexid()
    bmd.format_edges_section()


def test_spline_edge():
    vertices = {
        name: Vertex(index * 0.1, index * 0.2, index * 0.3, name, index=index)
        for index, name in enumerate("abc")
    }
    bmd = BlockMeshDict()
    edge = bmd.add_splineedge(
        list("abc"), "edgename", [Point(0.1, 0.1, 0.1), Point(0.2, 0.2, 0.2)]
    )
    assert (
        edge.format(vertices)
        == """spline 0 1 2                      // edgename (a b c)
    (
         (                0.1                0.1                0.1 )
         (                0.2                0.2                0.2 )
)"""
    )


def test_other():
    bmd = BlockMeshDict()

    for iz in [0, 1]:
        for iy in [0, 1]:
            for ix in [0, 1]:
                bmd.add_vertex(ix, iy, iz, f"v{ix}{iy}{iz}")

    b0 = bmd.add_hexblock(list(bmd.vertices.keys()), (10, 10, 10), "b0")

    bound0 = bmd.add_boundary("wall", "hot", b0.face("e"))
    bound0.add_face(b0.face("n"))

    bmd.add_vertex(1, 2, 4, "foo")
    bmd.del_vertex("foo")

    with pytest.raises(ValueError):
        bmd.add_vertex(bmd.vertices["v000"], 2)

    bmd.add_boundary("wall", "cold", None)
