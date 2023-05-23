from fluidsimfoam.foam_input_files import (
    ConstantFileHelper,
    FvOptionsHelper,
    FvSchemesHelper,
    VolScalarField,
    VolVectorField,
)
from fluidsimfoam.output import Output

from .blockmesh import make_code_blockmesh


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


def make_vector_field(name, dimension, values=None):
    field = VolVectorField(name, dimension, values=values)
    add_default_boundaries(field)
    return field


class OutputPHill(Output):
    """Output for the phill solver"""

    name_variables = ["U", "p_rgh", "T", "alphat"]
    name_system_files = Output.name_system_files + ["blockMeshDict", "fvOptions"]
    name_constant_files = ["g", "transportProperties", "turbulenceProperties"]

    _default_control_dict_params = Output._default_control_dict_params.copy()
    _default_control_dict_params.update(
        {
            "application": "buoyantBoussinesqPimpleFoam",
            "startFrom": "latestTime",
            "endTime": 1200000,
            "deltaT": 10,
            "writeControl": "adjustableRunTime",
            "writeInterval": 5000,
            "adjustTimeStep": "on",
            "maxCo": 0.6,
            "maxAlphaCo": 0.6,
            "maxDeltaT": 1,
        }
    )

    _helper_fv_schemes = FvSchemesHelper(
        ddt="default         Euler implicit",
        grad="default         Gauss linear",
        div="""
        default         none
        div(phi,U)      Gauss upwind
        div(phi,T)      Gauss upwind
        div(phi,R)      Gauss upwind
        div(R)          Gauss linear
        div((nuEff*dev2(T(grad(U))))) Gauss linear
        div((nuEff*dev(T(grad(U))))) Gauss linear
""",
        laplacian="""
        default         Gauss linear corrected
""",
        interpolation={
            "default": "linear",
        },
        sn_grad={
            "default": "uncorrected",
        },
    )

    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "transportModel": "Newtonian",
            "nu": 1.0e-2,
            "Pr": 10,
            "beta": 1,
            "TRef": 0,
            "Prt": 1,
        },
        dimensions={
            "nu": "m^2/s",
            "Pr": "1",
            "beta": "1/K",
            "TRef": "K",
            "Prt": "1",
        },
        default_dimension="",
        comments={},
    )

    _helper_g = ConstantFileHelper(
        "g",
        {"value": [0, -9.81, 0]},
        dimension="m/s^2",
        cls="uniformDimensionedVectorField",
    )

    _helper_fv_options = FvOptionsHelper()
    _helper_fv_options.add_option(
        "meanVelocityForce",
        name="momentumSource",
        active=True,
        default={
            "fields": "(U)",
            "Ubar": "(0.1 0 0)",
        },
        parameters=["Ubar"],
    )

    _helper_fv_options.add_option(
        "atmCoriolisUSource",
        active=False,
        default={
            "Omega": "(0 7.2921e-5 0)",
        },
        parameters=["Omega"],
    )

    _helper_fv_options.add_option(
        "explicitPorositySource",
        name="porosity",
        cell_zone="porosity",
        coeffs={
            "type": "fixedCoeff",
            "fixedCoeffCoeffs": {
                "alpha": "(500 -1000 -1000)",
                "beta": "(0 0 0)",
                "rhoRef": "1",
                "coordinateSystem": {
                    "origin": "(0 0 0)",
                    "e1": "(0.70710678 0.70710678 0)",
                    "e2": "(0 0 1)",
                },
            },
        },
        parameters=["fixedCoeffCoeffs/alpha"],
    )

    _helper_fv_options.add_option(
        "explicitPorositySource",
        name="porosity_darcy",
        cell_zone="porosity",
        coeffs={
            "type": "DarcyForchheimer",
            "d": "(0 1e6 0)",
            "f": "(0 1e6 0)",
            "coordinateSystem": {
                "type": "cartesian",
                "origin": "(0 0 0)",
                "e1": "(1 0 0)",
                "e2": "(0 1 0)",
            },
        },
        parameters=["f", "d"],
    )

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {
                "nx": 20,
                "ny": 50,
                "nz": 1,
                "ny_porosity": 10,
                "h_max": 80,
                "ly_porosity": 3000,
                "lx": 2000,
                "ly": 2000,
                "lz": 0.01,
                "scale": 1,
                "geometry": "sinus",
            }
        )

    def _make_code_block_mesh_dict(self, params):
        return make_code_blockmesh(params.block_mesh_dict)

    def _make_tree_alphat(self, params):
        return make_scalar_field("alphat", dimension="m^2/s", values=0)

    def _make_tree_p_rgh(self, params):
        return make_scalar_field("p_rgh", dimension="m^2/s^2", values=0)

    def _make_tree_u(self, params):
        field = make_vector_field("U", dimension="m/s", values=[0.1, 0, 0])
        field.set_boundary("top", "slip")
        field.set_boundary("bottom", "noSlip")
        return field

    @classmethod
    def _complete_params_t(cls, params):
        params._set_child(
            "init_fields",
            attribs={"buoyancy_frequency": 1e-3, "T0": 0},
            doc="""The fluid is linearly stratifed with a buoyancy frequency""",
        )

    def _make_tree_t(self, params):
        field = make_scalar_field("T", dimension="K")

        x, y, z = self.sim.oper.get_cells_coords()
        N = params.init_fields.buoyancy_frequency
        T0 = params.init_fields.T0
        field.set_values(T0 + (N**2) / 9.81 * y)

        return field
