from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from lark import Lark, Token, Transformer

from .ast import OFInputFile

here = Path(__file__).absolute().parent

grammar = (here / "grammar.lark").read_text()

parser = Lark(grammar, start="value", lexer="basic")


def parse(text):
    tree = parser.parse(text)
    return OFTransformer().transform(tree)


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
        foamfile_assignment = nodes.pop(0)
        if foamfile_assignment.name != "FoamFile":
            raise ValueError
        d = {node.name: node.value for node in nodes}
        return OFInputFile(foamfile_assignment.value, d)

    def keyword(self, nodes):
        return nodes[0]

    def dataentry(self, nodes):
        return nodes[0]

    def var_assignment(self, nodes):
        nodes = [node for node in nodes if node is not None]
        name = nodes.pop(0)
        return Assignment(name, nodes[0])

    def assignment(self, nodes):
        return nodes[0]

    def NEWLINE(self, nodes):
        return None

    def dict_assignment(self, nodes):
        nodes = filter_no_newlines(nodes)
        name = nodes.pop(0)
        d = {node.name: node.value for node in nodes}
        return Assignment(name, d)

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
        return Assignment(name, nodes[-1])
