"""Parser for OpenFOAM input files"""

from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Token, Transformer
from lark.exceptions import LarkError

from .ast import (
    Assignment,
    Code,
    CodeStream,
    Dict,
    DimensionSet,
    Directive,
    FoamInputFile,
    List,
    Name,
    Value,
    VariableAssignment,
)

here = Path(__file__).absolute().parent

grammar = (here / "grammar.lark").read_text()
grammar_advanced = (here / "grammar_advanced.lark").read_text()

lark_parser = Lark(grammar, start="value", lexer="basic")
lark_parser_advanced = Lark(grammar_advanced, start="value", lexer="basic")

parsers = {"simple": lark_parser, "advanced": lark_parser_advanced}


@dataclass
class ListInfo:
    name: str
    info: str = None
    dtype: str = None
    size: int = None


def parse(text, grammar=None):
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    if not text.endswith("\n"):
        text += "\n"

    if grammar is None:
        try:
            tree = lark_parser.parse(text)
        except LarkError:
            tree = lark_parser_advanced.parse(text)
    else:
        tree = parsers[grammar].parse(text)

    return FoamTransformer().transform(tree)


def dump(tree):
    return tree.dump()


def filter_no_newlines(items):
    return [item for item in items if item is not None]


def _convert_to_number(number):
    number = str(number)
    try:
        return int(number)
    except ValueError:
        return float(number)


