"""Utility to create blockMeshDict files

Taken from https://github.com/takaakiaoki/ofblockmeshdicthelper (Git commit
58589f1) and modified as follow:

- ``pyupgrade __init__.py --py39-plus``
- tested (100% coverage) and reproducible (sets sorted)
- refactor
- support for cyclic boundaries

"""

from itertools import groupby
from string import Template

from .. import DEFAULT_HEADER
from .edges import ArcEdge, SplineEdge
from .grading import EdgeGrading, Grading, SimpleGrading, SimpleGradingElement

__all__ = [
    "Grading",
    "SimpleGradingElement",
    "SimpleGrading",
    "EdgeGrading",
    "ArcEdge",
    "SplineEdge",
]


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
        comment = f"{self.index} {self.name}"
        if len(self.alias) > 1:
            comment += " : " + " ".join(sorted(self.alias))
        return (
            f"( {self.x:18.15g} {self.y:18.15g} {self.z:18.15g} )  // {comment}"
        )

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


class Boundary:
    def __init__(self, type_, name, faces=None, neighbour=None):
        """initialize boundary
        type_ is type keyword (wall, patch, empty, ..)
        name is nave of boundary emelment
        faces is faces which are applied with this boundary conditions
        """
        self.type_ = type_
        self.name = name
        if faces is None:
            faces = []
        elif isinstance(faces, Face):
            faces = [faces]
        self.faces = faces
        self.neighbour = neighbour

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
        if self.neighbour is None:
            tmp.append("{\n" + f"    type {self.type_};\n    faces\n    (")
        else:
            tmp.append(
                "{\n"
                + f"    type {self.type_};\n    neighbourPatch  {self.neighbour};\n    faces\n    ("
            )
        for f in self.faces:
            tmp.append(f"        {f.format(vertices)}")
        tmp.append("    );\n}")
        return "\n".join(tmp)


class BlockMeshDict:
    def __init__(self):
        self.convert_to_meters = 1.0
        self.vertices = {}  # mapping of uniq name to Vertex object
        self.blocks = {}
        self.edges = {}
        self.boundaries = {}
        self._vertices_in_blockmesh = None

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

    def set_scale(self, scale):
        self.convert_to_meters = scale

    def add_vertex(self, x, y=None, z=None, name=None):
        """add vertex by coordinate and uniq name
        x y z is coordinates of vertex
        name is uniq name to refer the vertex
        returns Vertex object whici is added.
        """
        if isinstance(x, Vertex):
            if any(arg is not None for arg in (y, z, name)):
                raise ValueError(
                    "x is a Vertex and "
                    "`any(arg is not None for arg in (y, z, name))`"
                )
            vertex = x
            name = vertex.name
        else:
            vertex = Vertex(x, y, z, name)
        self.vertices[name] = vertex
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

    def add_arcedge(self, vnames, name, inter_vertex):
        e = ArcEdge(vnames, name, inter_vertex)
        self.edges[name] = e
        return e

    def add_splineedge(self, vnames, name, points):
        e = SplineEdge(vnames, name, points)
        self.edges[name] = e
        return e

    def add_boundary(self, type_, name, faces=None, neighbour=None):
        b = Boundary(type_, name, faces, neighbour)
        self.boundaries[name] = b
        return b

    def add_cyclic_boundaries(self, name0, name1, faces0, faces1):
        b0 = self.add_boundary("cyclic", name0, faces0, neighbour=name1)
        b1 = self.add_boundary("cyclic", name1, faces1, neighbour=name0)
        return b0, b1

    def assign_vertexid(self, sort=True):
        """1. create list of Vertex which are referred by blocks only.
        2. sort vertex according to (x, y, z)
        3. assign sequence number for each Vertex
        4. sorted list is saved as self._vertices_in_blockmesh
        """
        # gather 'uniq' names which are referred by blocks
        vnames_kept = set()
        self._vertices_in_blockmesh = []
        for b in self.blocks.values():
            for n in b.vnames:
                v = self.vertices[n]
                if v.name not in vnames_kept:
                    vnames_kept.add(v.name)
                    self._vertices_in_blockmesh.append(v)
        if sort:
            self._vertices_in_blockmesh = sorted(self._vertices_in_blockmesh)
        for i, v in enumerate(self._vertices_in_blockmesh):
            v.index = i

    def format_vertices_section(self):
        """format vertices section.
        assign_vertexid() should be called before this method, because
        self._vertices_in_blockmesh should be available and
        members of self._vertices_in_blockmesh should have valid index.
        """
        tmp = ["vertices\n("]
        for v in self._vertices_in_blockmesh:
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

    def format(self, header=DEFAULT_HEADER, sort_vortices=True):
        self.assign_vertexid(sort=sort_vortices)
        template = Template(
            r"""$header
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
            header=header,
            metricconvert=str(self.convert_to_meters),
            vertices=self.format_vertices_section(),
            edges=self.format_edges_section(),
            blocks=self.format_blocks_section(),
            boundary=self.format_boundary_section(),
            mergepatchpairs=self.format_mergepatchpairs_section(),
        )
