from textwrap import dedent

import numpy as np

from fluidsimfoam.foam_input_files import (
    BlockMeshDict,
    ConstantFileHelper,
    FvSchemesHelper,
    VolScalarField,
    VolVectorField,
)

from fluidsimfoam.output import Output


# def add_default_boundaries(field):
#     for name, type_ in (
#         ("inlet", "cyclic"),
#         ("outlet", "cyclic"),
#         ("top", "zeroGradient"),
#         ("wall", "zeroGradient"),
#         ("frontAndBackPlanes", "empty"),
#     ):
#         field.set_boundary(name, type_)


# def make_scalar_field(name, dimension, values=None):
#     field = VolScalarField(name, dimension, values=values)
#     add_default_boundaries(field)
#     return field


# code_init_alpha_a = dedent(
#     r"""
#     const IOdictionary& d = static_cast<const IOdictionary&>(dict);
#     const fvMesh& mesh = refCast<const fvMesh>(d.db());
#     scalarField alpha_a(mesh.nCells(), 0);
#     forAll(mesh.C(), i)
#     {
#         scalar y = mesh.C()[i].y();
#         alpha_a[i] = 0.305*(1.0+tanh((0.01-y)/0.001));
#     }
#     alpha_a.writeEntry("", os);
# """
# )


