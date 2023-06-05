class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def format(self):
        return f"( {self.x:18.15g} {self.y:18.15g} {self.z:18.15g} )"


class ArcEdge:
    def __init__(self, vnames, name, inter_vertex):
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
        self.inter_vertex = inter_vertex

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        comment = " ".join(self.vnames)
        v = self.inter_vertex
        return (
            f"arc {index} ({v.x:18.15g} {v.y:18.15g} {v.z:18.15g}) "
            f"// {self.name} ({comment})"
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
        if points and not isinstance(points[0], Point):
            points = [Point(x, y, z) for x, y, z in points]
        self.points = points

    def format(self, vertices):
        """Format instance to dump
        vertices is dict of name to Vertex
        """
        index = " ".join(str(vertices[vn].index) for vn in self.vnames)
        comment = " ".join(self.vnames)
        tmp = []
        tmp.append(
            f"spline {index}                      // {self.name} ({comment})"
        )
        tmp.append("    (")
        for p in self.points:
            tmp.append("         " + p.format())
        tmp.append(")")
        return "\n".join(tmp)
