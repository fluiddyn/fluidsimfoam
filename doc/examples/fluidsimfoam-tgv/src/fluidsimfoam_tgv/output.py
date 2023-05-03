from textwrap import dedent

import numpy as np

from fluidsimfoam.foam_input_files.fields import VolScalarField, VolVectorField
from fluidsimfoam.output import Output

code_control_dict_functions = dedent(
    """
    functions
    {
        minmaxdomain
        {
            type fieldMinMax;
            //type banana;

            libs ("libfieldFunctionObjects.so");

            enabled true;

            mode component;

            writeControl timeStep;
            writeInterval 1;

            log true;

            fields (p U);
        }
    };
"""
)

boundary_prefixes = ("upper", "lower", "left", "right", "front", "back")

code_init_p = dedent(
    """
    const IOdictionary& d = static_cast<const IOdictionary&>(dict);
    const fvMesh& mesh = refCast<const fvMesh>(d.db());
    scalarField p(mesh.nCells(), 0.);
    forAll(p, i)
    {
        const scalar x = mesh.C()[i][0];
        const scalar y = mesh.C()[i][1];
        const scalar z = mesh.C()[i][2];
        p[i]=-0.0625*(Foam::cos(2*x) + Foam::cos(2*y))*Foam::cos(2*z+2);
    }
    p.writeEntry("",os);
"""
)

code_init_u = dedent(
    """
    const IOdictionary& d = static_cast<const IOdictionary&>(dict);
    const fvMesh& mesh = refCast<const fvMesh>(d.db());
    vectorField U(mesh.nCells(), Foam::Vector<double>(0.,0.,0.));
    forAll(U, i)
    {
        const scalar x = mesh.C()[i][0];
        const scalar y = mesh.C()[i][1];
        const scalar z = mesh.C()[i][2];
        U[i] = Foam::Vector<double>(Foam::sin(x)
        *Foam::cos(y)*Foam::cos(z), -Foam::cos(x)
        *Foam::sin(y)*Foam::cos(z), 0.);
    }
    U.writeEntry("",os);
"""
)


class OutputTGV(Output):
    """Output for the TGV solver"""

    system_files_names = Output.system_files_names + ["blockMeshDict"]

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    def make_code_control_dict(self, params):
        code = super().make_code_control_dict(params)
        return code + code_control_dict_functions

    @classmethod
    def _complete_params_fv_solution(cls, params):
        params._set_child("fv_solution", doc="""TODO""")
        solvers = params.fv_solution._set_child("solvers", doc="""TODO""")
        attribs = {
            "solver": "PCG",
            "preconditioner": "DIC",
            "tolerance": 1e-06,
            "relTol": 0.01,
        }

        solvers._set_child("p", attribs=attribs)
        solvers._set_child("pFinal", attribs=attribs)
        solvers.pFinal.relTol = 0
        solvers._set_child(
            "U",
            attribs={
                "solver": "PBiCGStab",
                "preconditioner": "DILU",
                "tolerance": 1e-08,
                "relTol": 0,
            },
        )

        params.fv_solution._set_child(
            "piso",
            attribs={
                "nCorrectors": 2,
                "nNonOrthogonalCorrectors": 1,
                "pRefPoint": "(0 0 0)",
                "pRefValue": 0,
            },
        )

    @classmethod
    def _complete_params_fv_schemes(cls, params):
        fv_schemes = params._set_child("fv_schemes", doc="""TODO""")
        fv_schemes._set_child("ddtSchemes", attribs={"default": "backward"})
        fv_schemes._set_child("gradSchemes", attribs={"default": "leastSquares"})
        fv_schemes._set_child("divSchemes", attribs={"default": "none"})
        fv_schemes._set_child(
            "laplacianSchemes", attribs={"default": "Gauss linear corrected"}
        )
        fv_schemes._set_child(
            "interpolationSchemes", attribs={"default": "linear"}
        )
        fv_schemes._set_child("snGradSchemes", attribs={"default": "corrected"})

    @classmethod
    def _complete_params_p(cls, params):
        params._set_child(
            "init_fields",
            attribs={"type": "from_py", "amplitude": 1.0},
            doc="""type have to be in ['from_py', 'codestream']""",
        )

    def make_tree_p(self, params):
        field = VolScalarField("p", "m^2/s^2")
        for prefix in boundary_prefixes:
            field.set_boundary(prefix + "Boundary", "cyclic")

        if params.init_fields.type == "codestream":
            field.set_codestream(code_init_p)
        elif params.init_fields.type == "from_py":
            x, y, z = self.sim.oper.get_cells_coords()
            p = -0.0625 * (np.cos(2 * x) + np.cos(2 * y)) * np.cos(2 * z + 2)
            field.set_values(list(p))
        else:
            ValueError

        return field

    def make_tree_u(self, params):
        field = VolVectorField("U", "m/s")
        for prefix in boundary_prefixes:
            field.set_boundary(prefix + "Boundary", "cyclic")

        if params.init_fields.type == "codestream":
            field.set_codestream(code_init_u)
        elif params.init_fields.type == "from_py":
            x, y, z = self.sim.oper.get_cells_coords()
            vxs = np.sin(x) * np.cos(y) * np.cos(z)
            vys = -np.cos(x) * np.sin(y) * np.cos(z)
            vzs = np.zeros_like(x)
            values = [(vx, vy, vz) for vx, vy, vz in zip(vxs, vys, vzs)]
            field.set_values(values)
        else:
            ValueError

        return field