class OutputSedveg(Output):
    name_variables = [
        "Theta",
        "U.a",
        "U.b",
        "U.c",
        "alpha.a",
        "alpha.c",
        "alphaPlastic",
        "delta",
        "epsilon.b",
        "k.b",
        "ks.b",
        "kw.b",
        "muI",
        "nut.b",
        "omega.b",
        "omegas.b",
        "omegaw.b",
        "p_rbgh",
        "pa",
    ]
    name_system_files = [
        "blockMeshDict",
        "controlDict",
        "fvSchemes",
        "fvSolution",
        "decomposeParDict",
    ]
    name_constant_files = [
        "filterProperties",
        "forceProperties",
        "g",
        "granularRheologyProperties",
        "interfacialProperties",
        "kineticTheoryProperties",
        "ppProperties",
        "transportProperties",
        "turbulenceProperties.a",
        "turbulenceProperties.b",
        "twophaseRASProperties",
    ]
    internal_symlinks = {}

    # _helper_control_dict = None
    # can be replaced by:
    _helper_control_dict = Output._helper_control_dict.new(
        {
            "application": "sedFoam_rbgh",
            "startFrom": "latestTime",
            "endTime": 50,
            "deltaT": 0.02,
            "writeFormat": "ascii",
            "writeControl": "adjustableRunTime",
            "writeInterval": 5,
            "adjustTimeStep": "true",
            "maxCo": 0.1,
            "maxAlphaCo": 0.1,
            "maxDeltaT": 1.0,
        }
    )

    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "phasea": {
                "rho": 2650,
                "nu": 1e-6,
                "d": 0.0005,
                "sF": 1,
                "hExp": 2.65,
            },
            "phaseb": {
                "rho": 1000,
                "nu": 1e-6,
                "d": 3e-3,
                "sF": 0.5,
                "hExp": 2.65,
            },
            "phasec": {
                "rho": 1,
                "nu": 0.0,
                "d": 0.0063,
                "sF": 1,
                "hExp": 2.65,
            },
            "transportModel": "Newtonian",
            "nu": 1.0e-6,
            "nuMax": 1e2,
            "alphaSmall": 1e-5,
        },
        dimensions={
            "phasea": {"rho": "kg/m^3", "nu": "m^2/s", "d": "m"},
            "phaseb": {"rho": "kg/m^3", "nu": "m^2/s", "d": "m"},
            "phasec": {"rho": "kg/m^3", "nu": "m^2/s", "d": "m"},
            "nu": "m^2/s",
            "nuMax": "m^2/s",
        },
        default_dimension="",
        comments={
            "phasea": {
                "sF": "shape Factor to adjust settling velocity for non-spherical particles",
                "hExp": "hindrance exponent for drag: beta^(-hExp) (2.65 by default)",
            },
            "nuMax": "viscosity limiter for the Frictional model (required for stability)",
            "alphaSmall": "minimum volume fraction (phase a) for division by alpha",
        },
    )

    _helper_turbulence_properties_b = ConstantFileHelper(
        "turbulenceProperties.b",
        {
            "simulationType": "RAS",
            "RAS": {
                "RASModel": "twophasekOmegaVeg",
                "turbulence": "on",
                "printCoeffs": "on",
                "twophasekOmegaVegCoeffs": {
                    "alphaOmega": 0.52,
                    "betaOmega": 0.072,
                    "C3om": 0.35,
                    "C4om": 1.0,
                    "alphaKomega": 0.5,
                    "alphaOmegaOmega": 0.5,
                    "Clim": 0.0,
                    "sigmad": 0.0,
                    "Cmu": 0.09,
                    "Clambda": 0.01,
                    "KE2": 0.0,
                    "KE4": 1.0,
                    "KE6": 0.2,
                    "KE7": 0.15,
                    "nutMax": 0.005,
                    "popeCorrection": "false",
                    "writeTke": "true",
                },
                "twophasekOmegaCoeffs": {
                    "alphaOmega": 0.52,
                    "betaOmega": 0.072,
                    "C3om": 0.35,
                    "C4om": 1.0,
                    "alphaKomega": 0.5,
                    "alphaOmegaOmega": 0.5,
                    "Clim": 0.0,
                    "sigmad": 0.0,
                    "Cmu": 0.09,
                    "KE2": 0.0,
                    "KE4": 1.0,
                    "nutMax": 0.005,
                    "popeCorrection": "false",
                    "writeTke": "true",
                },
            },
        },
    )

    _helper_force_properties = ConstantFileHelper(
        "forceProperties",
        {
            "gradPMEAN": [400, 0, 0],
            "phiSwitch": 1,
            "tilt": 1,
            "Cvm": 0,
            "Cl": 0,
            "Ct": 0,
            "debugInfo": "true",
            "writeTau": "true",
            "writeMomentumBudget": "true",
            "ClipUa": 1,
        },
        dimensions={"gradPMEAN": "kg/m^2/s^2"},
        default_dimension="",
        comments={
            "phiSwitch": "If 1, accounts for the reduction of volume due to the presence of vegetation",
            "gradPMEAN": "mean pressure",
            "tilt": "To impose same gravity term to both phases",
            "Cvm": "Virtual/Added Mass coefficient",
            "Cl": "Lift force coefficient",
            "Ct": "Eddy diffusivity coefficient for phase a",
        },
    )

    _helper_twophase_ras_properties = ConstantFileHelper(
        "twophaseRASProperties",
        {
            "SUS": 3.0,
            "KE1": 0,
            "KE3": 0,
            "B": 0.25,
            "Tpsmall": 1e-6,
        },
        dimensions={"Tpsmall": "kg/m^3/s"},
        default_dimension="",
    )

    # remove these lines to get fluidsimfoam default helpers
    _helper_turbulence_properties = None
    _complete_params_block_mesh_dict = None

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {
                "nx": 1,
                "ny1": 50,
                "ny2": 50,
                "nz": 1,
                "scale": 1,
                "lx": 0.02,
                "ly1": 0.01,
                "ly2": 0.13,
                "lz": 0.02,
                "grading1": "simpleGrading (1 1 1)",
                "grading2": "simpleGrading (1 1 46.0284)",
            }
        )

    def _make_code_block_mesh_dict(self, params):
        nx = params.block_mesh_dict.nx
        ny1 = params.block_mesh_dict.ny1
        ny2 = params.block_mesh_dict.ny2
        nz = params.block_mesh_dict.nz

        lx = params.block_mesh_dict.lx
        ly1 = params.block_mesh_dict.ly1
        ly2 = params.block_mesh_dict.ly2
        lz = params.block_mesh_dict.lz

        grading1 = params.block_mesh_dict.grading1
        grading2 = params.block_mesh_dict.grading2

        bmd = BlockMeshDict()

        bmd.set_scale(params.block_mesh_dict.scale)

        stepz = lz/2
        index = 0
        for z in [stepz, -stepz]:
            for x, y in ((+lx/2, 0.0), (lx/2, ly1), (-lx/2, ly1), (-lx/2, 0.0)):
                bmd.add_vertex(x, y, z, f"v{index}")
                index += 1
        for z in [stepz, -stepz]:        
            for x, y in ((lx/2, ly2), (-lx/2, ly2)):
                bmd.add_vertex(x, y, z, f"v{index}")
                index += 1

        b0 = bmd.add_hexblock(
            [f"v{index}" for index in [3, 0, 4, 7, 2, 1, 5, 6]],
            (nx, nz, ny1),
            name="",
            grading=grading1
        )
        b1 = bmd.add_hexblock(
            [f"v{index}" for index in [2, 1, 5, 6, 9, 8, 10, 11]],
            (nx, nz, ny2),
            name="",
            grading=grading2,
        )

        bmd.add_cyclic_boundaries("inlet", "outlet", b0.face("w"), b0.face("e"))
        # for "top": issue with order...
        # there was (7 6 2 3) and we produce (3 2 6 7)
        bmd.add_boundary("wall", "top", b0.face("t"))
        bmd.add_boundary("wall", "walls", b0.face("b"))
        bmd.add_boundary(
            "empty", "frontAndBackPlanes", [b0.face("s"), b0.face("n")]
        )

        return bmd.format(sort_vortices="as_added")


    # @classmethod
    # def _complete_params_alpha_a(cls, params):
    #     params._set_child(
    #         "init_fields",
    #         attribs={"type": "tanh", "width": 0.001, "bed_height": 0.01},
    #         doc="""type have to be in ['tanh', 'codestream']""",
    #     )

    # def _make_tree_alpha_a(self, params):
    #     field = make_scalar_field("alpha_a", dimension="")
    #     field.set_boundary("top", "fixedValue", "uniform 0")

    #     if params.init_fields.type == "codestream":
    #         field.set_codestream(code_init_alpha_a)
    #     elif params.init_fields.type == "tanh":
    #         x, y, z = self.sim.oper.get_cells_coords()
    #         width = params.init_fields.width
    #         bed_height = params.init_fields.bed_height
    #         field.set_values(0.305 * (1.0 + np.tanh((bed_height - y) / width)))
    #     else:
    #         raise ValueError(f"Unsupported {params.init_fields.type = }")

    #     return field