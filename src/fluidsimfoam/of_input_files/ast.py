import re
from dataclasses import dataclass

symbols = ["kg", "m", "s", "K", "kmol", "A", "cd"]


def str2of_units(units):
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


def of_units2str(of_units):
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

        if isinstance(dimension, (list, tuple)):
            if len(dimension) != len(symbols):
                raise ValueError("len(dimension) != len(symbols)")
            dimension = of_units2str(dimension)
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

    def dump(self):
        if self.dimension is not None:
            dimension_list = str2of_units(self.dimension)
            dimension_dumped = " ".join(str(number) for number in dimension_list)
        if self.dimension is not None and self.name is not None:
            return f"{self.name} [{dimension_dumped}] {self.value};"
        elif self.dimension is None and self.name is not None:
            return f"{self.name} {self.value};"
        elif self.dimension is not None and self.name is None:
            return f"[{dimension_dumped}] {self.value};"
        else:
            return f"{self.value};"
