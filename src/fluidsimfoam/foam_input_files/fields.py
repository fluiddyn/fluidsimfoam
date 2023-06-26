"""Helper to create field files

"""

import re
import struct
from abc import ABC, abstractmethod
from io import BytesIO
from numbers import Number
from pathlib import Path
from typing import Union

import numpy as np

from fluidsimfoam.foam_input_files import parse, parse_header, read_header
from fluidsimfoam.foam_input_files.ast import (
    Code,
    CodeStream,
    Dict,
    DimensionSet,
    FoamInputFile,
    List,
    Value,
)

DEFAULT_CODE_INCLUDE = '#include "fvCFD.H"'
DEFAULT_CODE_OPTIONS = (
    "-I$(LIB_SRC)/finiteVolume/lnInclude \\\n-I$(LIB_SRC)/meshTools/lnInclude"
)
DEFAULT_CODE_LIBS = "-lmeshTools \\\n-lfiniteVolume"


def get_arch(header: dict):
    """Get architecture info

    From OpenFOAM documentation: "The arch specification indicates the machine
    endian (LSB|MSB), the label width (32|64) and the scalar precision (32|64)."

    """
    arch = header["arch"]
    arch = arch.removeprefix('"').removesuffix('"')
    endianess, label_width, scalar_precision = arch.split(";")
    label_width = int(label_width[len("label=") :])
    scalar_precision = int(scalar_precision[len("scalar=") :])
    return endianess, label_width, scalar_precision


byte_order_codes = {
    # Little-endian, least significant byte (LSB) first
    "LSB": "<",
    # Big-endian, most significant byte (MSB) first
    "MSB": ">",
}

dcode_types = {
    32: "f",
    64: "d",
}


def create_array_from_bin_data(
    bin_data: bytes,
    cls_name: str,
    endianess: str,
    nb_elems: int,
    scalar_precision: int,
):
    nb_numbers_per_elem = 1
    if "Vector" in cls_name:
        nb_numbers_per_elem = 3
    elif "SymmTensor" in cls_name:
        nb_numbers_per_elem = 6
    elif "Tensor" in cls_name:
        nb_numbers_per_elem = 9

    fmt = (
        byte_order_codes[endianess]
        + f"{nb_elems*nb_numbers_per_elem:d}"
        + dcode_types[scalar_precision]
    )

    arr = np.array(struct.unpack(fmt, bin_data))
    if nb_numbers_per_elem > 1:
        arr = arr.reshape((nb_elems, nb_numbers_per_elem))
    return arr