class FoamTransformer(Transformer):
    def SIGNED_NUMBER(self, token):
        return _convert_to_number(token)

    def CNAME(self, token):
        return token.value

    def NEWLINE(self, nodes):
        return None

    def ESCAPED_STRING(self, token):
        return token.value

    def DOUBLE_NAME(self, token):
        return token.value

    def TRIPLE_NAME(self, token):
        return token.value

    def EQKEY(self, token):
        return token.value

    def MACRO(self, token):
        return token.value

    def dimension_set(self, items):
        return DimensionSet(
            [
                item
                for item in items
                if not (isinstance(item, Token) and item.type == "NEWLINE")
            ]
        )

    def directive(self, nodes):
        if len(nodes) != 1:
            raise RuntimeError
        return str(nodes[0])

    def list(self, items):
        return List(
            [
                item
                for item in items
                if not (isinstance(item, Token) and item.type == "NEWLINE")
                and item is not None
            ]
        )

    def file(self, nodes):
        first_assignment = nodes[0]
        if first_assignment.name == "FoamFile":
            info_dict = first_assignment.value
            nodes = nodes[1:]
        else:
            info_dict = None

        for node in nodes:
            if isinstance(node.value, List):
                node.value.add_name(node.name)

        return FoamInputFile(info_dict, {node.name: node.value for node in nodes})

    def var_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        dimension_set = None
        name_in_value = None
        name = nodes.pop(0)
        if len(nodes) == 1:
            value = nodes[0]
        else:
            try:
                index_dimension = [
                    isinstance(elem, DimensionSet) for elem in nodes
                ].index(True)
            except ValueError:
                dimension_set = None
            else:
                dimension_set = nodes.pop(index_dimension)

            name_in_value = None
            if all([isinstance(elem, str) for elem in nodes]):
                last_value = " ".join(nodes)
            else:
                last_value = nodes.pop(-1)
                if not all(isinstance(node, str) for node in nodes):
                    nodes = [str(node) for node in nodes]
                if nodes:
                    name_in_value = " ".join(nodes)
                if isinstance(last_value, List):
                    last_value._name = name_in_value

            if (name_in_value is None and dimension_set is None) or isinstance(
                last_value, List
            ):
                value = last_value
            else:
                value = Value(
                    last_value, name=name_in_value, dimension=dimension_set
                )
        return VariableAssignment(name, value)

    def dict_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)
        directive = None

        if len(nodes) == 1:
            name = nodes.pop(0)
            return Assignment(name, Dict(data={}, name=name))

        nodes_str = []
        for node in nodes:
            if isinstance(node, str) and node.startswith("#"):
                # like #codeStream
                directive = nodes.pop(1)
                break
        if isinstance(nodes[0], list):
            name = "(" + " ".join(nodes.pop(0)) + ")"
        else:
            name = nodes.pop(0)
        if nodes_str:
            name += " " + " ".join(nodes_str)

        nodes_assign = [
            node
            for node in nodes
            if hasattr(node, "name") and hasattr(node, "value")
        ]

        for node in nodes_assign:
            if isinstance(node.value, List):
                node.value.add_name(node.name)

        if directive is not None and directive == "#codeStream":
            cls = CodeStream
        else:
            cls = Dict

        return Assignment(
            name,
            cls(
                data={node.name: node.value for node in nodes_assign},
                name=name,
                directive=directive,
            ),
        )

    def isolated_list(self, nodes):
        nodes = filter_no_newlines(nodes)
        if len(nodes) != 1:
            raise NotImplementedError(nodes)
        name = None
        return Assignment(name, nodes[0])

    def list_info(self, nodes):
        nodes = filter_no_newlines(nodes)

        dtype = None
        for inode, node in enumerate(nodes):
            if isinstance(node, Token) and node.type == "LIST_TYPE":
                dtype = str(node)[5:-1]
                break
        if dtype is not None:
            nodes.pop(inode)

        size = None
        if len(nodes) > 1 and isinstance(nodes[-1], int):
            size = nodes.pop(-1)

        name = nodes.pop(0)

        info = None
        if nodes:
            info = " ".join(nodes)

        return ListInfo(name=name, info=info, dtype=dtype, size=size)

    def list_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)

        list_info, the_list = nodes
        assert isinstance(list_info, ListInfo)

        name = list_info.name
        name_internal = name

        if list_info.info is not None:
            name_internal += " " + list_info.info

        if list_info.dtype is not None:
            name_internal += f"\nList<{list_info.dtype}>"

        if list_info.size is not None:
            name_internal += f"\n{list_info.size}"

        if isinstance(name, int):
            name = str(name)
        if isinstance(name_internal, int):
            name_internal = str(name_internal)

        the_list._name = name_internal
        return Assignment(name, the_list)

    def dimension_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)

        if len(nodes) == 3:
            return Assignment(name, Value(nodes[-1], nodes[0], nodes[-2]))
        elif len(nodes) == 2:
            return Assignment(name, Value(nodes[-1], dimension=nodes[-2]))
        else:
            raise RuntimeError(nodes)

    def macro_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        if len(nodes) != 1:
            raise NotImplementedError(nodes)
        name = nodes.pop(0)
        return Assignment(name, "")

    def equal_assign(self, nodes):
        nodes = [node for node in nodes if node is not None]
        if len(nodes) != 2:
            raise RuntimeError(nodes)
        value = nodes[1]
        if hasattr(value, "dump"):
            value = value.dump()
        return f"{nodes[0]}={value}"

    def directive_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        if len(nodes) == 2:
            directive, content = nodes
        else:
            directive = nodes.pop(0)
            function_name = nodes.pop(0)
            arguments = ", ".join(nodes)
            content = function_name + f"({arguments})"
        key = directive + " " + content
        return Assignment(key, Directive(directive, content))

    def code_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)
        directive = None
        if len(nodes) == 2:
            name, code = nodes
        elif len(nodes) == 3:
            name, directive, code = nodes
            if not directive.startswith("#"):
                raise NotImplementedError(nodes)
        else:
            raise NotImplementedError(nodes)
        code = str(code)
        if code.startswith("#{\n"):
            code = code.split("\n", 1)[-1]
            code = code.rsplit("\n", 1)[0]
        else:
            code = code[2:-3].strip()
        return Assignment(name, Code(name, code, directive=directive))

    def special_directives(self, token):
        token = filter_no_newlines(token)
        return Name(token[0].value + "\n")
