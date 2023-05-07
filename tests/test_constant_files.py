from fluidsimfoam.foam_input_files import ConstantFileHelper
from fluidsimfoam.params import Parameters

result = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      twophaseRASProperties;
}

// Shared coefficients
SUS  SUS [0 0 0 0 0 0 0] 1;

// density stra (Uf-Us)
KE1  KE1 [0 0 0 0 0 0 0] 0;

// turb generation
KE3  KE3 [0 0 0 0 0 0 0] 0;

// turb modulation coeff
B  B [0 0 0 0 0 0 0] 0.15;

// Limiters
Tpsmall  Tpsmall [1 -3 -1 0 0 0 0] 1e-06;
"""


def test_simple():
    helper = ConstantFileHelper(
        "twophaseRASProperties",
        {"SUS": 0, "KE1": 0, "KE3": 0, "B": 0.15, "Tpsmall": 1e-6},
        default_dimension="",
        comments={
            "SUS": "Shared coefficients",
            "KE1": "density stra (Uf-Us)",
            "KE3": "turb generation",
            "B": "turb modulation coeff",
            "Tpsmall": "Limiters",
        },
        dimensions={"Tpsmall": "kg/m^3/s"},
    )

    params = Parameters("params")
    helper.complete_params(params)
    assert params.twophase_ras_properties.sus == 0

    params.twophase_ras_properties.sus = 1
    tree = helper.make_tree(params)
    assert tree.dump() == result


result_with_list = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      forceProperties;
}

// mean pressure
gradPMEAN  gradPMEAN [1 -2 -2 0 0 0 0] (490.5 0 0);

// To impose same gravity term to both phases
tilt  tilt [0 0 0 0 0 0 0] 1;

debugInfo  true;
"""


def test_with_list():
    helper = ConstantFileHelper(
        "forceProperties",
        {"gradPMEAN": [1000, 0, 0], "tilt": 1, "debugInfo": "true"},
        default_dimension="",
        comments={
            "gradPMEAN": "mean pressure",
            "tilt": "To impose same gravity term to both phases",
        },
        dimensions={"gradPMEAN": "kg/m^2/s^2"},
    )

    params = Parameters("params")
    helper.complete_params(params)
    assert params.force_properties.grad_pmean == [1000, 0, 0]

    params.force_properties.grad_pmean == [490.5, 0, 0]
    tree = helper.make_tree(params)
    assert tree.dump() == result_with_list


result_with_dict = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}

simulationType  RAS;

RAS
{
    // can be twophaseMixingLength, twophasekEpsilon or twophasekOmega
    RASModel  twophaseMixingLength;
    twophaseMixingLengthCoeffs
    {
        expoLM        1.0;
        alphaMaxLM    0.61;
        kappaLM       0.41;
    }
}
"""


def test_with_dict():
    helper = ConstantFileHelper(
        "turbulenceProperties",
        {
            "simulationType": "RAS",
            "RAS": {
                "RASModel": "twophaseMixingLength",
                "twophaseMixingLengthCoeffs": {
                    "expoLM": 1.5,
                    "alphaMaxLM": 0.61,
                    "kappaLM": 0.41,
                },
            },
        },
        comments={
            "RAS": {
                "RASModel": "can be twophaseMixingLength, twophasekEpsilon or twophasekOmega"
            }
        },
    )

    params = Parameters("params")
    helper.complete_params(params)
    p_tp = params.turbulence_properties
    assert p_tp.ras.twophase_mixing_length_coeffs.expo_lm == 1.5

    p_tp.ras.twophase_mixing_length_coeffs.expo_lm == 1.0
    tree = helper.make_tree(params)
    assert tree.dump() == result_with_list
