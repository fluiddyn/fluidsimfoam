"""Helper to create field files

"""

from abc import ABC

from fluidsimfoam.foam_input_files import parse
from fluidsimfoam.foam_input_files.ast import (
    Code,
    CodeStream,
    Dict,
    DimensionSet,
    FoamInputFile,
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

    def __init__(self, name, dimension, tree=None):
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

    def dump(self):
        return self.tree.dump()

    def set_values(self, values):
        if isinstance(values, (int, float)):
            self.tree.children["internalField"] = Value(values, name="uniform")
            return

        raise NotImplementedError

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


class VolVectorField(FieldABC):
    cls = "volVectorField"
