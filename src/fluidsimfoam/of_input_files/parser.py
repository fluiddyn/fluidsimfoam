from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from lark import Lark, Token, Transformer

from .ast import OFInputFile, VariableAssignment

here = Path(__file__).absolute().parent

grammar = (here / "grammar.lark").read_text()

parser = Lark(grammar, start="value", lexer="basic")


def parse(text):
    tree = parser.parse(text)
    return OFTransformer().transform(tree)


def dump(tree):
    NotImplementedError()


def filter_no_newlines(items):
    return [item for item in items if item is not None]


@dataclass
class Assignment:
    name: str
    value: object


class OFTransformer(Transformer):
    def number(self, n):
        (n,) = n
        n = str(n)
        try:
            return int(n)
        except ValueError:
            return float(n)

    def list(self, items):
        return [
            item
            for item in items
            if not (isinstance(item, Token) and item.type == "NEWLINE")
        ]

    def CNAME(self, token):
        return token.value

    def file(self, nodes):
        print(f"in file: ", nodes)

        # raise BaseException()

        foamfile_assignment = nodes.pop(0)
        if foamfile_assignment.name != "FoamFile":
            raise ValueError

        return OFInputFile(
            foamfile_assignment.value, {node.name: node.value for node in nodes}
        )

    def keyword(self, nodes):
        return nodes[0]

    def dataentry(self, nodes):
        return nodes[0]

    def var_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        if len(nodes) == 1:
            value = nodes[0]
        else:
            value = " ".join(nodes)
        return VariableAssignment(name, value)

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
        return Assignment(name, {node.name: node.value for node in nodes})

    def ESCAPED_STRING(self, token):
        return token.value[1:-1]

    def string(self, nodes):
        return nodes[0]

    def dimension_set(self, items):
        return [
            item
            for item in items
            if not (isinstance(item, Token) and item.type == "NEWLINE")
        ]

    def dimension_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        if len(nodes) == 3:
            nodes.pop(0)
        return Assignment(name, nodes)

    def directive(self, nodes):
        return nodes[0]

    def macro(self, nodes):
        return nodes[0]

    def macro_assignment(self, nodes):
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def directive_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def block(self, nodes):
        return nodes[0]

    def blocks_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def boundary_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        return Assignment(name, nodes[0])
