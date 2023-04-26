"""OpenFOAM input files

.. autosummary::
   :toctree:

    blockmeshhelper
    ast
    generators
    parser

"""

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
]

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
