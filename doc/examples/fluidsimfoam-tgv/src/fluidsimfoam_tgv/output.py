from textwrap import dedent

import numpy as np
from numpy import cos, sin

from fluidsimfoam.foam_input_files import (
    FvSchemesHelper,
    VolScalarField,
    VolVectorField,
)
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

    helper_fv_schemes = FvSchemesHelper(
        ddt="default   backward",
        grad="default  leastSquares",
        div="""
            default         none
            div(phi,U)      Gauss linear
            div((nuEff*dev2(T(grad(U))))) Gauss linear""",
        laplacian="default  Gauss linear corrected",
        interpolation="default  linear",
        sn_grad="default  corrected",
    )

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
            field.set_values(-0.0625 * (cos(2 * x) + cos(2 * y)) * cos(2 * z + 2))
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
            vx = sin(x) * cos(y) * cos(z)
            vy = -cos(x) * sin(y) * cos(z)
            vz = np.zeros_like(x)
            field.set_values(vx, vy, vz)
        else:
            ValueError

        return field
