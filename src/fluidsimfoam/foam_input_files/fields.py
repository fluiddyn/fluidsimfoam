"""Helper to create field files

"""

from abc import ABC, abstractmethod
from numbers import Number

from fluidsimfoam.foam_input_files import parse
from fluidsimfoam.foam_input_files.ast import (
    Code,
    CodeStream,
    Dict,
    DimensionSet,
    FoamInputFile,
    List,
    Value,
    str2foam_units,
)

DEFAULT_CODE_INCLUDE = '#include "fvCFD.H"'
DEFAULT_CODE_OPTIONS = (
    "-I$(LIB_SRC)/finiteVolume/lnInclude \\\n-I$(LIB_SRC)/meshTools/lnInclude"
)
DEFAULT_CODE_LIBS = "-lmeshTools \\\n-lfiniteVolume"


class FieldABC(ABC):
    cls: str

    @classmethod
    def from_code(cls, code: str):
        if "nonuniform" not in code:
            tree = parse(code)
            return cls(None, None, tree=tree)

        raise NotImplementedError

    def __init__(self, name, dimension, tree=None, values=None):
        if tree is not None:
            self.tree = tree
            return

        info = {
            "version": "2.0",
            "format": "ascii",
            "class": self.cls,
            "object": name,
        }

        if not isinstance(dimension, DimensionSet):
            dimension = DimensionSet(str2foam_units(dimension))

        self.tree = FoamInputFile(
            info, children={"dimensions": dimension, "internalField": None}
        )

        self.tree.set_child("boundaryField", {})

        if values is not None:
            self.set_values(values)

    def dump(self):
        return self.tree.dump()

    @abstractmethod
    def set_values(self, values):
        """Set internalField with value(s)"""

    def set_codestream(
        self,
        code,
        include=DEFAULT_CODE_INCLUDE,
        options=DEFAULT_CODE_OPTIONS,
        libs=DEFAULT_CODE_LIBS,
    ):
        data = {
            "codeInclude": include,
            "codeOptions": options,
            "codeLibs": libs,
            "code": code,
        }
        data = {key: Code(key, value.strip()) for key, value in data.items()}
        self.tree.children["internalField"] = CodeStream(
            data, name="internalField", directive="#codeStream"
        )

    def set_boundary(self, name, type_, value=None):
        boundaries = self.tree.children["boundaryField"]
        data = {"type": type_}
        if value is not None:
            data["value"] = value

        boundaries[name] = Dict(data, name=name)


class VolScalarField(FieldABC):
    cls = "volScalarField"

    def set_values(self, values):
        if isinstance(values, Number):
            value = Value(values, name="uniform")
        else:
            value = List(
                values,
                name=f"internalField nonuniform\nList<scalar>\n{len(values)}",
            )
        self.tree.children["internalField"] = value


class VolVectorField(FieldABC):
    cls = "volVectorField"

    def set_values(self, values):
        n_elem = len(values)
        if n_elem == 3 and isinstance(values[0], Number):
            value = Value(List(values), name="uniform")
        else:
            value = List(
                [List(value) for value in values],
                name=f"internalField nonuniform\nList<vector>\n{n_elem}",
            )
        self.tree.children["internalField"] = value