class FieldABC(ABC):
    cls_name: str

    @classmethod
    def from_code(
        cls, code: Union[bytes, str], skip_boundary_field=False, header=None
    ):
        if header is None:
            if isinstance(code, bytes):
                code_for_header = code.split(b"\n}\n")[0].decode() + "\n}\n"
            else:
                code_for_header = code
            header = parse_header(code_for_header)

        if isinstance(code, str):
            code = code.encode()

        if b"nonuniform" not in code:
            tree = parse(code)
            return cls(None, None, tree=tree)

        index_nonuniform = code.index(b"nonuniform")
        try:
            index_boundaryField = code.rindex(b"boundaryField", index_nonuniform)
        except ValueError:
            index_boundaryField = len(code)

        index_opening_par = code.index(
            b"(", index_nonuniform, index_boundaryField
        )
        index_closing_par = code.rindex(
            b")", index_nonuniform, index_boundaryField
        )

        code_to_parse = code[:index_nonuniform] + b";\n"
        if not skip_boundary_field:
            code_to_parse += b"\n" + code[index_boundaryField:]

        tree = parse(code_to_parse.decode())
        code_data = code[index_opening_par + 1 : index_closing_par].strip()

        format = header["format"]
        if format == "ascii":
            if code_data.startswith(b"("):
                code_data = re.sub(b"[()]", b"", code_data)
            data = np.loadtxt(BytesIO(code_data))
        elif format == "binary":
            endianess, label_width, scalar_precision = get_arch(header)
            nb_elems = int(
                code[index_nonuniform:index_opening_par].split(b">")[1].strip()
            )
            data = create_array_from_bin_data(
                code_data, cls.cls_name, endianess, nb_elems, scalar_precision
            )

        tree.data = data
        return cls("", "", tree=tree, values=data)

    @classmethod
    def from_path(cls, path: str or Path, skip_boundary_field=False, header=None):
        path = Path(path)
        field = cls.from_code(
            path.read_bytes(),
            skip_boundary_field=skip_boundary_field,
            header=header,
        )
        field.path = path
        return field

    def __init__(self, name, dimension, tree=None, values=None):
        if tree is not None:
            self.tree = tree
        else:
            info = {
                "version": "2.0",
                "format": "ascii",
                "class": self.cls_name,
                "object": name,
            }

            if not isinstance(dimension, DimensionSet):
                dimension = DimensionSet(dimension)

            self.tree = FoamInputFile(
                info, children={"dimensions": dimension, "internalField": None}
            )

            self.tree.set_child("boundaryField", {})

        if values is not None:
            self.set_values(values)

        self.path = None

    def dump(self):
        return self.tree.dump()

    def overwrite(self):
        if self.path is None:
            raise ValueError("self.path is None")
        with open(self.path, "w") as file:
            file.write(self.dump())

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

    def set_boundary(self, name, type_, value=None, gradient=None):
        boundaries = self.tree.children["boundaryField"]
        data = {"type": type_}
        if value is not None:
            data["value"] = value
        if gradient is not None:
            data["gradient"] = gradient
        boundaries[name] = Dict(data, name=name)

    def set_name(self, name):
        self.tree.info["object"] = name

    def get_array(self):
        return np.array(self.tree.children["internalField"])


class VolScalarField(FieldABC):
    cls_name = "volScalarField"

    def set_values(self, values):
        if isinstance(values, Number):
            value = Value(values, name="uniform")
        else:
            value = List(
                list(values),
                name=f"internalField nonuniform\nList<scalar>\n{len(values)}",
            )
        self.tree.children["internalField"] = value


class VolVectorField(FieldABC):
    cls_name = "volVectorField"

    def set_values(self, values, vy=None, vz=None):
        if vy is not None:
            if vz is None:
                raise ValueError
            if not isinstance(values, np.ndarray):
                raise ValueError
            if values.ndim != 1 or values.size != vy.size != vz.size:
                raise ValueError
            vx = values
            values = np.stack([vx, vy, vz]).T

        n_elem = len(values)
        if n_elem == 3 and isinstance(values[0], Number):
            value = Value(
                "(" + " ".join(str(value) for value in values) + ")",
                name="uniform",
            )
        else:
            value = values
        self.tree.set_child("internalField", value)

    def get_components(self):
        arr = self.get_array()
        return arr[:, 0], arr[:, 1], arr[:, 2]


class VolTensorField(FieldABC):
    cls_name = "volTensorField"

    def set_values(self, values):
        if not isinstance(values, np.ndarray) or values.ndim != 2:
            raise NotImplementedError(
                "not isinstance(values, np.ndarray) or values.ndim != 2"
            )

        self.tree.set_child("internalField", values)


classes = {
    cls.cls_name: cls for cls in (VolScalarField, VolVectorField, VolTensorField)
}


def read_field_file(path, skip_boundary_field=True):
    header = read_header(path)
    try:
        cls_name = header["class"]
    except KeyError:
        raise RuntimeError(f"no class found for file {path}")
    cls = classes[cls_name]
    return cls.from_path(
        path, skip_boundary_field=skip_boundary_field, header=header
    )


def create_field_from_code(code):
    header = parse_header(code)
    try:
        cls_name = header["class"]
    except KeyError:
        raise RuntimeError(f"no class found for this code: {code[:500] = }")
    cls = classes[cls_name]
    return cls.from_code(code, header=header)
