"""Base class for the ``params`` object"""

import re

import fluiddyn.util.xmltotext
from fluidsim_core.params import Parameters as _Parameters


def get_indent_after_tag(text):
    return " " * (len(re.match(r"\s*\S*", text).group()) + 1)


def get_position_first_letter(text):
    return len(re.match(r"\s*", text).group())


pattern_entries = re.compile(r'''[\w]+="[^"]*"''')


def format_too_long_tagstart(text, lengthmax=79):
    if len(text) <= lengthmax:
        return text

    lines = []
    first_word = text.strip().split(None, 1)[0]

    position_first_letter = get_position_first_letter(text)
    line = " " * position_first_letter + first_word
    indent = get_indent_after_tag(text)

    entries = pattern_entries.findall(text)
    for word in entries:
        if len(line + word) > lengthmax:
            lines.append(line)
            line = indent + word
        else:
            if line.endswith(" "):
                line = line + word
            else:
                line = line + " " + word

    if text.endswith("/>"):
        end = "/>"
    else:
        end = ">"

    lines.append(line + end)
    return "\n".join(lines)


fluiddyn.util.xmltotext.format_too_long_tagstart = format_too_long_tagstart


table = {
    "(": "__opar__",
    ")": "__cpar__",
    ",": "__comma__",
    "*": "__mul__",
    ".": "__dot__",
    "|": "__bar__",
}
pattern_protect = re.compile(
    "(" + "|".join(re.escape(c) for c in table.keys()) + ")"
)
pattern_unprotect = re.compile("(" + "|".join(table.values()) + ")")
table_inverse = {v: k for k, v in table.items()}


def protect_characters(name):
    return pattern_protect.sub(lambda match: table[match.group()], name)


def unprotect_characters(name):
    return pattern_unprotect.sub(lambda match: table_inverse[match.group()], name)


class Parameters(_Parameters):
    def _make_element_xml(self, parentxml=None):
        elemxml = super()._make_element_xml(parentxml)
        elemxml.attrib = {
            protect_characters(name): value
            for name, value in elemxml.attrib.items()
        }
        return elemxml

    def _load_from_elemxml(self, elemxml):
        elemxml.attrib = {
            unprotect_characters(name): value
            for name, value in elemxml.attrib.items()
        }
        super()._load_from_elemxml(elemxml)

    def __repr__(self):
        return unprotect_characters(super().__repr__())

    def _del_attrib(self, key):
        del self.__dict__[key]
        self._key_attribs.remove(key)

    def __getitem__(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            return super().__getitem__(key)

    def _update_attribs(self, attribs):
        for key, value in attribs.items():
            try:
                self[key] = value
            except AttributeError:
                self._set_attrib(key, value)
