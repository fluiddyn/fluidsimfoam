from textwrap import dedent

from fluidsimfoam.foam_input_files import (
    BlockMeshDictRectilinear,
    ConstantFileHelper,
    FvSchemesHelper,
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

    name_variables = ["T", "U", "alphat", "epsilon", "k", "nut", "p", "p_rgh"]
    name_system_files = Output.name_system_files + [
        "blockMeshDict",
        "solverInfo",
        "streamlines",
    ]
    name_constant_files = Output.name_constant_files + ["g"]

    _helper_fv_schemes = FvSchemesHelper(
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

    _helper_turbulence_properties = ConstantFileHelper(
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
    _helper_transport_properties = ConstantFileHelper(
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
        params.control_dict._update_attribs(
            {
                "application": "buoyantBoussinesqPimpleFoam",
                "start_from": "latestTime",
                "end_time": 1000,
                "delta_t": 1,
                "write_control": "runTime",
                "write_interval": 50,
                "write_format": "binary",
            }
        )

    def _make_code_control_dict(self, params):
        code = super()._make_code_control_dict(params)
        return code + code_control_dict_functions

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {"nx": 80, "ny": 80, "nz": 1, "lx": 1.0, "ly": 1.0, "lz": 0.1}
        )

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

        bmd.add_boundary("wall", "frontAndBack", [b0.face("s"), b0.face("n")])
        bmd.add_boundary("wall", "topAndBottom", [b0.face("t"), b0.face("b")])
        bmd.add_boundary("wall", "hot", b0.face("e"))
        bmd.add_boundary("wall", "cold", b0.face("w"))

        return bmd.format(sort_vortices=False)
