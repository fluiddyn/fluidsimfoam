from textwrap import dedent

from fluidsimfoam.foam_input_files.fields import VolScalarField, VolVectorField

code_p = dedent(
    """
    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       volScalarField;
        object      p;
    }}

    dimensions  [0 2 -2 0 0 0 0];

    internalField{}

    boundaryField
    {{
    }}
"""
).strip()


def test_p():
    field = VolScalarField("p", "m^2.s^-2")

    assert field.dump().strip() == code_p.format("")

    field.set_values(2.0)
    assert field.dump().strip() == code_p.format("  uniform 2.0;")

    field.set_values([1.0, 2.0, 3.0])
    result = " nonuniform\nList<scalar>\n3\n(\n    1.0\n    2.0\n    3.0\n);"
    assert field.dump().strip() == code_p.format(result)


code_nut = dedent(
    """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       volScalarField;
        object      nut;
    }

    dimensions  [0 2 -1 0 0 0 0];

    internalField  uniform 0;

    boundaryField
    {
        wall
        {
            type     nutkWallFunction;
            value    $internalField;
        }
        #includeEtc    "caseDicts/setConstraintTypes";
    }
"""
)


def test_nut():
    field = VolScalarField("nut", "m^2/s")
    field.set_values(0)
    field.set_boundary("wall", "nutkWallFunction", "$internalField")

    field.tree.children["boundaryField"][
        "#includeEtc"
    ] = '"caseDicts/setConstraintTypes"'

    assert field.dump().strip() == code_nut.strip()


code_u = dedent(
    r"""
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       volVectorField;
        object      U;
    }

    dimensions  [0 1 -1 0 0 0 0];

    internalField  #codeStream
    {
        codeInclude
        #{
            #include "fvCFD.H"
        #};
        codeOptions
        #{
            -I$(LIB_SRC)/finiteVolume/lnInclude \
            -I$(LIB_SRC)/meshTools/lnInclude
        #};
        codeLibs
        #{
            -lmeshTools \
            -lfiniteVolume
        #};
        code
        #{
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
        #};
    };

    boundaryField
    {
        upperBoundary
        {
            type    cyclic;
        }
        lowerBoundary
        {
            type    cyclic;
        }
        leftBoundary
        {
            type    cyclic;
        }
        rightBoundary
        {
            type    cyclic;
        }
        frontBoundary
        {
            type    cyclic;
        }
        backBoundary
        {
            type    cyclic;
        }
    }
"""
)


def test_u():
    field = VolVectorField("U", "m/s")

    field.set_codestream(
        dedent(
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
    )

    for prefix in ("upper", "lower", "left", "right", "front", "back"):
        field.set_boundary(prefix + "Boundary", "cyclic")

    assert field.dump().strip() == code_u.strip()


code_vector = dedent(
    r"""
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       volVectorField;
        object      U;
    }

    dimensions  [0 1 -1 0 0 0 0];

    internalField nonuniform
    List<vector>
    3
    (
        (-1 2 3)
        (-2 4 6)
        (-3 6 9)
    );

    boundaryField
    {
    }
"""
)


def test_vector():
    field = VolVectorField("U", "m/s")
    field.set_values([[-i, 2 * i, 3 * i] for i in range(1, 4)])
    assert field.dump().strip() == code_vector.strip()
