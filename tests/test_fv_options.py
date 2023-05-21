from textwrap import dedent

from fluidsimfoam.foam_input_files.fv_options import FvOptionsHelper
from fluidsimfoam.params import Parameters

header = r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvOptions;
}
"""

result = (
    header
    + r"""
momentumSource
{
    type             meanVelocityForce;
    active           yes;
    selectionMode    all;
    fields           (U);
    Ubar             (0.1 0 0);
}
"""
)


def test_mean_velo_force():
    helper = FvOptionsHelper()

    helper.add_option(
        "meanVelocityForce",
        name="momentumSource",
        default={
            "fields": "(U)",
            "Ubar": "(0.2 0 0)",
        },
        parameters=["Ubar"],
    )

    params = Parameters("params")

    helper.complete_params(params)

    momentum_source = params.fv_options.momentum_source
    assert momentum_source.active is True
    assert momentum_source.ubar == "(0.2 0 0)"

    momentum_source.ubar = "(0.1 0 0)"
    tree = helper.make_tree(params)
    assert tree.dump().strip() == result.strip()


def test_disk():
    result = header + dedent(
        r"""
            disk1
            {
                type             rotorDiskSource;
                active           yes;
                selectionMode    cellSet;
                cellSet          rotorDisk1;
                fields           (U);
            }
    """
    )

    helper = FvOptionsHelper()
    helper.add_option(
        "rotorDiskSource",
        name="disk1",
        cell_set="rotorDisk1",
        default={"fields": "(U)"},
    )
    params = Parameters("params")
    helper.complete_params(params)
    tree = helper.make_tree(params)
    assert tree.dump().strip() == result.strip()


def test_fixed_value():
    result = header + dedent(
        r"""
            fixedValue
            {
                type             scalarFixedValueConstraint;
                active           no;
                selectionMode    cellZone;
                cellZone         porosity;
                fieldValues
                {
                    k          1;
                    epsilon    150;
                }
            }
    """
    )
    helper = FvOptionsHelper()
    helper.add_option(
        "scalarFixedValueConstraint",
        name="fixedValue",
        cell_zone="porosity",
        default={"fieldValues": {"k": 2, "epsilon": 150}},
        parameters=["fieldValues/k", "fieldValues/epsilon"],
    )
    params = Parameters("params")
    helper.complete_params(params)
    params.fv_options.fixed_value.active = False
    params.fv_options.fixed_value.field_values.k = 1
    tree = helper.make_tree(params)
    assert tree.dump().strip() == result.strip()


def test_explicit_porosity():
    result = header + dedent(
        r"""
            porosity
            {
                type      explicitPorositySource;
                active    yes;
                explicitPorositySourceCoeffs
                {
                    selectionMode    cellZone;
                    cellZone         porosity;
                    type             fixedCoeff;
                    fixedCoeffCoeffs
                    {
                        alpha     (500 -1000 -1000);
                        beta      (0 0 0);
                        rhoRef    1;
                        coordinateSystem
                        {
                            origin    (0 0 0);
                            e1        (0.70710678 0.70710678 0);
                            e2        (0 0 1);
                        }
                    }
                }
            }
    """
    )
    helper = FvOptionsHelper()
    helper.add_option(
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
        parameters=["coeffs/alpha"],
    )
    params = Parameters("params")
    helper.complete_params(params)
    params.fv_options.porosity.active = True
    tree = helper.make_tree(params)
    assert tree.dump().strip() == result.strip()
