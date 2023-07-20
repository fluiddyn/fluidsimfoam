---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Mesh generation with the BlockMeshDict utility

One of the *fluidsimfoam solver's* utilities is mesh generation. You may quickly parameterize your mesh and send as many simulations with various meshes using the BlockMeshDict.
Let's assume that we are generating this blockMeshDict:

````{code-cell} ipython3
```
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2206                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   0.1;

vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    movingWall
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
    fixedWalls
    {
        type wall;
        faces
        (
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);


// ************************************************************************* //

```
````

## Mesh Parameters

First, we can observe the mesh parameters, such as the number of grids in the x, y, and z dimensions, which are 20, 20, and 1 accordingly. Scale is 0.1 and length of domain in x, y and z directions are 1, 1 and 0.1, respectively.
In order to generate mesh, we should import `BlockMeshDict`, and each solver has a `Simul` object with all the default parameters. Then we assigne the default parameters to `params`, update some parameters we need to change by ```params.block_mesh_dict._update_attribs()```. 

```{code-cell} ipython3
from fluidsimfoam.foam_input_files import BlockMeshDict
from fluidsimfoam_phill import Simul

params = Simul.create_default_params()

params.block_mesh_dict._update_attribs(
    {
        "nx": 20,
        "ny": 20,
        "nz": 1,
        "scale": 0.1,
        "lx": 1,
        "ly": 1,
        "lz": 0.1,
    }
)
```

## Utilize `BlockMeshDict`

Now we have the updated `params.block_mesh_dict`. After creating an instance of `BlockMeshDict` class (bmd = BlockMeshDict()), we can set attributes to produce our blockMeshDict:

- {func}`set_scale`: set the scale
- {func}`add_vertex`: Add vertices, (coordinates, "name")
- {func}`replicate_vertices_further_z`: for 2D cases we can use it to duplicate the vertices with different "z"
- {func}`add_hexblock`: Add hex block, you need to pass vertex names(8) and number of grids in each directions, name.
- {func}`add_hexblock_from_2d`: Add hex block for 2D cases, you need to pass 4 vertex names
- {func}`add_boundary`: add boundary conditions
- {func}`add_cyclic_boundary`: add cyclic boundary conditions

```{code-cell} ipython3
def _make_code_block_mesh_dict(params):
    p_bmd = params.block_mesh_dict
    nx = p_bmd.nx
    ny = p_bmd.ny
    nz = p_bmd.nz

    lx = p_bmd.lx
    ly = p_bmd.ly
    lz = p_bmd.lz

    # make the blockmesh object:
    bmd = BlockMeshDict()

    # define the scale
    bmd.set_scale(params.block_mesh_dict.scale)

    # add vertices (coordinates, "name")
    for x_y_z_name in (
        # back
        (0, 0, 0, "left_bot"),
        (lx, 0, 0, "right_bot"),
        (lx, ly, 0, "right_up"),
        (0, ly, 0, "left_up"),
    ):
        bmd.add_vertex(*x_y_z_name)

    # replicate vertices for front with "lz"
    bmd.replicate_vertices_further_z(lz)

    # make block
    block_0 = bmd.add_hexblock_from_2d(
        ["left_bot", "right_bot", "right_up", "left_up"],
        [nx, ny, nz],
        "main",
    )

    # define boundaries (type, "name", [face])
    bmd.add_boundary("wall", "movingWall", [block_0.face("n")])
    bmd.add_boundary(
        "wall",
        "fixedWalls",
        [block_0.face("w"), block_0.face("e"), block_0.face("s")],
    )
    bmd.add_boundary(
        "wall", "frontAndBack", [block_0.face("b"), block_0.face("t")]
    )

    return bmd.format(sort_vortices="as_added")


mesh = _make_code_block_mesh_dict(params)
with open("./system/blockMeshDict", "w") as file:
    file.write(mesh)
pprint.pprint(mesh)
```

+++ {"user_expressions": []}

```{eval-rst}
.. literalinclude:: ./system/blockMeshDict
```

For more information you can see [here](https://fluidsimfoam.readthedocs.io/en/latest/_generated/fluidsimfoam.foam_input_files.blockmesh.html).

+++ {"user_expressions": []}

## Manipulate Mesh

We now have a parameterized mesh, which is quite simple to change. You may modify the mesh in the following ways, for example, to make it 3D:

```{code-cell} ipython3
params.block_mesh_dict.nz = 20
params.block_mesh_dict.lz = 1

mesh = _make_code_block_mesh_dict(params)
with open("./system/blockMeshDict2", "w") as file:
    file.write(mesh)
```

```{eval-rst}
.. literalinclude:: ./system/blockMeshDict2
```
