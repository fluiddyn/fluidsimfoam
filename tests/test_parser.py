from pathlib import Path
from textwrap import dedent

from fluidsimfoam.of_input_files import dump, parse
from fluidsimfoam.of_input_files.ast import (
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
        check_dump=True,
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
        check_dump=True,
        check_dump_parse=True,
    )


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

        #include  "initialConditions";
    """,
        cls=FoamInputFile,
        check_dump=True,
        check_dump_parse=True,
    )


def test_simple_code_stream():
    tree = base_test(
        """
        code
        #{
            #include    "initialConditions";
        #};
        
    """,
        check_dump=True,
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


def test_reading_one_file():
    path_to_file = here / "pure_openfoam_cases/tiny-tgv/system/fvSolution"
    with open(path_to_file, "r") as file:
        text = file.read()

    tree = base_test(text, cls=FoamInputFile, check_dump=False)


# def test_loop_directory():
#     path_dirs = here / "pure_openfoam_cases/tiny-tgv/system"

#     for path_dir in path_dirs.rglob("*"):

#         with open(path_dir, "r") as file:
#             text = file.read()

#         tree = parse(text)
