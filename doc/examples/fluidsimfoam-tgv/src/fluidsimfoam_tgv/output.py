from textwrap import dedent

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

    def make_tree_p(self, params):
        field = VolScalarField("p", "m^2/s^2")
        for prefix in boundary_prefixes:
            field.set_boundary(prefix + "Boundary", "cyclic")
        field.set_codestream(code_init_p)
        return field

    def make_tree_u(self, params):
        field = VolVectorField("U", "m/s")
        for prefix in boundary_prefixes:
            field.set_boundary(prefix + "Boundary", "cyclic")
        field.set_codestream(code_init_u)
        return field
