from collections.abc import Iterable
from itertools import product


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
            f"({self.x.format()} {self.y.format()} {self.z.format()})"
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
