"""OpenFOAM input files

.. rubric:: AST and parser

.. autosummary::
   :toctree:

    ast
    generators
    parser
    format

.. rubric:: Helper to create input files

.. autosummary::
   :toctree:

    blockmesh
    control_dict
    fields
    fv_schemes
    constant_files
    fv_options
    decompose_par
    util

"""
from abc import ABC, abstractmethod

from inflection import underscore

from .ast import Dict, DimensionSet, FoamInputFile, List, Value
from .parser import dump, parse

__all__ = [
    "parse",
    "dump",
    "create_field_from_code",
    "FoamInputFile",
    "DEFAULT_HEADER",
    "ControlDictHelper",
    "Dict",
    "List",
    "Value",
    "BlockMeshDict",
    "VolScalarField",
    "VolVectorField",
    "FvSchemesHelper",
    "Vertex",
    "read_field_file",
    "FileHelper",
    "ConstantFileHelper",
    "BlockMeshDictRectilinear",
    "FvOptionsHelper",
    "DimensionSet",
    "DecomposeParDictHelper",
    "format_code",
    "FoamFormatError",
]


def _as_py_name(name):
    return underscore(name).replace(".", "_")


def _update_dict_with_params(data, params_data):
    for key, value in data.items():
        name = underscore(key)

        try:
            param_value = params_data[name]
        except (KeyError, AttributeError):
            continue

        if isinstance(value, dict):
            _update_dict_with_params(value, param_value)
        else:
            data[key] = param_value


def _complete_params_dict(subparams, name, default, doc=None):
    name = _as_py_name(name)
    subsubparams = subparams._set_child(name, doc=doc)

    for key, value in default.items():
        if isinstance(value, dict):
            _complete_params_dict(subsubparams, key, value)
            continue

        subsubparams._set_attrib(_as_py_name(key), value)


class FileHelper(ABC):
    """Abstract class for "Helper" objects"""

    @abstractmethod
    def complete_params(self, params):
        """Complete the params object"""

    @abstractmethod
    def make_tree(self, params):
        """Make the AST corresponding to a file"""


DEFAULT_HEADER = r"""
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2206                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
"""

DEFAULT_HEADER = DEFAULT_HEADER[1:-1]

from .blockmesh import BlockMeshDict, BlockMeshDictRectilinear, Vertex
from .constant_files import ConstantFileHelper
from .control_dict import ControlDictHelper
from .decompose_par import DecomposeParDictHelper
from .fields import (
    VolScalarField,
    VolVectorField,
    create_field_from_code,
    read_field_file,
)
from .format import FoamFormatError, format_code
from .fv_options import FvOptionsHelper
from .fv_schemes import FvSchemesHelper
