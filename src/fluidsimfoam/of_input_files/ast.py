import re
from dataclasses import dataclass

symbols = ["kg", "m", "s", "K", "kmol", "A", "cd"]


def str2foam_units(units):
    result = [0] * 7
    sign = 1
    while units:
        try:
            index = re.search(r"[/.]", units).start()
        except AttributeError:
            unit_all = units
            units = ""
            next_oper = "."
        else:
            next_oper = units[index]
            assert next_oper in "/."
            unit_all = units[:index]

        units = units[index + 1 :]
        if "^" in unit_all:
            unit_name, unit_value = unit_all.split("^")
            unit_value = int(unit_value)
        else:
            unit_name, unit_value = unit_all, 1
        if unit_name != "1":
            unit_index = symbols.index(unit_name)
            result[unit_index] = sign * unit_value
        sign = 1 if next_oper == "." else -1
    return result


def foam_units2str(of_units):
    if len(of_units) != len(symbols):
        raise ValueError("len(of_units) != len(symbols)")
    result = []
    for symbol, exponent in zip(symbols, of_units):
        if exponent == 0:
            continue
        operator = "." if exponent > 0 else "/"
        if abs(exponent) == 1:
            result.append(f"{operator}{symbol}")
        else:
            result.append(f"{operator}{symbol}^{abs(exponent)}")
    result = "".join(result)
    if result.startswith("."):
        result = result[1:]
    elif result.startswith("/"):
        result = "1" + result
    return result


class Node:
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class FoamInputFile(Node):
    def __init__(self, info, children):
        self.info = info
        self.children = children

    def __repr__(self):
        tmp = ["InputFile(\n"]
        if self.info is not None:
            tmp.append(f"info={self.info},\n")
        tmp.append(f"children={self.children}\n)")
        return "".join(tmp)

    def dump(self):
        tmp = []
        if self.info is not None:
            tmp.append("FoamFile" + "\n{")
            for key, node in self.info.items():
                s = (12 - len(key)) * " "
                tmp.append(f"    {key}{s}{node};")
            tmp.append("}\n")
        for key, node in self.children.items():
            if hasattr(node, "dump"):
                tmp.append(node.dump())
            elif hasattr(node, "dump_without_assignment"):
                tmp.append(f"{key}  {node.dump_without_assignment()};")
            else:
                tmp.append(f"{key}  {node};")
        return "\n".join(tmp)


@dataclass
class Assignment:
    name: str
    value: object

    def dump(self, indent=0):
        if hasattr(self.value, "dump"):
            return self.value.dump(indent)
        else:
            return indent * " " + f"{self.name}  {self.value};"


class VariableAssignment(Assignment):
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

        if isinstance(dimension, (list, tuple)):
            if len(dimension) != len(symbols):
                raise ValueError("len(dimension) != len(symbols)")
            dimension = foam_units2str(dimension)
        self.dimension = dimension

    def __repr__(self):
        if self.dimension is not None and self.name is not None:
            return f'Value({self.value}, name="{self.name}", dimension="{self.dimension}")'
        elif self.dimension is None and self.name is not None:
            return f'Value({self.value}, name="{self.name}")'
        elif self.dimension is not None and self.name is None:
            return f'Value({self.value}, dimension="{self.dimension}")'
        else:
            return f"Value({self.value})"

    def dump_without_assignment(self, indent=0):
        if self.dimension is not None:
            dimension_list = str2foam_units(self.dimension)
            dimension_dumped = " ".join(str(number) for number in dimension_list)
        if self.dimension is not None and self.name is not None:
            return f"{self.name} [{dimension_dumped}] {self.value}"
        elif self.dimension is None and self.name is not None:
            return f"{self.name} {self.value}"
        elif self.dimension is not None and self.name is None:
            return f"[{dimension_dumped}] {self.value}"
        else:
            return f"{self.value};"


class DimensionSet(list, Node):
    def __init__(self, of_units):
        if len(of_units) != len(symbols):
            raise ValueError("len(dimension) != len(symbols)")

        if not all(isinstance(elem, int) for elem in of_units):
            raise ValueError("Bad {of_units = }")

        super().__init__(of_units)

    def __repr__(self):
        return foam_units2str(self)

    def dump_without_assignment(self, indent=0):
        return "[" + " ".join(str(number) for number in self) + "]"


class Dict(dict, Node):
    def __init__(self, data, name=None):
        self._name = name
        super().__init__(**data)

    def get_name(self):
        return self._name

    def __repr__(self):
        return super().__repr__()

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        if self._name is not None:
            tmp.append(indentation + self._name + f"\n{indentation}" + "{")
        max_length = max(len(key) for key in self)
        default_space = 4
        num_spaces = max_length + default_space
        for key, node in self.items():
            if hasattr(node, "dump"):
                tmp.append(node.dump(indent + 4))
            else:
                s = (num_spaces - len(key)) * " "
                tmp.append(indentation + f"    {key}{s}{node};")
        tmp.append(indentation + "}\n")
        return "\n".join(tmp)


class List(list, Node):
    """Represents an OpenFoam list"""

    def __init__(self, iterable=None, name=None):
        self._name = name
        super().__init__(iterable)

    def get_name(self):
        return self._name

    def __repr__(self):
        return super().__repr__()

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        if self._name is not None:
            tmp.append(
                "\n" + indentation + self._name + f"\n{indentation}" + "(\n"
            )
            for item in self:
                if hasattr(item, "dump"):
                    tmp.append(item.dump(indent + 4))
                else:
                    tmp.append(indentation + f"    {item}")
            tmp.append(indentation + ");\n")
            return "".join(tmp)
        elif self._name is None:
            for item in self:
                if hasattr(item, "dump"):
                    tmp.append(item.dump(indent + 4))
                else:
                    tmp.append(f"{item}")
            # tmp.append(")\n")
            return indentation + "(" + " ".join(tmp) + ")\n"


class Code(dict, Node):
    def __init__(self, data, name=None):
        self._name = name
        super().__init__(**data)

    def get_name(self):
        return self._name

    def __repr__(self):
        return super().__repr__()

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        if self._name is not None:
            tmp.append(indentation + self._name + f"\n{indentation}" + "#{")
        max_length = max(len(key) for key in self)
        default_space = 4
        num_spaces = max_length + default_space
        for key, node in self.items():
            if hasattr(node, "dump"):
                tmp.append(node.dump(indent + 4))
            else:
                s = (num_spaces - len(key)) * " "
                tmp.append(indentation + f"    {key}{s}{node};")
        tmp.append(indentation + "#};\n")
        return "\n".join(tmp)
