"""OpenFOAM input files

.. rubric:: AST and parser

.. autosummary::
   :toctree:

    ast
    generators
    parser

.. rubric:: Helper to create input files

.. autosummary::
   :toctree:

    blockmesh
    fields
    fv_schemes
    constant_files

"""

from abc import ABC, abstractmethod

from .ast import Dict, FoamInputFile, List, Value
from .parser import dump, parse

__all__ = [
    "parse",
    "dump",
    "FoamInputFile",
    "DEFAULT_HEADER",
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
]


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

# taken from https://doc.cfd.direct/openfoam/user-guide-v6/controldict
DEFAULT_CONTROL_DICT = dict(
    application="icoFoam",
    startFrom="startTime",
    startTime=0,
    stopAt="endTime",
    endTime=0.5,
    deltaT=0.005,
    writeControl="timeStep",
    writeInterval=20,
    purgeWrite=0,
    writeFormat="ascii",
    writePrecision=6,
    writeCompression="off",
    timeFormat="general",
    timePrecision=6,
    runTimeModifiable="true",
)

from .blockmesh import BlockMeshDict, Vertex
from .constant_files import ConstantFileHelper
from .fields import VolScalarField, VolVectorField, read_field_file
from .fv_schemes import FvSchemesHelper
