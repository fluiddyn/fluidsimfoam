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
