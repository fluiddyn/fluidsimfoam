from lark import Lark, Transformer, Token

grammar = r"""
    ?value: CNAME
          | dict_assignment
          | list
          | file
          | assignment
          | string
          | CPP_COMMENT
          | C_COMMENT
          | SIGNED_NUMBER      -> number
    string : ESCAPED_STRING
    keyword : CNAME
    dataentry : CNAME | value | list | string
    assignment : keyword dataentry ";" NEWLINE
    dict_assignment : CNAME NEWLINE "{" NEWLINE [assignment (assignment)*] "}" NEWLINE

    list: "(" (value|NEWLINE)* ")"
    list_assignment: CNAME NEWLINE list ";" NEWLINE

    file : [(dict_assignment | assignment | list_assignment)*]
    CPP_COMMENT: /\/\/[^\n]*/ NEWLINE
    C_COMMENT: "/*" /(.|\n)*?/ "*/" NEWLINE

    %ignore /[\n\f\r]+/
    %ignore CPP_COMMENT
    %ignore C_COMMENT
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.NUMBER
    %import common.WS
    %ignore WS
    %import common.NEWLINE
    %import common.CNAME
    """


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


parser = Lark(grammar, start="value", lexer="basic")

with open("turbulenceProperties", "r") as file:
    tree = parser.parse(file.read())

tree = OFTransformer().transform(tree)

print(tree.pretty())
