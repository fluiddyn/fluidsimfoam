from dataclasses import dataclass


class Node:
    pass


class OFInputFile(Node):
    def __init__(self, info, children):
        self.info = info
        self.children = children

    def __repr__(self):
        s = super().__repr__()
        return s

    def dump(self):
        s = ""
        return s


class VariableAssignment(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        s = super().__repr__()
        return s

    def dump(self):
        s = str(self.name) + " " + str(self.value) + ";"
        return s


@dataclass
class Value(Node):
    def __init__(self, value, name=None, dimension=None):
        self.value = value
        self.name = name

        s_dim = ""

        if dimension is not None:
            symbols = ["kg", "m", "s", "K", "kmol", "A", "cd"]

            if len(dimension) != len(symbols):
                raise BaseException()
                raise ValueError("len(dimension) != len(symbols)")

            numerator = []
            denominator = []
            for i, d in enumerate(dimension):
                if d > 0:
                    if d == 1:
                        numerator.append(symbols[i])
                    else:
                        numerator.append(symbols[i] + "^" + str(d))
                elif d < 0:
                    if d == -1:
                        denominator.append(symbols[i])
                    else:
                        denominator.append(symbols[i] + "^" + str(-d))

            if numerator:
                s_dim += "".join(numerator)
                if denominator:
                    s_dim += "/" + "".join(denominator)
            else:
                if denominator:
                    s_dim += "1/" + "".join(denominator)

        self.dimension = s_dim

    # def __repr__(self):
    #     ...
