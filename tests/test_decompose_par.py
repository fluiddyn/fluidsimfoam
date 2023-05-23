from textwrap import dedent

from fluidsimfoam.foam_input_files import DecomposeParDictHelper
from fluidsimfoam.params import Parameters


def test_simple():
    result = dedent(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "system";
            object      decomposeParDict;
        }

        numberOfSubdomains  8;

        method            simple;

        coeffs
        {
            n
            (
                4
                2
                1
            );
            order    xyz;
            delta    0.001;
        }
    """
    ).strip()

    helper = DecomposeParDictHelper(1, "simple")

    params = Parameters("params")
    helper.complete_params(params)
    par_params = params.parallel
    par_params.nsubdoms = 8
    par_params.nsubdoms_xyz = [4, 2, 1]

    tree = helper.make_tree(params)
    assert tree.dump().strip() == result


def test_scotch():
    result = dedent(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "system";
            object      decomposeParDict;
        }

        numberOfSubdomains  12;

        method            scotch;
    """
    ).strip()

    helper = DecomposeParDictHelper(1, "scotch")

    params = Parameters("params")
    helper.complete_params(params)
    par_params = params.parallel
    par_params.nsubdoms = 12

    tree = helper.make_tree(params)

    assert tree.dump().strip() == result
