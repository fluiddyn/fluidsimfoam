from textwrap import dedent

from fluidsimfoam.foam_input_files.blockmeshhelper import BlockMeshDict, Vertex
from fluidsimfoam.foam_input_files.fields import VolScalarField, VolVectorField
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

    variable_names = [
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
    system_files_names = Output.system_files_names + ["blockMeshDict"]
    constant_files_names = [
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

    default_control_dict_params = Output.default_control_dict_params.copy()
    default_control_dict_params.update(
        {
            "application": "sedFoam",
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

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        default = {"nx": 1, "ny": 1, "nz": 120, "scale": 0.183}
        default.update({"lx": 1.0, "ly": 1.0, "lz": 0.1})
        for key, value in default.items():
            params.block_mesh_dict[key] = value

    def make_code_block_mesh_dict(self, params):
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

    def make_tree_alpha_a(self, params):
        field = VolScalarField("alpha_a", dimension="")
        add_default_boundaries(field)
        field.set_boundary("top", "fixedValue", "uniform 0")
        field.set_codestream(code_init_alpha_a)
        return field

    def make_tree_alpha_plastic(self, params):
        field = VolScalarField("alphaMinFriction", dimension="", values=0.57)
        add_default_boundaries(field)
        return field

    def make_tree_theta(self, params):
        field = VolScalarField("Theta", dimension="m^2/s^2", values=0.0)
        add_default_boundaries(field)
        return field

    def make_tree_u_a(self, params, name="U.a"):
        field = VolVectorField(name, dimension="m/s", values=(0, 0, 0))
        add_default_boundaries(field)
        field.set_boundary("bottom", "fixedValue", "uniform (0 0 0)")
        return field

    def make_tree_u_b(self, params):
        return self.make_tree_u_a(params, name="U.b")

    def make_tree_epsilon_b(self, params):
        field = VolScalarField("epsilon", dimension="m^2/s^3", values=1e-8)
        add_default_boundaries(field)
        return field

    def make_tree_k_b(self, params):
        field = VolScalarField("k.b", dimension="m^2/s^2", values=1e-6)
        add_default_boundaries(field)
        field.set_boundary("bottom", "fixedValue", "uniform 1e-06")
        return field

    def make_tree_mu_i(self, params):
        field = VolScalarField("muI", dimension="", values=0.0)
        add_default_boundaries(field)
        return field

    def make_tree_nut_b(self, params):
        field = VolScalarField("nut.b", dimension="m^2/s^1", values=0.0)
        add_default_boundaries(field)
        field.set_boundary("bottom", "fixedValue", "uniform 0.0")
        return field

    def make_tree_omega_b(self, params):
        field = VolScalarField("omega.b", dimension="1/s", values=1e-20)
        add_default_boundaries(field)
        return field

    def make_tree_pa(self, params):
        field = VolScalarField("pa", dimension="kg/m/s^2", values=0.0)
        add_default_boundaries(field)
        field.set_boundary("top", "slip")
        return field

    def make_tree_p_rbgh(self, params):
        field = VolScalarField("p_rbgh", dimension="kg/m/s^2", values=0.0)
        add_default_boundaries(field)
        field.set_boundary("top", "fixedValue", "uniform 0.0")
        field.set_boundary(
            "bottom", "fixedFluxPressure", gradient="$internalField"
        )
        return field

    def make_tree_delta(self, params):
        field = VolScalarField("delta", dimension="", values=0.0)
        add_default_boundaries(field)
        return field
