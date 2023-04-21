import re
from dataclasses import dataclass
from textwrap import dedent

from inflection import underscore

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


def foam_units2str(foam_units):
    result = []
    for symbol, exponent in zip(symbols, foam_units):
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
    def __init__(self, info, children, header=None, comments=None):
        self.info = info
        self.children = children
        self.header = header
        self.comments = comments

    def __repr__(self):
        tmp = ["InputFile(\n"]
        if self.info is not None:
            tmp.append(f"info={self.info},\n")
        tmp.append(f"children={self.children}\n)")
        return "".join(tmp)

    def dump(self):
        tmp = []
        if self.info is not None:
            tmp1 = ["FoamFile\n{"]
            for key, node in self.info.items():
                s = (12 - len(key)) * " "
                tmp1.append(f"    {key}{s}{node};")
            tmp1.append("}")
            tmp.append("\n".join(tmp1))
        for key, node in self.children.items():
            if hasattr(node, "dump"):
                code_node = node.dump()
                # special for isolated list
                if key is None and isinstance(node, List):
                    code_node += ";"
            elif hasattr(node, "dump_without_assignment"):
                code_node = f"{key}  {node.dump_without_assignment()};"
            elif node is None:
                code_node = f"{key}"
            else:
                code_node = f"{key:14s}  {node};"
            if self.comments is not None and key in self.comments:
                comment = "// " + self.comments[key].replace("\n", "\n// ")
                code_node = comment + "\n" + code_node
            tmp.append(code_node)
        result = "\n\n".join(tmp)
        if self.header is not None:
            result = self.header + "\n" + result
        if result[-1] != "\n":
            result += "\n"
        return result


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

    def dump(self, indent=0):
        if hasattr(self.value, "dump"):
            return indent * " " + f"{self.name}  {self.value.dump(indent)};"
        else:
            return indent * " " + f"{self.name}  {self.value};"


@dataclass
class Value(Node):
    def __init__(self, value, name=None, dimension=None):
        self.value = value
        self.name = name
        if isinstance(dimension, (list, tuple)):
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
            return f"{self.value}"


class DimensionSet(list, Node):
    def __init__(self, foam_units):
        if not all(isinstance(elem, int) for elem in foam_units):
            raise ValueError("Bad {foam_units = }")
        super().__init__(foam_units)

    def __repr__(self):
        return foam_units2str(self)

    def dump_without_assignment(self, indent=0):
        return "[" + " ".join(str(number) for number in self) + "]"


class Dict(dict, Node):
    def __init__(self, data, name=None, directive=None):
        self._name = name
        self._directive = directive
        super().__init__(**data)

    def get_name(self):
        return self._name

    def __repr__(self):
        return super().__repr__()

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        if self._name is not None:
            line = indentation + self._name
            if self._directive is not None:
                line += "  " + self._directive
            tmp.append(line + f"\n{indentation}" + "{")

        try:
            max_length = max(len(key) for key in self)
        except ValueError:
            max_length = 0

        default_space = 4
        num_spaces = max_length + default_space
        for key, node in self.items():
            if hasattr(node, "dump"):
                tmp.append(node.dump(indent + 4))
            elif hasattr(node, "dump_without_assignment"):
                tmp.append(f"    {key}  {node.dump_without_assignment()};")
            else:
                if node == "":
                    s = ""
                else:
                    s = (num_spaces - len(key)) * " "
                tmp.append(indentation + f"    {key}{s}{node};")
        tmp.append(indentation + "}")
        return "\n".join(tmp)


class List(list, Node):
    """Represents an OpenFoam list"""

    def __init__(self, iterable=None, name=None):
        self._name = name
        super().__init__(iterable)

    def get_name(self):
        return self._name

    def add_name(self, name):
        if self._name is None:
            self._name = name
        elif isinstance(self._name, str):
            if self._name != name:
                self._name = name + " " + self._name
        else:
            raise RuntimeError()

    def __repr__(self):
        return super().__repr__()

    def _make_list_strings(self, indent):
        return [self._dump_item(item, indent) for item in self]

    def _dump_item(self, item, indent=0):
        if hasattr(item, "dump"):
            return item.dump(indent)
        else:
            return indent * " " + str(item)

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        if self._name is None:
            tmp.extend(self._make_list_strings(indent=0))
            return indentation + "(" + " ".join(tmp) + ")"
        else:
            tmp.append(indentation + self._name + f"\n{indentation}" + "(")
            special_keys = {"blocks": "hex", "edges": "spline"}
            if self._name not in special_keys.keys():
                tmp.append("\n".join(self._make_list_strings(indent + 4)))
            elif self:
                special_key = special_keys[self._name]
                if not self[0] == special_key:
                    raise ValueError(self)
                lines = []
                items_line = None
                for item in self:
                    if item == special_key:
                        if items_line is not None:
                            lines.append(items_line)
                        items_line = [item]
                    else:
                        items_line.append(item)
                lines.append(items_line)
                lines = [
                    " ".join(self._dump_item(_item) for _item in items_line)
                    for items_line in lines
                ]
                tmp.extend((indent + 4) * " " + line for line in lines)
            tmp.append(indentation + ");")
            return "\n".join(tmp)


class CodeStream(Dict):
    """A dictionnary to store #codeStream"""


def _make_alias(name):
    def get(self):
        return self[name].code

    def set(_self, value):
        _self[name].code = value

    return property(get, set)


for _name in ("codeInclude", "codeOptions", "codeLibs", "code"):
    setattr(CodeStream, underscore(_name), _make_alias(_name))


class Code(Node):
    def __init__(self, name, code, directive=None):
        self.name = name
        self.code = dedent(code)
        self.directive = directive

    def __repr__(self):
        if self.directive is None:
            return f'Code("{self.code[:20]}[...]")'
        return f'Code("{self.code[:20]}[...]", directive={self.directive})'

    def dump(self, indent=0):
        tmp = []
        indentation = indent * " "
        indentation4 = (indent + 4) * " "
        start = indentation + self.name
        if self.directive is not None:
            start += " " + self.directive
        tmp.append(start + f"\n{indentation}" + "#{")
        for line in self.code.split("\n"):
            tmp.append(indentation4 + line)
        tmp.append(indentation + "#};\n")
        return "\n".join(tmp)


@dataclass
class Name(Node):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Name({self.name})"

    def dump(self, indent=0):
        return f"{self.name}"


class Directive(Node):
    def __init__(self, directive, content):
        self.directive = directive
        self.content = content

    def __repr__(self):
        return f"{self.directive}  {self.content}"

    def dump(self, indent=0):
        return indent * " " + f"{self.directive}  {self.content};"
