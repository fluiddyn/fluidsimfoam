def parse():
    from lark import Lark, Token, Transformer

    grammar = r"""
        ?value: CNAME
            | dict_assignment
            | nested_dict
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
        nested_dict : CNAME NEWLINE "{" NEWLINE (dict_assignment)* "}" NEWLINE
        list: "(" (value|NEWLINE)* ")"
        list_assignment: CNAME NEWLINE list ";" NEWLINE

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
