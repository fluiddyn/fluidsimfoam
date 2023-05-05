from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from fluidsimfoam.foam_input_files.fv_schemes import FvSchemesHelper
from fluidsimfoam.params import Parameters

result = dedent(
    r"""
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      fvSchemes;
    }

    ddtSchemes
    {
        default    Euler;
    }

    gradSchemes
    {
    }

    divSchemes
    {
        div(phi,T)    Gauss limitedLinear 1;
        div(phi,U)    foo;
        div(phi,k)    $turbulence;
    }

    laplacianSchemes
    {
    }

    interpolationSchemes
    {
    }

    snGradSchemes
    {
    }
"""
)


def test_simple():
    params = Parameters("params")

    fv_scheme_helper = FvSchemesHelper(
        ddt={"default": "Euler"},
        div={
            "default": "none",
            "div(phi,U)": "Gauss linearUpwind grad(U)",
            "div(phi,T)": "Gauss limitedLinear 1",
        },
    )
    fv_scheme_helper.complete_params(params)

    with TemporaryDirectory() as path_tmp_dir:
        path_tmp_dir = Path(path_tmp_dir)

        path_tmp = path_tmp_dir / "tmp.xml"
        params._save_as_xml(path_tmp)
        params_loaded_from_xml = Parameters(path_file=path_tmp)

        path_tmp = path_tmp_dir / "tmp.h5"
        params._save_as_hdf5(str(path_tmp))
        params_loaded_from_h5 = Parameters(path_file=path_tmp)

    assert params_loaded_from_xml == params
    assert params_loaded_from_h5.fv_schemes.div == params.fv_schemes.div

    params.fv_schemes.div.default = "Euler"
    params.fv_schemes.div["div(phi,U)"] = "foo"

    # add a div scheme
    params.fv_schemes.div._set_attrib("div(phi,k)", "$turbulence")
    # del a div scheme
    params.fv_schemes.div._del_attrib("default")

    tree = fv_scheme_helper.make_tree(params)
    assert tree.dump().strip() == result.strip()
