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


def add_default_boundaries(field):
    for name, type_ in (
        ("inlet", "cyclic"),
        ("outlet", "cyclic"),
        ("top", "zeroGradient"),
        ("bottom", "zeroGradient"),
        ("frontAndBackPlanes", "empty"),
    ):
        field.set_boundary(name, type_)


def make_scalar_field(name, dimension, values=None):
    field = VolScalarField(name, dimension, values=values)
    add_default_boundaries(field)
    return field


code_init_alpha_a = dedent(
    r"""
    const IOdictionary& d = static_cast<const IOdictionary&>(dict);
    const fvMesh& mesh = refCast<const fvMesh>(d.db());
    scalarField alpha_a(mesh.nCells(), 0);
    forAll(mesh.C(), i)
    {
        scalar y = mesh.C()[i].y();
        alpha_a[i] = 0.305*(1.0+tanh((12.5*0.006-y)/0.005));
    /*if (y < 12.5*0.006)
    {
    alpha_a[i] = 0.61;
    }
    else
    {
    alpha_a[i] = 0;
    }*/
    }
    alpha_a.writeEntry("", os);
"""
)


class OutputSED(Output):
    """Output for the SED solver"""

    name_variables = [
        "Theta",
        "U.a",
        "U.b",
        "alpha.a",
        "alphaPlastic",
        "delta",
        "epsilon.b",
        "k.b",
        "muI",
        "nut.b",
        "omega.b",
        "pa",
        "p_rbgh",
    ]
    name_system_files = Output.name_system_files + ["blockMeshDict"]
    name_constant_files = [
        "forceProperties",
        "granularRheologyProperties",
        "kineticTheoryProperties",
        "transportProperties",
        "turbulenceProperties.b",
        "g",
        "interfacialProperties",
        "ppProperties",
        "turbulenceProperties.a",
        "twophaseRASProperties",
    ]

    _default_control_dict_params = Output._default_control_dict_params.copy()
    _default_control_dict_params.update(
        {
            "application": "sedFoam_rbgh",
            "startFrom": "latestTime",
            "endTime": 20,
            "deltaT": 1e-5,
            "writeControl": "adjustableRunTime",
            "writeInterval": 5,
            "adjustTimeStep": "on",
            "maxCo": 0.1,
            "maxAlphaCo": 0.1,
            "maxDeltaT": 1e-3,
        }
    )
    _helper_fv_schemes = FvSchemesHelper(
        ddt="default  Euler implicit",
        grad="default  Gauss linear",
        div="""
            default         none
            // alphaEqn
            div(phi,alpha)  Gauss limitedLinear01 1
            div(phir,alpha) Gauss limitedLinear01 1
            // UEqn
            div(phi.a,U.a)    Gauss limitedLinearV 1
            div(phi.b,U.b)    Gauss limitedLinearV 1
            div(phiRa,Ua)   Gauss limitedLinear 1
            div(phiRb,Ub)   Gauss limitedLinear 1
            div(Rca)        Gauss linear
            div(Rcb)        Gauss linear
            // pEqn
            div(alpha,nu)   Gauss linear
            // k and EpsilonEqn
            div(phi.b,k.b)     Gauss limitedLinear 1
            div(phi.b,epsilon.b) Gauss limitedLinear 1
            div(phi.b,omega.b) Gauss limitedLinear 1
            // ThetaEqn
            div(phi,Theta)  Gauss limitedLinear 1
            // alphaPlastic
            div(phia,alphaPlastic)  Gauss limitedLinear01 1
            div(phia,pa_new_value)  Gauss limitedLinear 1
""",
        laplacian="""
            default         none
            laplacian(nuEffa,U.a) Gauss linear corrected
            laplacian(nuEffb,U.b) Gauss linear corrected
            laplacian(nuFra,U.a)  Gauss linear corrected
            laplacian((rho*(1|A(U))),p_rbgh) Gauss linear corrected
            laplacian(DkEff,k.b) Gauss linear corrected
            laplacian(DkEff,beta) Gauss linear corrected
            laplacian(DepsilonEff,epsilon.b) Gauss linear corrected
            laplacian(DepsilonEff,beta) Gauss linear corrected
            laplacian(DomegaEff,omega.b) Gauss linear corrected
            laplacian(kappa,Theta) Gauss linear corrected
            laplacian(kappaAlpha,alpha) Gauss linear corrected
""",
        interpolation={
            "default": "linear",
        },
        sn_grad={
            "default": "corrected",
        },
    )
    _helper_fv_schemes.add_dict("fluxRequired", {"default": "no", "p_rbgh": ""})

    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "phasea": {
                "rho": 2500,
                "nu": 1e-6,
                "d": 6e-3,
                "sF": 1,
                "hExp": 3.1,
            },
            "phaseb": {
                "rho": 1000,
                "nu": 1e-6,
                "d": 3e-3,
                "sF": 0.5,
                "hExp": 3.1,
            },
            "transportModel": "Newtonian",
            "nu": 1.0e-6,
            "nuMax": 1e2,
            "alphaSmall": 1e-5,
        },
        dimensions={
            "phasea": {"rho": "kg/m^3", "nu": "m^2/s", "d": "m"},
            "phaseb": {"rho": "kg/m^3", "nu": "m^2/s", "d": "m"},
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
                "RASModel": "twophaseMixingLength",
                "turbulence": "on",
                "printCoeffs": "on",
                "twophaseMixingLengthCoeffs": {
                    "expoLM": 1.0,
                    "alphaMaxLM": 0.61,
                    "kappaLM": 0.41,
                },
            },
        },
        comments={
            "RAS": {
                "RASModel": "can be twophaseMixingLength, twophasekEpsilon or twophasekOmega"
            }
        },
    )

    _helper_twophase_ras_properties = ConstantFileHelper(
        "twophaseRASProperties",
        {
            "SUS": 0,
            "KE1": 0,
            "KE3": 0,
            "B": 0.15,
            "Tpsmall": 1e-6,
        },
        dimensions={"Tpsmall": "kg/m^3/s"},
        default_dimension="",
        comments={
            "SUS": "Shared coefficients",
            "KE1": "density stra (Uf-Us)",
            "KE3": "turb generation",
            "B": "turb modulation coeff",
            "Tpsmall": "Limiters",
        },
    )

    _helper_force_properties = ConstantFileHelper(
        "forceProperties",
        {
            "gradPMEAN": [490.5, 0, 0],
            "tilt": 1,
            "Cvm": 0,
            "Cl": 0,
            "Ct": 0,
            "debugInfo": "true",
            "writeTau": "true",
        },
        dimensions={"gradPMEAN": "kg/m^2/s^2"},
        default_dimension="",
        comments={
            "gradPMEAN": "mean pressure",
            "tilt": "To impose same gravity term to both phases",
            "Cvm": "Virtual/Added Mass coefficient",
            "Cl": "Lift force coefficient",
            "Ct": "Eddy diffusivity coefficient for phase a",
        },
    )

    _helper_pp_properties = ConstantFileHelper(
        "ppProperties",
        {
            "ppModel": "JohnsonJackson",
            "alphaMax": 0.635,
            "alphaMinFriction": 0.57,
            "Fr": 5e-2,
            "eta0": 3,
            "eta1": 5,
            "packingLimiter": "no",
        },
        default_dimension="",
        dimensions={"Fr": "kg/m/s^2"},
    )

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {
                "nx": 1,
                "ny": 1,
                "nz": 120,
                "scale": 0.183,
                "lx": 1.0,
                "ly": 1.0,
                "lz": 0.1,
            }
        )

    def _make_code_block_mesh_dict(self, params):
        nx = params.block_mesh_dict.nx
        ny = params.block_mesh_dict.ny
        nz = params.block_mesh_dict.nz

        # lx = params.block_mesh_dict.lx
        # ly = params.block_mesh_dict.ly
        # lz = params.block_mesh_dict.lz

        bmd = BlockMeshDict()

        bmd.set_scale(params.block_mesh_dict.scale)

        step = 0.005
        index = 0
        for z in [step, -step]:
            for x, y in ((-step, 0.0), (+step, 0.0), (step, 1.0), (-step, 1.0)):
                bmd.add_vertex(x, y, z, f"v{index}")
                index += 1

        b0 = bmd.add_hexblock(
            [f"v{index}" for index in [0, 1, 5, 4, 3, 2, 6, 7]],
            (nx, ny, nz),
            name="",
        )

        bmd.add_cyclic_boundaries("inlet", "outlet", b0.face("w"), b0.face("e"))
        # for "top": issue with order...
        # there was (7 6 2 3) and we produce (3 2 6 7)
        bmd.add_boundary("wall", "top", b0.face("t"))
        bmd.add_boundary("wall", "bottom", b0.face("b"))
        bmd.add_boundary(
            "empty", "frontAndBackPlanes", [b0.face("s"), b0.face("n")]
        )

        return bmd.format(sort_vortices="as_added")

    @classmethod
    def _complete_params_alpha_a(cls, params):
        params._set_child(
            "init_fields",
            attribs={"type": "tanh", "width": 0.005},
            doc="""type have to be in ['tanh', 'codestream']""",
        )

    def _make_tree_alpha_a(self, params):
        field = make_scalar_field("alpha_a", dimension="")
        field.set_boundary("top", "fixedValue", "uniform 0")

        if params.init_fields.type == "codestream":
            field.set_codestream(code_init_alpha_a)
        elif params.init_fields.type == "tanh":
            x, y, z = self.sim.oper.get_cells_coords()
            width = params.init_fields.width
            field.set_values(0.305 * (1.0 + np.tanh((12.5 * 0.006 - y) / width)))
        else:
            raise ValueError(f"Unsupported {params.init_fields.type = }")

        return field

    def _make_tree_alpha_plastic(self, params):
        return make_scalar_field("alphaMinFriction", dimension="", values=0.57)

    def _make_tree_delta(self, params):
        return make_scalar_field("delta", dimension="", values=0.0)

    def _make_tree_mu_i(self, params):
        return make_scalar_field("muI", dimension="", values=0.0)

    def _make_tree_u_a(self, params, name="U.a"):
        field = VolVectorField(name, dimension="m/s", values=(0, 0, 0))
        add_default_boundaries(field)
        field.set_boundary("bottom", "fixedValue", "uniform (0 0 0)")
        return field

    def _make_tree_u_b(self, params):
        return self._make_tree_u_a(params, name="U.b")

    def _make_tree_omega_b(self, params):
        return make_scalar_field("omega.b", dimension="1/s", values=1e-20)

    def _make_tree_theta(self, params):
        return make_scalar_field("Theta", dimension="m^2/s^2", values=0.0)

    def _make_tree_epsilon_b(self, params):
        return make_scalar_field("epsilon", dimension="m^2/s^3", values=1e-8)

    def _make_tree_k_b(self, params):
        field = make_scalar_field("k.b", dimension="m^2/s^2", values=1e-6)
        field.set_boundary("bottom", "fixedValue", "uniform 1e-06")
        return field

    def _make_tree_nut_b(self, params):
        field = make_scalar_field("nut.b", dimension="m^2/s^1", values=0.0)
        field.set_boundary("bottom", "fixedValue", "uniform 0.0")
        return field

    def _make_tree_pa(self, params):
        field = make_scalar_field("pa", dimension="kg/m/s^2", values=0.0)
        field.set_boundary("top", "slip")
        return field

    def _make_tree_p_rbgh(self, params):
        field = make_scalar_field("p_rbgh", dimension="kg/m/s^2", values=0.0)
        field.set_boundary("top", "fixedValue", "uniform 0.0")
        field.set_boundary(
            "bottom", "fixedFluxPressure", gradient="$internalField"
        )
        return field
