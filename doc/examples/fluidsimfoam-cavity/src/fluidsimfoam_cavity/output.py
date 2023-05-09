from fluidsimfoam.foam_input_files import (
    BlockMeshDict,
    ConstantFileHelper,
    FvSchemesHelper,
    Vertex,
    VolScalarField,
    VolVectorField,
)
from fluidsimfoam.output import Output


class OutputCavity(Output):
    """Output for the TGV solver"""

    system_files_names = Output.system_files_names + [
        "blockMeshDict",
        "decomposeParDict",
    ]

    helper_fv_schemes = FvSchemesHelper(
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

    helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {"nu": 0.01},
    )

    def make_tree_p(self, params):
        field = VolScalarField("p", "m^2/s^2")
        field.set_values(0)
        field.set_boundary("movingWall", "zeroGradient")
        field.set_boundary("fixedWalls", "zeroGradient")
        field.set_boundary("frontAndBack", "empty")
        return field

    def make_tree_u(self, params):
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

    def make_code_block_mesh_dict(self, params):
        nx = params.block_mesh_dict.nx
        ny = params.block_mesh_dict.ny
        nz = params.block_mesh_dict.nz

        lx = params.block_mesh_dict.lx
        ly = params.block_mesh_dict.ly
        lz = params.block_mesh_dict.lz

        bmd = BlockMeshDict()

        bmd.set_scale(params.block_mesh_dict.scale)

        basevs = [
            Vertex(0, 0, lz, "v0"),
            Vertex(lx, 0, lz, "v1"),
            Vertex(lx, ly, lz, "v2"),
            Vertex(0, ly, lz, "v3"),
        ]

        for v in basevs:
            bmd.add_vertex(v.x, v.y, 0, v.name + "-0")
            bmd.add_vertex(v.x, v.y, v.z, v.name + "+z")

        vertex_names = [
            f"v{index}{post}" for post in ("-0", "+z") for index in range(4)
        ]

        b0 = bmd.add_hexblock(
            vertex_names,
            (nx, ny, nz),
            name="",
        )

        bmd.add_boundary("wall", "movingWall", b0.face("n"))
        bmd.add_boundary(
            "wall", "fixedWalls", [b0.face("w"), b0.face("e"), b0.face("s")]
        )
        bmd.add_boundary("empty", "frontAndBack", [b0.face("b"), b0.face("t")])

        return bmd.format(sort_vortices=False)
