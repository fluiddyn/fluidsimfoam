from fluidsimfoam.of_input_files import parse


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


def test_macro():
    text = """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        type fixedValue;
        value $internalField;
    """
    tree = parse(text)
    assert tree.children == {"type": "fixedValue", "value": "internalField"}


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
        nu             [ 0 2 -1 0 0 0 0 ] 0.000625;
    """
    tree = parse(text)

    assert tree.info == {
        "version": 2.0,
        "format": "ascii",
        "class": "dictionary",
        "location": "constant",
        "object": "transportProperties",
    }
    assert tree.children == {"transportModel": "Newtonian", "nu": 0.000625}


def test_assign_with_dimension_set():
    ...
