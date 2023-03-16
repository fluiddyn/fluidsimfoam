from lark import Lark, Transformer

json_grammar = r"""
    ?value: CNAME
          | dict
          | assignment
          | string
          | CPP_COMMENT
          | C_COMMENT
          | SIGNED_NUMBER      -> number
    string : ESCAPED_STRING
    vector : "(" value value value ")"
    keyword : CNAME | value
    dataentry : CNAME | value | vector | string
    assignment : keyword dataentry ";" NEWLINE
    multi_assignment : [assignment (assignment)*]
    dict : CNAME NEWLINE "{" NEWLINE [assignment (assignment)*] "}" NEWLINE

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


class TreeToJson(Transformer):
    def string(self, s):
        (s,) = s
        return s[1:-1]
    def number(self, n):
        (n,) = n
        return float(n)

    list = list
    pair = tuple
    dict = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

json_parser = Lark(json_grammar, start='value', lexer='basic')

with open("turbulenceProperties", "r") as f:
    tree = json_parser.parse(f.read())

print(tree.pretty())