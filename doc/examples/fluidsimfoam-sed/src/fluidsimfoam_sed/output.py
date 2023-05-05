from textwrap import dedent

import numpy as np
from inflection import underscore

from fluidsimfoam.foam_input_files import FoamInputFile
from fluidsimfoam.foam_input_files.blockmesh import BlockMeshDict
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

    @classmethod
    def _complete_params_alpha_a(cls, params):
        params._set_child(
            "init_fields",
            attribs={"type": "tanh", "width": 0.005},
            doc="""type have to be in ['tanh', 'codestream']""",
        )

    def make_tree_alpha_a(self, params):
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

    def make_tree_alpha_plastic(self, params):
        return make_scalar_field("alphaMinFriction", dimension="", values=0.57)

    def make_tree_delta(self, params):
        return make_scalar_field("delta", dimension="", values=0.0)

    def make_tree_mu_i(self, params):
        return make_scalar_field("muI", dimension="", values=0.0)

    def make_tree_u_a(self, params, name="U.a"):
        field = VolVectorField(name, dimension="m/s", values=(0, 0, 0))
        add_default_boundaries(field)
        field.set_boundary("bottom", "fixedValue", "uniform (0 0 0)")
        return field

    def make_tree_u_b(self, params):
        return self.make_tree_u_a(params, name="U.b")

    def make_tree_omega_b(self, params):
        return make_scalar_field("omega.b", dimension="1/s", values=1e-20)

    def make_tree_theta(self, params):
        return make_scalar_field("Theta", dimension="m^2/s^2", values=0.0)

    def make_tree_epsilon_b(self, params):
        return make_scalar_field("epsilon", dimension="m^2/s^3", values=1e-8)

    def make_tree_k_b(self, params):
        field = make_scalar_field("k.b", dimension="m^2/s^2", values=1e-6)
        field.set_boundary("bottom", "fixedValue", "uniform 1e-06")
        return field

    def make_tree_nut_b(self, params):
        field = make_scalar_field("nut.b", dimension="m^2/s^1", values=0.0)
        field.set_boundary("bottom", "fixedValue", "uniform 0.0")
        return field

    def make_tree_pa(self, params):
        field = make_scalar_field("pa", dimension="kg/m/s^2", values=0.0)
        field.set_boundary("top", "slip")
        return field

    def make_tree_p_rbgh(self, params):
        field = make_scalar_field("p_rbgh", dimension="kg/m/s^2", values=0.0)
        field.set_boundary("top", "fixedValue", "uniform 0.0")
        field.set_boundary(
            "bottom", "fixedFluxPressure", gradient="$internalField"
        )
        return field

    default_pp_prop = {
        "alphaMax": 0.635,
        "alphaMinFriction": 0.57,
        "Fr": 5e-2,
        "eta0": 3,
        "eta1": 5,
    }

    @classmethod
    def _complete_params_pp_properties(cls, params):
        params._set_attribs(
            {
                underscore(name): value
                for name, value in cls.default_pp_prop.items()
            }
        )

    def make_tree_pp_properties(self, params):
        tree = FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "location": '"constant"',
                "object": "ppProperties",
            }
        )
        tree.set_value("ppModel", "JohnsonJackson")
        for name in self.default_pp_prop.keys():
            key = underscore(name)
            dimension = "" if name != "Fr" else "kg/m/s^2"
            tree.set_value(name, params[key], dimension=dimension)
        tree.set_value("packingLimiter", "no")
        return tree
