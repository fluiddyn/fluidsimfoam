"""Base class for the ``params`` object"""

from fluidsim_core.params import Parameters as _Parameters

table = {"(": "__opar__", ")": "__cpar__", ",": "__comma__", "*": "__mul__"}


def protect_characters(name):
    for char, code in table.items():
        name = name.replace(char, code)
    return name


def unprotect_characters(name):
    for char, code in table.items():
        name = name.replace(code, char)
    return name


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
