from textwrap import dedent

from inflection import underscore

from fluidsimfoam.foam_input_files import (
    BlockMeshDict,
    ConstantFileHelper,
    FvSchemesHelper,
    Vertex,
)
from fluidsimfoam.output import Output

code_control_dict_functions = dedent(
    """
    functions
    {
        #includeFunc solverInfo
        #includeFunc streamlines
    }
"""
)


class OutputCBox(Output):
    """Output for the cbox solver"""

    variable_names = ["T", "U", "alphat", "epsilon", "k", "nut", "p", "p_rgh"]
    system_files_names = Output.system_files_names + [
        "blockMeshDict",
        "solverInfo",
        "streamlines",
    ]
    constant_files_names = Output.constant_files_names + ["g"]

    helper_fv_schemes = FvSchemesHelper(
        ddt={"default": "Euler"},
        grad={"default": "Gauss linear"},
        div={
            "default": "none",
            "div(phi,U)": "Gauss linearUpwind grad(U)",
            "div(phi,T)": "Gauss limitedLinear 1",
            "turbulence": "Gauss limitedLinear 1",
            "div(phi,k)": "$turbulence",
            "div(phi,epsilon)": "$turbulence",
            "div((nuEff*dev2(T(grad(U)))))": "Gauss linear",
        },
        laplacian={
            "default": "Gauss linear corrected",
        },
        interpolation={
            "default": "linear",
        },
        sn_grad={
            "default": "corrected",
        },
    )

    helper_turbulence_properties = ConstantFileHelper(
        "turbulenceProperties",
        {
            "simulationType": "laminar",
            "RAS": {
                "RASModel": "kEpsilon",
                "turbulence": "on",
                "printCoeffs": "on",
            },
        },
    )
    helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "transportModel": "Newtonian",
            "nu": 0.001,
            "beta": 1.88583,
            "TRef": 300,
            "Pr": 1.0,
            "Prt": 1.0,
        },
        comments={
            "nu": "Laminar viscosity",
            "beta": "Thermal expansion coefficient",
            "TRef": "Reference temperature",
            "Pr": "Laminar Prandtl number",
            "Prt": "Turbulent Prandtl number",
        },
    )

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    @classmethod
    def _complete_params_control_dict(cls, params):
        super()._complete_params_control_dict(params)

        default = {
            "application": "buoyantBoussinesqPimpleFoam",
            "startFrom": "latestTime",
            "endTime": 1000,
            "deltaT": 1,
            "writeControl": "runTime",
            "writeInterval": 50,
            "writeFormat": "binary",
        }

        for key, value in default.items():
            params.control_dict[underscore(key)] = value

    def make_code_control_dict(self, params):
        code = super().make_code_control_dict(params)
        return code + code_control_dict_functions

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        default = {"nx": 80, "ny": 80, "nz": 1}
        default.update({"lx": 1.0, "ly": 1.0, "lz": 0.1})
        for key, value in default.items():
            params.block_mesh_dict[key] = value

    def make_code_block_mesh_dict(self, params):
        nx = params.block_mesh_dict.nx
        ny = params.block_mesh_dict.ny
        nz = params.block_mesh_dict.nz

        lx = params.block_mesh_dict.lx
        ly = params.block_mesh_dict.ly
        lz = params.block_mesh_dict.lz

        bmd = BlockMeshDict()

        bmd.set_metric(params.block_mesh_dict.metric)

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

        bmd.add_boundary("wall", "frontAndBack", [b0.face("s"), b0.face("n")])
        bmd.add_boundary("wall", "topAndBottom", [b0.face("t"), b0.face("b")])
        bmd.add_boundary("wall", "hot", b0.face("e"))
        bmd.add_boundary("wall", "cold", b0.face("w"))

        return bmd.format(sort_vortices=False)
