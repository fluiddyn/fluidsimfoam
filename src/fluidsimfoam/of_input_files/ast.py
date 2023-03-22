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

    def __repr__(self):
        if self.dimension is not None:
            return f'Value({self.value}, name="{self.name}", dimension="{self.dimension}")'
        else:
            return f'Value({self.value}, name="{self.name}")'

    def dump(self):
        if self.dimension is not None:
            numerator = self.dimension.split("/")[0]
            denominator = self.dimension.split("/")[1]
            symbols = ["kg", "m", "s", "K", "kmol", "A", "cd"]
            dim = [0, 0, 0, 0, 0, 0, 0]

            for i, symb in enumerate(symbols):
                s = symb + "^"
                if s in numerator:
                    a = numerator.find(s)
                    dim[i] = int(numerator[a + len(symb) + 1])
                    numerator = numerator.replace(
                        s + numerator[a + len(symb) + 1], ""
                    )

                if s in denominator:
                    a = denominator.find(s)
                    dim[i] = -int(denominator[a + len(symb) + 1])
                    denominator = denominator.replace(
                        s + denominator[a + len(symb) + 1], ""
                    )

            for i, symb in reversed(list(enumerate(symbols))):
                if symb in numerator:
                    a = numerator.find(symb)
                    dim[i] = 1
                    numerator = numerator.replace(symb, "")

                if symb in denominator:
                    a = denominator.find(symb)
                    dim[i] = -1
                    denominator = denominator.replace(symb, "")

            dim = str(dim).replace(",", "")
            dim = dim.replace("[", "[ ")
            dim = dim.replace("]", " ]")

            return f"{self.name} {dim} {self.value};"
        else:
            return f"{self.name} {self.value};"
