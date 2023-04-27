from textwrap import dedent

from fluidsimfoam.foam_input_files.fields import VolScalarField

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
