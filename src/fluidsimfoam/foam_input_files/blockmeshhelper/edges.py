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
