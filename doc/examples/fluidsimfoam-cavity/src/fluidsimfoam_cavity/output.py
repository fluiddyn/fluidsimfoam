from fluidsimfoam.foam_input_files import (
    BlockMeshDictRectilinear,
    ConstantFileHelper,
    FvSchemesHelper,
    VolScalarField,
    VolVectorField,
)
from fluidsimfoam.output import Output


class OutputCavity(Output):
    """Output for the TGV solver"""

    name_system_files = Output.name_system_files + [
        "blockMeshDict",
        "decomposeParDict",
    ]

    _helper_fv_schemes = FvSchemesHelper(
        ddt="default   Euler",
        grad="""
            default    Gauss linear
            grad(p)    Gauss linear
        """,
        div="""
            default         none
            div(phi,U)      Gauss linear""",
        laplacian="default  Gauss linear orthogonal",
        interpolation="default  linear",
        sn_grad="default  orthogonal",
    )

    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {"nu": 0.01},
    )

    def _make_tree_p(self, params):
        field = VolScalarField("p", "m^2/s^2")
        field.set_values(0)
        field.set_boundary("movingWall", "zeroGradient")
        field.set_boundary("fixedWalls", "zeroGradient")
        field.set_boundary("frontAndBack", "empty")
        return field

    def _make_tree_u(self, params):
        field = VolVectorField("U", "m/s")
        field.set_values([0, 0, 0])
        field.set_boundary("movingWall", "fixedValue", "uniform (1 0 0)")
        field.set_boundary("fixedWalls", "noSlip")
        field.set_boundary("frontAndBack", "empty")
        return field

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        default = {"nx": 20, "ny": 20, "nz": 1}
        default.update({"lx": 1.0, "ly": 1.0, "lz": 0.1})
        for key, value in default.items():
            params.block_mesh_dict[key] = value
        params.block_mesh_dict.scale = 0.1

    def _make_code_block_mesh_dict(self, params):
        lx = params.block_mesh_dict.lx
        ly = params.block_mesh_dict.ly
        lz = params.block_mesh_dict.lz

        nx = params.block_mesh_dict.nx
        ny = params.block_mesh_dict.ny
        nz = params.block_mesh_dict.nz

        bmd = BlockMeshDictRectilinear(
            lx, ly, lz, nx, ny, nz, params.block_mesh_dict.scale
        )
        b0 = bmd.block

        bmd.add_boundary("wall", "movingWall", b0.face("n"))
        bmd.add_boundary(
            "wall", "fixedWalls", [b0.face("w"), b0.face("e"), b0.face("s")]
        )
        bmd.add_boundary("empty", "frontAndBack", [b0.face("b"), b0.face("t")])

        return bmd.format(sort_vortices=False)
