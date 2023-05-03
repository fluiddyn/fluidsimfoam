"""Read information on the mesh from the polyMesh directory

"""

import re
from functools import lru_cache
from io import StringIO

import numpy as np


@lru_cache(maxsize=1)
def get_points_coords(path):
    """Get points coordinates"""

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

    if txt.startswith("("):
        txt = re.sub("[()]", "", txt)

    txt = txt.strip()

    index_last_comment = txt.rfind("\n//")
    txt = txt[:index_last_comment].strip()

    coords = np.loadtxt(StringIO(txt))
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]

    assert x.size == nb_cells

    return x, y, z
