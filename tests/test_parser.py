from pathlib import Path
from textwrap import dedent

from fluidsimfoam.of_input_files import dump, parse
from fluidsimfoam.of_input_files.ast import (
    Assignment,
    Dict,
    DimensionSet,
    OFInputFile,
    Value,
    VariableAssignment,
)

here = Path(__file__).absolute().parent


def base_test(text, representation=None, cls=None, check_dump=False):
    tree = parse(text)
    if representation is not None:
        assert repr(tree) == representation
    if cls is not None:
        assert isinstance(tree, cls)
    if check_dump:
        dump_text = dump(tree)
        assert dedent(text).strip() == dump_text.strip()
    return tree


def test_var_simple():
    tree = base_test(
        """
        a b;
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
        cls=OFInputFile,
        check_dump=True,
    )


def test_list_simple():
    tree = base_test(
        """
        faces
        (
            (1 5 4 0)
            (1 5 4 0)
        );
    """,
        cls=Assignment,
    )
    assert tree.name == "faces"
    assert tree.value == [[1, 5, 4, 0], [1, 5, 4, 0]]


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
        cls=OFInputFile,
    )
    assert tree.info["version"] == 2.0


def test_var_value_with_space():
    tree = base_test(
        """
        laplacianSchemes
        {
            default         Gauss linear corrected;
        }
    """
    )
    assert tree.value["default"] == "Gauss linear corrected"


def test_dict_simple():
    tree = base_test(
        """
        my_dict
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "system";
            object      controlDict;
        }
    """,
        cls=Assignment,
        check_dump=True,
    )
    my_dict = tree.value
    # TODO: fixme
    assert isinstance(my_dict, Dict)
    assert my_dict["version"] == 2.0
    assert my_dict["format"] == "ascii"
    assert my_dict["location"] == '"system"'


def test_dict_nested():
    tree = base_test(
        """
        my_nested_dict
        {
            p
            {
                solver          PCG;
                preconditioner  DIC;
                tolerance       1e-06;
                relTol          0.05;
            }

            U
            {
                solver          smoothSolver;
                smoother        symGaussSeidel;
                tolerance       1e-05;
                relTol          0;
            }
        }
    """,
        cls=Assignment,
    )
    my_nested_dict = tree.value
    assert my_nested_dict["p"]["solver"] == "PCG"
    assert my_nested_dict["U"]["tolerance"] == 1e-05


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
    """,
        cls=OFInputFile,
        # TODO: fixme
        check_dump=True,
    )

    assert tree.info == {
        "version": 2.0,
        "format": "ascii",
        "class": "volScalarField",
        "object": "p",
    }
    assert tree.children == {"a": 1, "b": 2}


def test_directive():
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        #include "initialConditions"
    """
    )
    assert tree.children == {"include": '"initialConditions"'}


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

        relTol          $p;
    """
    )
    assert tree.children == {"relTol": "p"}


def test_dimension_set():
    tree = base_test(
        """
        dimension       [0 2 -1 0 0 0 0];
        transportModel  Newtonian;
        nu              nu [0 2 -1 0 0 0 0] 1e-06;  // for comment test
        Cvm             [0 0 0 0 0 0 0] 0;  // Virtual/Added Mass coefficient
    """
    )
    assert tree.children["nu"] == Value(
        1e-06, name="nu", dimension=[0, 2, -1, 0, 0, 0, 0]
    )
    assert isinstance(tree.children["dimension"], DimensionSet)


def test_reading_one_file():
    path_to_file = here / "pure_openfoam_cases/tiny-tgv/system/fvSolution"
    with open(path_to_file, "r") as file:
        text = file.read()

    tree = parse(text)
    assert tree.info["object"] == "fvSolution"
    assert tree.children["solvers"]["U"]["solver"] == "PBiCGStab"
    assert tree.children["PISO"]["pRefPoint"] == [0, 0, 0]


# def test_loop_directory():
#     path_dirs = here / "pure_openfoam_cases/tiny-tgv/system"

#     for path_dir in path_dirs.rglob("*"):

#         with open(path_dir, "r") as file:
#             text = file.read()

#         tree = parse(text)
