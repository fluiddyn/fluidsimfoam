from .ast import FoamInputFile
from .parser import dump, parse

__all__ = ["parse", "dump", "FoamInputFile", "DEFAULT_HEADER"]

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
