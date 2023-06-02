"""Abstract Syntax Trees for OpenFOAM input files"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from numbers import Number
from textwrap import dedent
from typing import Optional

import numpy as np
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


def _compute_spaces_to_align(data, max_length=20):
    try:
        max_length = min(
            max_length,
            max(
                len(key)
                for key, value in data.items()
                if value is not None and not isinstance(value, (Dict, List))
            ),
        )
    except ValueError:
        max_length = 0

    default_space = 4
    return max_length + default_space


class Node:
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class NodeLikePyDict(ABC):
    def init_from_py_objects(
        self,
        data: dict,
        dimensions: Optional[dict] = None,
        default_dimension=False,
        comments: Optional[dict] = None,
    ):
        if dimensions is None:
            dimensions = {}
        if comments is None:
            comments = {}
        for key, value in data.items():
            if isinstance(value, (type(None), str)):
                self.set_child(key, value)
            elif isinstance(value, (Number, list)):
                if default_dimension is False:
                    self.set_child(key, value)
                else:
                    dimension = dimensions.get(key, default_dimension)
                    if isinstance(value, list):
                        value = List(value)
                    self.set_value(key, value, dimension)
            elif isinstance(value, dict):
                dimensions_dict = dimensions.get(key, None)
                comments_dict = comments.get(key, None)
                obj = Dict({}, name=key, comments=comments_dict)
                obj.init_from_py_objects(
                    value,
                    dimensions=dimensions_dict,
                    default_dimension=default_dimension,
                    comments=comments_dict,
                )
                self._set_item(key, obj)
            else:
                raise NotImplementedError(type(value))

    def set_child(self, key, child):
        if (
            isinstance(child, list)
            and child
            and isinstance(child[0], list)
            and child[0]
            and all(isinstance(n, Number) for n in child[0])
        ):
            child = np.array(child)

        if isinstance(child, (type(None), str, Number, DimensionSet)):
            pass
        elif isinstance(child, dict):
            child = Dict(child, name=key)
        elif isinstance(child, list):
            child = List(child, name=key)
        elif isinstance(child, np.ndarray):
            shape = child.shape
            ndim = child.ndim
            child.tolist()
            dtype = None
            if ndim == 2:
                if shape[1] == 9:
                    dtype = "tensor"
                elif shape[1] == 3:
                    dtype = "vector"
                else:
                    raise NotImplementedError
                child = [List(sequence) for sequence in child]
            elif ndim == 1:
                dtype = "scalar"
            else:
                raise NotImplementedError
            child = List(child, name=key, dtype=dtype)
        elif isinstance(child, Node):
            pass
        else:
            raise NotImplementedError(type(child))
        self._set_item(key, child)

    def set_value(self, name, value, dimension=None):
        if isinstance(value, Number) or dimension is not None:
            value = Value(value, name, dimension=dimension)
        self._set_item(name, value)

    @abstractmethod
    def _set_item(self, key, value):
        """Set an item"""


class FoamInputFile(Node, NodeLikePyDict):
    def __init__(self, info, children=None, header=None, comments=None):
        self.info = info
        if children is None:
            children = {}
        self.children = children
        self.header = header
        self.comments = comments
        self.path = None

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

        num_spaces = _compute_spaces_to_align(self.children, max_length=14)
        for key, node in self.children.items():
            if hasattr(node, "dump"):
                code_node = node.dump()
                # special for isolated list
                if key is None and isinstance(node, List):
                    code_node += ";"
            elif node is None:
                code_node = f"{key}"
            else:
                if hasattr(node, "dump_without_assignment"):
                    node_dumped = node.dump_without_assignment()
                else:
                    node_dumped = node
                if node_dumped == "":
                    s = ""
                else:
                    s = max(2, (num_spaces - len(key))) * " "
                code_node = f"{key}{s}{node_dumped};"
            if self.comments is not None and key in self.comments:
                comment = self.comments[key]
                if isinstance(comment, str):
                    comment = "// " + comment.replace("\n", "\n// ")
                    code_node = comment + "\n" + code_node
            tmp.append(code_node)
        result = "\n\n".join(tmp)
        if self.header is not None:
            result = self.header + "\n" + result
        if result[-1] != "\n":
            result += "\n"
        return result

    def overwrite(self):
        if self.path is None:
            raise ValueError("self.path is None")
        with open(self.path, "w") as file:
            file.write(self.dump())

    def _set_item(self, key, value):
        self.children[key] = value

    def __setitem__(self, key, item):
        self.children[key] = item

    def __getitem__(self, key):
        return self.children[key]


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

        if isinstance(self.value, Node) and hasattr(self.value, "dump"):
            value_dumped = self.value.dump()
        else:
            value_dumped = str(self.value)

        if self.dimension is not None and self.name is not None:
            return f"{self.name} [{dimension_dumped}] {value_dumped}"
        elif self.dimension is None and self.name is not None:
            return f"{self.name} {value_dumped}"
        elif self.dimension is not None and self.name is None:
            return f"[{dimension_dumped}] {value_dumped}"
        else:
            return f"{value_dumped}"


class DimensionSet(list, Node):
    def __init__(self, foam_units):
        if isinstance(foam_units, str):
            foam_units = str2foam_units(foam_units)
        if not all(isinstance(elem, int) for elem in foam_units):
            raise ValueError("Bad {foam_units = }")
        super().__init__(foam_units)

    def __repr__(self):
        return foam_units2str(self)

    def dump_without_assignment(self, indent=0):
        return "[" + " ".join(str(number) for number in self) + "]"


class Dict(dict, Node, NodeLikePyDict):
    def __init__(self, data, name=None, directive=None, comments=None):
        self._name = name
        self._directive = directive
        self.comments = comments
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

        num_spaces = _compute_spaces_to_align(self)
        for key, node in self.items():
            if self.comments is not None and key in self.comments:
                comment = self.comments[key]
                if isinstance(comment, str):
                    tmp.append("    // " + comment.replace("\n", "\n    // "))

            if hasattr(node, "dump"):
                tmp.append(node.dump(indent + 4))
            elif node is None:
                tmp.append(indentation + f"    {key}")
            else:
                if hasattr(node, "dump_without_assignment"):
                    code_node = node.dump_without_assignment()
                else:
                    code_node = node
                if node == "":
                    s = ""
                else:
                    s = max(2, (num_spaces - len(key))) * " "
                tmp.append(indentation + f"    {key}{s}{code_node};")
        tmp.append(indentation + "}")

        # because OpenFOAM inconsistency
        if isinstance(self, CodeStream):
            tmp[-1] += ";"

        return "\n".join(tmp)

    def _set_item(self, key, value):
        self[key] = value


class List(list, Node):
    """Represents an OpenFoam list"""

    def __init__(self, iterable=None, name=None, dtype=None):
        self._name = name
        self._dtype = dtype
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
        if isinstance(item, (Node, Assignment)) and hasattr(item, "dump"):
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
            header = self._name
            if self._dtype is not None:
                header += (
                    f"   nonuniform List<{self._dtype}>\n"
                    f"{indentation}{len(self)}"
                )

            tmp.append(indentation + header + f"\n{indentation}" + "(")
            special_keyss = {
                "blocks": ("hex",),
                "edges": ("spline", "arc", "polyLine", "BSpline", "line"),
            }
            if self._name not in special_keyss.keys():
                tmp.append("\n".join(self._make_list_strings(indent + 4)))
            elif self:
                special_keys = special_keyss[self._name]
                if not self[0] in special_keys:
                    raise ValueError(self)
                special_key = self[0]
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
        tmp.append(indentation + "#};")
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
