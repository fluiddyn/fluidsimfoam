"""blockmeshhelper

Taken from https://github.com/takaakiaoki/ofblockmeshdicthelper (Git commit
58589f1) and modified as follow:

- `pyupgrade __init__.py --py39-plus`

TODO:

- unittests most format functions (especially those not already tested!)
- "sorted(set)"
- split this file in different modules (for ex. grading.py)

"""

from collections.abc import Iterable
from itertools import groupby, product
from string import Template


class Vertex:
    def __init__(self, x, y, z, name, index=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name  # identical name
        self.alias = {name}  # aliasname, self.name should be included

        # sequential index which is assigned at final output
        # for blocks, edges, boundaries
        self.index = index

    def format(self):
        com = f"{self.index} {self.name}"
        if len(self.alias) > 1:
            com += " : " + " ".join(sorted(self.alias))
        return f"( {self.x:18.15g} {self.y:18.15g} {self.z:18.15g} )  // {com}"

    def __lt__(self, rhs):
        return (self.z, self.y, self.x) < (rhs.z, rhs.y, rhs.x)

    def __eq__(self, rhs):
        return (self.z, self.y, self.x) == (rhs.z, rhs.y, rhs.x)

    def __hash__(self):
        return hash((self.z, self.y, self.x))


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def format(self):
        return f"( {self.x:18.15g} {self.y:18.15g} {self.z:18.15g} )"


class Face:
    def __init__(self, vnames, name):
        """
        vname is list or tuple of vertex names
        """
        self.vnames = vnames
        self.name = name

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        comment = " ".join(self.vnames)
        return f"({index:s})  // {self.name:s} ({comment:s})"


class Grading:
    """base class for Simple- and Edge- Grading"""


class SimpleGradingElement:
    """x, y or z Element of simpleGrading. adopted to multi-grading"""

    def __init__(self, d):
        """initialization
        d is single number for expansion ratio
          or iterative object consits (direction ratio, cell ratio, expansion ratio)
        """
        self.d = d

    def format(self):
        if isinstance(self.d, Iterable):
            return (
                "( "
                + " ".join(f"( {e[0]:g} {e[1]:g} {e[2]:g} )" for e in self.d)
                + " )"
            )
        else:
            return str(self.d)


class SimpleGrading(Grading):
    """configutation for 'simpleGrading'"""

    def __init__(self, x, y, z):
        if not isinstance(x, SimpleGradingElement):
            self.x = SimpleGradingElement(x)
        else:
            self.x = x
        if not isinstance(y, SimpleGradingElement):
            self.y = SimpleGradingElement(y)
        else:
            self.y = y
        if not isinstance(z, SimpleGradingElement):
            self.z = SimpleGradingElement(z)
        else:
            self.z = z

    def format(self):
        return (
            f"simpleGrading "
            f"({self.x.format():s} {self.y.format():s} {self.z.format():s})"
        )


class EdgeGrading(Grading):
    """configutation for 'edgeGrading'"""

    def __init__(self, x1, x2, x3, x4, y1, y2, y3, y4, z1, z2, z3, z4):
        if not isinstance(x1, SimpleGradingElement):
            self.x1 = SimpleGradingElement(x1)
        else:
            self.x1 = x1
        if not isinstance(x2, SimpleGradingElement):
            self.x2 = SimpleGradingElement(x2)
        else:
            self.x2 = x2
        if not isinstance(x3, SimpleGradingElement):
            self.x3 = SimpleGradingElement(x3)
        else:
            self.x3 = x3
        if not isinstance(x4, SimpleGradingElement):
            self.x4 = SimpleGradingElement(x4)
        else:
            self.x4 = x4
        if not isinstance(y1, SimpleGradingElement):
            self.y1 = SimpleGradingElement(y1)
        else:
            self.y1 = y1
        if not isinstance(y2, SimpleGradingElement):
            self.y2 = SimpleGradingElement(y2)
        else:
            self.y2 = y2
        if not isinstance(y3, SimpleGradingElement):
            self.y3 = SimpleGradingElement(y3)
        else:
            self.y3 = y3
        if not isinstance(y4, SimpleGradingElement):
            self.y4 = SimpleGradingElement(y4)
        else:
            self.y4 = y4
        if not isinstance(x1, SimpleGradingElement):
            self.z1 = SimpleGradingElement(z1)
        else:
            self.z1 = z1
        if not isinstance(z2, SimpleGradingElement):
            self.z2 = SimpleGradingElement(z2)
        else:
            self.z2 = z2
        if not isinstance(z3, SimpleGradingElement):
            self.z3 = SimpleGradingElement(z3)
        else:
            self.z3 = z3
        if not isinstance(z4, SimpleGradingElement):
            self.z4 = SimpleGradingElement(z4)
        else:
            self.z4 = z4

    def format(self):
        tmp = []
        for letter, index in product("xyz", "1234"):
            var = getattr(self, letter + index)
            tmp.append(var.format())
        return "edgeGrading (" + " ".join(tmp) + ")"


class HexBlock:
    def __init__(self, vnames, cells, name, grading=SimpleGrading(1, 1, 1)):
        """Initialize HexBlock instance
        vnames is the vertex names in order descrived in
            http://www.openfoam.org/docs/user/mesh-description.php
        cells is number of cells devied into in each direction
        name is the uniq name of the block
        grading is grading method.
        """
        self.vnames = vnames
        self.cells = cells
        self.name = name
        self.grading = grading

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        comment = " ".join(self.vnames)
        return (
            f"hex ({index}) {self.name} "
            f"({self.cells[0]:d} {self.cells[1]:d} {self.cells[2]:d}) "
            f"{self.grading.format()}  // {self.name} ({comment})"
        )

    def face(self, index, name=None):
        """Generate Face object
        index is number or keyword to identify the face of Hex
            0 = 'w' = 'xm' = '-100' = (0 4 7 3)
            1 = 'e' = 'xp' = '100' = (1 2 5 6)
            2 = 's' = 'ym' = '0-10' = (0 1 5 4)
            3 = 'n' = 'yp' = '010' = (2 3 7 6)
            4 = 'b' = 'zm' = '00-1' = (0 3 2 1)
            5 = 't' = zp' = '001' = (4 5 6 7)
        name is given to Face instance. If omitted, name is automatically
            genaratied like ('f-' + self.name + '-w')
        """
        kw_to_index = {
            "w": 0,
            "xm": 0,
            "-100": 0,
            "e": 1,
            "xp": 1,
            "100": 1,
            "s": 2,
            "ym": 2,
            "0-10": 2,
            "n": 3,
            "yp": 3,
            "010": 3,
            "b": 4,
            "zm": 4,
            "00-1": 4,
            "t": 5,
            "zp": 5,
            "001": 5,
        }
        index_to_vertex = [
            (0, 4, 7, 3),
            (1, 2, 6, 5),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (0, 3, 2, 1),
            (4, 5, 6, 7),
        ]
        index_to_defaultsuffix = [
            "f-{}-w",
            "f-{}-n",
            "f-{}-s",
            "f-{}-n",
            "f-{}-b",
            "f-{}-t",
        ]

        if isinstance(index, str):
            index = kw_to_index[index]

        vnames = tuple([self.vnames[i] for i in index_to_vertex[index]])
        if name is None:
            name = index_to_defaultsuffix[index].format(self.name)
        return Face(vnames, name)


class ArcEdge:
    def __init__(self, vnames, name, interVertex):
        """Initialize ArcEdge instance
        vnames is the vertex names in order descrived in
          http://www.openfoam.org/docs/user/mesh-description.php
        # two vertices is needed for Arc
        cells is number of cells devied into in each direction
        name is the uniq name of the block
        grading is grading method.
        """
        self.vnames = vnames
        self.name = name
        self.interVertex = interVertex

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        comment = " ".join(self.vnames)
        # raise BaseException()
        return (
            "arc {0:s} ({1.x:18.15g} {1.y:18.15g} {1.z:18.15g}) "
            "// {2:s} ({3:s})".format(index, self.interVertex, self.name, comment)
        )


class SplineEdge:
    def __init__(self, vnames, name, points):
        """Initialize SplineEdge instance
        vnames is the vertex names in order descrived in
          http://www.openfoam.org/docs/user/mesh-description.php
        # two vertices is needed for Spline
        """
        self.vnames = vnames
        self.name = name
        self.points = points

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        vcom = " ".join(self.vnames)  # for comment

        tmp = []
        tmp.append(
            "spline {:s}                      "
            "// {:s} ({:s})".format(index, self.name, vcom)
        )
        tmp.append("    (")

        for p in self.points:
            tmp.append("         " + p.format())
        tmp.append(")")
        return "\n".join(tmp)


class Boundary:
    def __init__(self, type_, name, faces=[]):
        """initialize boundary
        type_ is type keyword (wall, patch, empty, ..)
        name is nave of boundary emelment
        faces is faces which are applied with this boundary conditions
        """
        self.type_ = type_
        self.name = name
        self.faces = faces

    def add_face(self, face):
        """add face instance
        face is a Face instance (not name) to be added
        """
        self.faces.append(face)

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        tmp = [self.name]
        tmp.append("{")
        tmp.append(f"    type {self.type_};")
        tmp.append("    faces")
        tmp.append("    (")
        for f in self.faces:
            s = f.format(vertices)
            tmp.append(f"        {s}")
        tmp.append("    );")
        tmp.append("}")
        return "\n".join(tmp)


class BlockMeshDict:
    def __init__(self):
        self.convert_to_meters = 1.0
        self.vertices = {}  # mapping of uniq name to Vertex object
        self.blocks = {}
        self.edges = {}
        self.boundaries = {}

    def set_metric(self, metric):
        """set self.comvert_to_meters by word"""
        metricsym_to_conversion = {
            "km": 1000,
            "m": 1,
            "cm": 0.01,
            "mm": 0.001,
            "um": 1e-6,
            "nm": 1e-9,
            "A": 1e-10,
            "Angstrom": 1e-10,
        }
        self.convert_to_meters = metricsym_to_conversion[metric]

    def add_vertex(self, x, y, z, name):
        """add vertex by coordinate and uniq name
        x y z is coordinates of vertex
        name is uniq name to refer the vertex
        returns Vertex object whici is added.
        """
        self.vertices[name] = Vertex(x, y, z, name)
        return self.vertices[name]

    def del_vertex(self, name):
        """del name key from self.vertices"""
        del self.vertices[name]

    def reduce_vertex(self, name1, *names):
        """treat name1, name2, ... as same point.

        name2.alias, name3.alias, ... are merged with name1.alias
        the key name2, name3, ... in self.vertices are kept and mapped to
        same Vertex instance as name1
        """
        v = self.vertices[name1]
        for n in names:
            w = self.vertices[n]
            v.alias.update(w.alias)
            # replace mapping from n w by to v
            self.vertices[n] = v

    def merge_vertices(self):
        """call reduce_vertex on all vertices with identical values."""

        # groupby expects sorted data
        sorted_vertices = sorted(
            list(self.vertices.items()), key=lambda v: hash(v[1])
        )
        groups = []
        for k, g in groupby(sorted_vertices, lambda v: hash(v[1])):
            groups.append(list(g))
        for group in groups:
            if len(group) == 1:
                continue
            names = [v[0] for v in group]
            self.reduce_vertex(*names)

    def add_hexblock(self, vnames, cells, name, grading=SimpleGrading(1, 1, 1)):
        b = HexBlock(vnames, cells, name, grading)
        self.blocks[name] = b
        return b

    def add_arcedge(self, vnames, name, interVertex):
        e = ArcEdge(vnames, name, interVertex)
        self.edges[name] = e
        return e

    def add_splineedge(self, vnames, name, points):
        e = SplineEdge(vnames, name, points)
        self.edges[name] = e
        return e

    def add_boundary(self, type_, name, faces=[]):
        b = Boundary(type_, name, faces)
        self.boundaries[name] = b
        return b

    def assign_vertexid(self, sort=True):
        """1. create list of Vertex which are referred by blocks only.
        2. sort vertex according to (x, y, z)
        3. assign sequence number for each Vertex
        4. sorted list is saved as self.valid_vertices
        """

        # gather 'uniq' names which are referred by blocks
        validvnames = set()
        # TODO: change this variable name (valid_vertices)
        self.valid_vertices = []
        for b in self.blocks.values():
            for n in b.vnames:
                v = self.vertices[n]
                if v.name not in validvnames:
                    validvnames.update([v.name])
                    self.valid_vertices.append(v)
        # TODO: it should be possible to skip this sort
        if sort:
            self.valid_vertices = sorted(self.valid_vertices)
        for i, v in enumerate(self.valid_vertices):
            v.index = i

    def format_vertices_section(self):
        """format vertices section.
        assign_vertexid() should be called before this method, because
        self.valid_vetices should be available and member self.valid_vertices
        should have valid index.
        """
        tmp = ["vertices\n("]
        for v in self.valid_vertices:
            tmp.append("    " + v.format())
        tmp.append(");")
        return "\n".join(tmp)

    def format_blocks_section(self):
        """format blocks section.
        assign_vertexid() should be called before this method, because
        vertices refered by blocks should have valid index.
        """
        tmp = ["blocks\n("]
        for b in self.blocks.values():
            tmp.append("    " + b.format(self.vertices))
        tmp.append(");")
        return "\n".join(tmp)

    def format_edges_section(self):
        """format edges section.
        assign_vertexid() should be called before this method, because
        vertices refered by blocks should have valid index.
        """

        tmp = ["edges\n("]
        for e in self.edges.values():
            tmp.append("    " + e.format(self.vertices))
        tmp.append(");")
        return "\n".join(tmp)

    def format_boundary_section(self):
        """format boundary section.
        assign_vertexid() should be called before this method, because
        vertices refered by faces should have valid index.
        """

        tmp = ["boundary\n("]
        for b in self.boundaries.values():
            # format Boundary instance and add indent
            indent = " " * 4
            s = b.format(self.vertices).replace("\n", "\n" + indent)
            tmp.append(indent + s)
        tmp.append(");")
        return "\n".join(tmp)

    def format_mergepatchpairs_section(self):
        return """\
mergePatchPairs
(
);"""

    def format(self):
        template = Template(
            r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2206                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   $metricconvert;

$vertices

$blocks

$edges

$boundary

$mergepatchpairs

// ************************************************************************* //
"""
        )

        return template.substitute(
            metricconvert=str(self.convert_to_meters),
            vertices=self.format_vertices_section(),
            edges=self.format_edges_section(),
            blocks=self.format_blocks_section(),
            boundary=self.format_boundary_section(),
            mergepatchpairs=self.format_mergepatchpairs_section(),
        )
