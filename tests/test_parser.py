from pathlib import Path
from textwrap import dedent

import pytest

from fluidsimfoam.foam_input_files import dump, parse
from fluidsimfoam.foam_input_files.ast import (
    Assignment,
    Dict,
    DimensionSet,
    FoamInputFile,
    Node,
    Value,
    VariableAssignment,
)

here = Path(__file__).absolute().parent


def base_test(
    text, representation=None, cls=None, check_dump=False, check_dump_parse=False
):
    tree = parse(text)
    if isinstance(tree, FoamInputFile):
        assert all(
            isinstance(obj, (Node, str, int, float)) for obj in tree.children
        )
    if representation is not None:
        assert repr(tree) == representation
    if cls is not None:
        assert isinstance(tree, cls)
    if check_dump:
        dump_text = dump(tree)
        assert dedent(text).strip() == dump_text.strip()
    if check_dump_parse:
        assert tree == parse(dump(tree))

    return tree


def test_var_simple():
    tree = base_test(
        """
        a  b;
    """,
        cls=VariableAssignment,
        check_dump=True,
    )


def test_var_multiple():
    tree = base_test(
        """
        a  b;
        c  d;
    """,
        representation="InputFile(\nchildren={'a': 'b', 'c': 'd'}\n)",
        cls=FoamInputFile,
        check_dump=True,
    )


def test_list_simple():
    tree = base_test(
        """
        faces
        (
            (1 5 4 0)
            (2 3 4 5)
        );
    """,
        cls=Assignment,
        check_dump_parse=True,
    )


def test_list_assignment():
    tree = base_test(
        """
        faces  (1 5 4 0);
    """,
        cls=Assignment,
        check_dump=True,
    )


def test_file_simple():
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            object      blockMeshDict;
        }

        // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

        a  b;
        c  d;
    """,
        cls=FoamInputFile,
    )


def test_var_value_with_space():
    tree = base_test(
        """
        laplacianSchemes
        {
            default         Gauss linear corrected;
        }
    """,
        check_dump_parse=True,
    )
    assert tree.value["default"] == "Gauss linear corrected"


def test_dict_simple():
    # we add a space on purpose...
    space = " "
    tree = base_test(
        f"""
        my_dict{space}
        {{
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "system";
            object      controlDict;
        }}
    """,
        cls=Assignment,
        check_dump_parse=True,
    )

    my_dict = tree.value
    assert isinstance(my_dict, Dict)
    assert my_dict["version"] == 2.0
    assert my_dict["format"] == "ascii"
    assert my_dict["location"] == '"system"'


@pytest.mark.xfail
def test_dict_strange_keys():
    """As in fvSchemes"""
    tree = base_test(
        """
        divSchemes
        {
            default         none;
            div(phi,U)      Gauss linear;
            div((nuEff*dev2(T(grad(U))))) Gauss linear;
        }
    """,
        check_dump_parse=True,
    )


def test_dict_nested():
    tree = base_test(
        """
        my_nested_dict
        {
            p
            {
                solver            PCG;
                preconditioner    DIC;
                tolerance         1e-06;
                relTol            0.05;
            }

            U
            {
                solver       smoothSolver;
                smoother     symGaussSeidel;
                tolerance    1e-05;
                relTol       0;
            }

        }
    """,
        cls=Assignment,
        check_dump=True,
        check_dump_parse=True,
    )

    my_nested_dict = tree.value
    assert my_nested_dict["p"]["solver"] == "PCG"
    assert my_nested_dict["U"]["tolerance"] == 1e-05


def test_dict_with_list():
    tree = base_test(
        """
        PISO
        {
            nCorrectors                 2;
            nNonOrthogonalCorrectors    1;
            pRefPoint                   (0 0 0);
            pRefValue                   0;
        }
    """,
        cls=Assignment,
        check_dump_parse=True,
    )
    assert tree.value["pRefPoint"]._name == "pRefPoint"


def test_list_with_dict():
    base_test(
        """
    boundary
    (

    upperBoundary
    {
        type cyclic;
        neighbourPatch lowerBoundary;
        faces
        (
            (3 7 6 2)
        );
    }
    );
    """,
        cls=Assignment,
        check_dump_parse=True,
    )


def test_file():
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        a  1;
        b  2;

        faces
        (
            (1 5 4 0)
            (2 3 4 5)
        );

        my_dict
        {
            a    1;
        }
    """,
        cls=FoamInputFile,
        check_dump_parse=True,
    )
    assert tree.children["my_dict"]["a"] == 1


def test_directive():
    base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        #include  "initialConditions";
    """,
        cls=FoamInputFile,
        check_dump=True,
        check_dump_parse=True,
    )


def test_code():
    base_test(
        r"""
        code_name
        #{
            -I$(LIB_SRC)/finiteVolume/lnInclude \
            -I$(LIB_SRC)/meshTools/lnInclude
        #};
    """,
        check_dump=True,
        check_dump_parse=True,
    )


def test_code_stream():
    tree = base_test(
        r"""
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
                scalarField p(mesh.nCells(), 0.);
                forAll(p, i)
                {
                    const scalar x = mesh.C()[i][0];
                    const scalar y = mesh.C()[i][1];
                    const scalar z = mesh.C()[i][2];
                    p[i]=-0.0625*(Foam::cos(2*x) + Foam::cos(2*y))*Foam::cos(2*z+2);
                }
                p.writeEntry("",os);
            #};
        };
""",
        check_dump_parse=True,
    )


def test_macro():
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        relTol  $p;
    """,
        check_dump=True,
    )


def test_dimension_set():
    tree = base_test(
        """
        dimension  [0 2 -1 0 0 0 0];
        nu  [0 2 -1 0 0 0 0] 1e-05;
        nu1  nu [0 2 -1 0 0 0 0] 1e-06;
        """,
        cls=FoamInputFile,
        check_dump=True,
        check_dump_parse=True,
    )
    assert isinstance(tree.children["nu"], Value)
    assert isinstance(tree.children["dimension"], DimensionSet)


path_tiny_tgv = here / "pure_openfoam_cases/tiny-tgv"


def test_reading_one_file():
    path_to_file = path_tiny_tgv / "system/fvSolution"
    with open(path_to_file, "r") as file:
        text = file.read()

    tree = base_test(text, cls=FoamInputFile, check_dump=False)
    assert tree.info["object"] == "fvSolution"
    assert tree.children["solvers"]["U"]["solver"] == "PBiCGStab"


paths_tiny_tgv = {
    path.name: path
    for path in path_tiny_tgv.rglob("*")
    if path.is_file() and "README" not in path.name
}


@pytest.mark.xfail
@pytest.mark.parametrize("path_name", paths_tiny_tgv)
def test_tiny_tgv(path_name):
    path = paths_tiny_tgv[path_name]
    text = path.read_text()
    tree = parse(text)
