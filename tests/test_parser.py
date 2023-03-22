from pathlib import Path
from textwrap import dedent

from fluidsimfoam.of_input_files import dump, parse
from fluidsimfoam.of_input_files.ast import OFInputFile, VariableAssignment

here = Path(__file__).absolute().parent


def base_test(text):
    tree = parse(text)
    # dump_text = dump(tree)
    # assert repr(tree) == """..."""
    # assert dedent(text.replace("\n", "")) == dedent(dump_text)
    return tree


def test_var_simple():
    tree = base_test(
        """
        a  b;
    """
    )
    assert isinstance(tree, VariableAssignment)
    assert tree.name == "a"
    assert tree.value == "b"


def test_var_multiple():
    tree = base_test(
        """
        a  b;
        c  d;
    """
    )


def test_list_simple():
    text = """
        faces
        (
            (1 5 4 0)
            (1 5 4 0)
            (1 5 4 0)
        );
    """
    tree = parse(text)


def test_dict_with_var_simple():
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            object      blockMeshDict;
        }
        a  b;
        c  d;
    """
    )

    assert isinstance(tree, OFInputFile)
    assert tree.children["a"] == "b"


def test_var_multiple():
    text = """
        laplacianSchemes
        {
            default         Gauss linear corrected;
        }
    """
    tree = parse(text)
    assert isinstance(tree.value, dict)
    assert tree.value["default"] == "Gauss linear corrected"


def test_dict_simple():
    text = """
        my_dict
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "system";
            object      controlDict;
        }
    """
    tree = parse(text)


def test_dict_nested():
    text = """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

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
    """
    tree = parse(text)
    assert tree.info["format"] == "ascii"
    assert tree.children["my_nested_dict"]["p"]["solver"] == "PCG"
    assert tree.children["my_nested_dict"]["U"]["tolerance"] == 1e-05


def test_file():
    tree = parse(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        a 1;
        b 2;
    """
    )

    assert tree.info == {
        "version": 2.0,
        "format": "ascii",
        "class": "volScalarField",
        "object": "p",
    }
    assert tree.children == {"a": 1, "b": 2}


def test_directive():
    text = """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        #include "initialConditions"
    """
    tree = parse(text)
    assert tree.children == {"include": "initialConditions"}


def test_macro():
    text = """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }
        
        relTol          $p;
    """
    tree = parse(text)
    assert tree.children == {"relTol": "p"}


def test_dimension_set():
    text = """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            location    "constant";
            object      transportProperties;
        }
        // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

        transportModel  Newtonian;
        nu             nu [ 0 2 -1 0 0 0 0 ] 1e-06;    // for comment test
        Cvm             Cvm [ 0 0 0 0 0 ] 0;                // Virtual/Added Mass coefficient
    """
    tree = parse(text)

    assert tree.info == {
        "version": 2.0,
        "format": "ascii",
        "class": "dictionary",
        "location": "constant",
        "object": "transportProperties",
    }
    assert tree.children["nu"] == [[0, 2, -1, 0, 0, 0, 0], 1e-06]


def test_assign_with_dimension_set():
    ...


# # def test_reading_file():
# #     path_to_file = here / "pure_openfoam_cases/tiny-tgv"
