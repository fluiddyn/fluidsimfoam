from fluidsimfoam.foam_input_files.fv_options import FvOptionsHelper
from fluidsimfoam.params import Parameters

result = r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      fvOptions;
}

momentumSource
{
    type      meanVelocityForce;
    active    yes;
    meanVelocityForceCoeffs
    {
        selectionMode    all;
        fields           (U);
        Ubar             (0.1 0 0);
    }
}
"""


def test_simple():
    helper = FvOptionsHelper()

    helper.add_option(
        "momentumSource",
        {
            "type": "meanVelocityForce",
            "active": "yes",
            "meanVelocityForceCoeffs": {
                "selectionMode": "all",
                "fields": "(U)",
                "Ubar": "(0.1 0 0)",
            },
        },
        parameters=["active", "meanVelocityForceCoeffs/Ubar"],
    )

    params = Parameters("params")

    helper.complete_params(params)

    momentum_source = params.fv_options.momentum_source
    assert momentum_source.active == "yes"
    assert momentum_source.mean_velocity_force_coeffs.ubar == "(0.1 0 0)"

    tree = helper.make_tree(params)

    assert tree.dump().strip() == result.strip()
