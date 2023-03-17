from lark import Lark, Token, Transformer

from .ast import OFInputFile

grammar = r"""
        ?value: CNAME
            | dict_assignment
            | nested_dict
            | list
            | list_assignment
            | file
            | assignment
            | string
            | CPP_COMMENT
            | C_COMMENT
            | SIGNED_NUMBER      -> number
        string : ESCAPED_STRING
        keyword : CNAME
        dataentry : CNAME | value | list | string
        assignment : [NEWLINE] keyword dataentry ";" NEWLINE
        dict_assignment : [NEWLINE] CNAME NEWLINE "{" NEWLINE [assignment (assignment)*] "}" NEWLINE
        nested_dict : [NEWLINE] CNAME NEWLINE "{" NEWLINE (dict_assignment)* "}" NEWLINE
        list : "(" (value|NEWLINE)* ")"
        nested_list : [NEWLINE] CNAME NEWLINE "(" [(list|NEWLINE)*] ")" ";" [NEWLINE]
        list_assignment : [NEWLINE] CNAME NEWLINE "(" [(list|NEWLINE)*] ")" ";" [NEWLINE]

        file : [(dict_assignment | nested_dict | assignment | list_assignment)*]
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
