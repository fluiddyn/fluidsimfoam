from textwrap import dedent

import numpy as np

from fluidsimfoam.foam_input_files.fields import (
    VolScalarField,
    VolTensorField,
    VolVectorField,
)

code_p = dedent(
    """
    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       volScalarField;
        object      p;
    }}

    dimensions    {}[0 2 -2 0 0 0 0];

    internalField{}

    boundaryField
    {{
    }}
"""
).strip()


def test_p():
    field = VolScalarField("p", "m^2.s^-2")

    assert field.dump().strip() == code_p.format("   ", "")

    field.set_values(2.0)
    assert field.dump().strip() == code_p.format("   ", "    uniform 2.0;")

    field.set_values([1.0, 2.0, 3.0])
    result = " nonuniform\nList<scalar>\n3\n(\n    1.0\n    2.0\n    3.0\n);"
    assert field.dump().strip() == code_p.format("", result)


code_nut = dedent(
    """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       volScalarField;
        object      nut;
    }

    dimensions       [0 2 -1 0 0 0 0];

    internalField    uniform 0;

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

    dimensions    [0 1 -1 0 0 0 0];

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

    dimensions    [0 1 -1 0 0 0 0];

    internalField   nonuniform List<vector>
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


code_cells_centers = dedent(
    r"""
    /*--------------------------------*- C++ -*----------------------------------*\
    | =========                 |                                                 |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  2212                                  |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/
    FoamFile
    {
        version     2.0;
        format      ascii;
        arch        "LSB;label=32;scalar=64";
        class       volVectorField;
        location    "0";
        object      C;
    }
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    dimensions      [0 1 0 0 0 0 0];

    internalField   nonuniform List<vector>
    14
    (
    (0.0785398163397 0.0785398163397 0.0785398163396)
    (0.235619449019 0.0785398163398 0.0785398163397)
    (0.392699081699 0.0785398163399 0.07853981634)
    (0.549778714378 0.07853981634 0.0785398163399)
    (0.706858347058 0.07853981634 0.0785398163399)
    (0.863937979737 0.0785398163398 0.0785398163398)
    (1.02101761242 0.0785398163395 0.0785398163397)
    (1.1780972451 0.0785398163397 0.0785398163399)
    (1.33517687778 0.0785398163399 0.07853981634)
    (1.49225651046 0.0785398163397 0.0785398163398)
    (1.64933614314 0.0785398163398 0.0785398163398)
    (1.80641577581 0.0785398163398 0.0785398163399)
    (1.96349540849 0.0785398163397 0.0785398163398)
    (2.12057504117 0.0785398163396 0.0785398163398)
    )
    ;

    boundaryField
    {
        upperBoundary
        {
            type            calculated;
            value           nonuniform List<vector>
    2
    (
    (50 8000 0.005)
    (150 8000 0.005)
    )
    ;
        }
        lowerBoundary
        {
            type            cyclic;
        }
        leftBoundary
        {
            type            cyclic;
        }
        rightBoundary
        {
            type            cyclic;
        }
        frontBoundary
        {
            type            cyclic;
        }
        backBoundary
        {
            type            cyclic;
        }
    }


    // ************************************************************************* //
"""
)

code_cx = dedent(
    r"""
    /*--------------------------------*- C++ -*----------------------------------*\
    | =========                 |                                                 |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  2212                                  |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/
    FoamFile
    {
        version     2.0;
        format      ascii;
        arch        "LSB;label=32;scalar=64";
        class       volScalarField;
        location    "0";
        object      Cx;
    }
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    dimensions      [0 1 0 0 0 0 0];

    internalField   nonuniform List<scalar>
    14
    (
    0.0785398163397
    0.235619449019
    0.392699081699
    0.549778714378
    0.706858347058
    0.863937979737
    1.02101761242
    1.1780972451
    1.33517687778
    1.49225651046
    1.64933614314
    1.80641577581
    1.96349540849
    2.12057504117
    )
    ;

    boundaryField
    {
        upperBoundary
        {
            type            cyclic;
        }
        lowerBoundary
        {
            type            cyclic;
        }
        leftBoundary
        {
            type            cyclic;
        }
        rightBoundary
        {
            type            cyclic;
        }
        frontBoundary
        {
            type            cyclic;
        }
        backBoundary
        {
            type            cyclic;
        }
    }


    // ************************************************************************* //
"""
)


def test_cells_centers():
    """Data obtained with `postProcess -func writeCellCentres`

    https://www.openfoam.com/documentation/guides/latest/doc/guide-fos-field-writeCellCentres.html

    """
    field_c = VolVectorField.from_code(code_cells_centers)
    field_cx = VolScalarField.from_code(code_cx)

    field_c = VolVectorField.from_code(
        code_cells_centers, skip_boundary_field=True
    )
    field_cx = VolScalarField.from_code(code_cx, skip_boundary_field=True)

    c_values = field_c.get_array()
    cx_values = field_cx.get_array()

    assert np.allclose(c_values[:, 0], cx_values)

    x, y, z = field_c.get_components()
    assert np.allclose(x, cx_values)


def test_tensor():
    field = VolTensorField("tensor", "")
    arr = np.ones((10, 9))
    field.set_values(arr)
