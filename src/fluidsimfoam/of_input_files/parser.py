from pathlib import Path

from lark import Lark, Token, Transformer

from .ast import OFInputFile

here = Path(__file__).absolute().parent

grammar = (here / "grammar.lark").read_text()

parser = Lark(grammar, start="value", lexer="basic")


def parse(text):
    tree = parser.parse(text)
    return OFTransformer().transform(tree)


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

    def file(self, tree):
        return OFInputFile(info, children)
