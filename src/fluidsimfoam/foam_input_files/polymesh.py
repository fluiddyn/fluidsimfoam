"""Read information on the mesh from the polymesh directory

"""


from io import StringIO

import numpy as np


def get_cells_coords(path):
    """Get cells coordinates"""

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

    assert x.size == nb_cells

    return x, y, z
