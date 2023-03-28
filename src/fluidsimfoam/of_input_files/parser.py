from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from lark import Lark, Token, Transformer

from .ast import (
    Assignment,
    Code,
    Dict,
    DimensionSet,
    FoamInputFile,
    List,
    Value,
    VariableAssignment,
)

here = Path(__file__).absolute().parent

grammar = (here / "grammar.lark").read_text()

lark_parser = Lark(grammar, start="value", lexer="basic")


def parse(text):
    tree = lark_parser.parse(text)
    return OFTransformer().transform(tree)


def dump(tree):
    return tree.dump()


def filter_no_newlines(items):
    return [item for item in items if item is not None]


class OFTransformer(Transformer):
    def number(self, n):
        (n,) = n
        n = str(n)
        try:
            return int(n)
        except ValueError:
            return float(n)

    def list(self, items):
        return List(
            [
                item
                for item in items
                if not (isinstance(item, Token) and item.type == "NEWLINE")
                and item is not None
            ]
        )

    def CNAME(self, token):
        return token.value

    def file(self, nodes):
        first_assignment = nodes[0]
        if first_assignment.name == "FoamFile":
            info_dict = first_assignment.value
            nodes = nodes[1:]
        else:
            info_dict = None
        return FoamInputFile(info_dict, {node.name: node.value for node in nodes})

    def keyword(self, nodes):
        return nodes[0]

    def dataentry(self, nodes):
        return nodes[0]

    def var_assignment(self, nodes):
        try:
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
                    dimension_set = nodes.pop(index_dimension)

                    if len(nodes) == 2:
                        name_in_value, value = nodes

                    elif len(nodes) == 1:
                        value = nodes[0]
                    else:
                        raise NotImplementedError()
                    value = Value(
                        value, name=name_in_value, dimension=dimension_set
                    )
                except ValueError:
                    value = " ".join(nodes)

            return VariableAssignment(name, value)
        except Exception as err:
            raise BaseException()

    def multi_var(self, nodes):
        d = {
            self.var_assignment(node).name: self.var_assignment(node).value
            for node in nodes
        }
        return d

    def assignment(self, nodes):
        return nodes[0]

    def NEWLINE(self, nodes):
        return None

    def dict_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)
        name = nodes.pop(0)
        return Assignment(
            name, Dict(data={node.name: node.value for node in nodes}, name=name)
        )

    def list_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)
        name = nodes.pop(0)
        return Assignment(name, List(nodes, name=name))

    def ESCAPED_STRING(self, token):
        return token.value

    def string(self, nodes):
        return nodes[0]

    def dimension_set(self, items):
        return DimensionSet(
            [
                item
                for item in items
                if not (isinstance(item, Token) and item.type == "NEWLINE")
            ]
        )

    def dimension_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)

        if len(nodes) == 3:
            return Assignment(name, Value(nodes[-1], nodes[0], nodes[-2]))
        elif len(nodes) == 2:
            return Assignment(name, Value(nodes[-1], dimension=nodes[-2]))

    def macro(self, nodes):
        nodes[0] = "$" + nodes[0]
        return nodes[0]

    def macro_assignment(self, nodes):
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def directive(self, nodes):
        nodes[0] = "#" + nodes[0]
        return nodes[0]

    def directive_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def code(self, nodes):
        nodes = filter_no_newlines(nodes)
        name = nodes.pop(0)
        # raise BaseException()
        return Assignment(
            name, Code(data={node.name: node.value for node in nodes}, name=name)
        )
