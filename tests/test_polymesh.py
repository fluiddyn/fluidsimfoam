import tempfile

from pathlib import Path

from fluidsimfoam.foam_input_files.polymesh import get_cells_coords

example = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2206                                  |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    arch        "LSB;label=32;scalar=64";
    class       vectorField;
    location    "constant/polyMesh";
    object      points;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //


10
(
(0 0 0)
(0.15707963268 0 0)
(0.314159265359 0 0)
(0.471238898038 0 0)
(0.628318530718 0 0)
(0 0 0)
(0.15707963268 0 0)
(0.314159265359 0 0)
(0.471238898038 0 0)
(0.628318530718 0 0)
)

"""
from io import StringIO
import numpy as np

with tempfile.TemporaryDirectory() as tmpdirname:
    path = Path(tmpdirname) / "points"

    with open(path, "w") as file:
        file.write(example)

    with open(path) as file:
        for line in file:
            if line == "FoamFile\n":
                break

        for line in file:
            if line == "}\n":
                break

        for line in file:
            line = line[:-1]
            if line.isdigit():
                nb_cells = int(line)
                break

        assert file.readline() == "(\n"

        txt = file.read()

        txt = txt.replace("(", "").replace(")", "").strip()

        coords = np.loadtxt(StringIO(txt))
        x = coords[:, 0]
        y = coords[:, 1]
        z = coords[:, 2]

        assert y.max() == 0.0
        assert z.max() == 0.0


# def test_get_cells_coords():

#     pass
