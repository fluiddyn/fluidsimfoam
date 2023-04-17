from functools import partial
from textwrap import dedent

from lark.exceptions import LarkError

from fluidsimfoam.foam_input_files import dump, parse
from fluidsimfoam.foam_input_files.ast import (
    Assignment,
    CodeStream,
    Dict,
    DimensionSet,
    FoamInputFile,
    Node,
    Value,
    VariableAssignment,
)


def base_test(
    text,
    representation=None,
    cls=None,
    check_dump=False,
    check_dump_parse=False,
    grammar=None,
):
    tree = parse(text, grammar=grammar)
    text = dedent(text)
    if isinstance(tree, FoamInputFile):
        assert all(
            isinstance(obj, (Node, str, int, float, type(None)))
            for obj in tree.children.values()
        ), tree
        assert all(
            isinstance(key, (type(None), str)) for key in tree.children.keys()
        ), tree

    if representation is not None:
        grammar
    if check_dump or check_dump_parse:
        dumped_text = dump(tree)
    if check_dump:
        assert dedent(text).strip() == dumped_text.strip()
    if check_dump_parse:
        try:
            assert tree == parse(dumped_text, grammar=grammar)
        except LarkError as err:
            raise RuntimeError from err
    return tree


base_test_simple = partial(base_test, grammar="simple")


def test_var_simple():
    tree = base_test_simple(
        """
        a  b;
    """,
        cls=VariableAssignment,
        check_dump=True,
    )


def test_var_quoted_string():
    tree = base_test_simple(
        """
        laplacianSchemes
        {
            default    "Gauss linear corrected";
        }
    """,
        check_dump=True,
    )
    assert tree.value["default"] == '"Gauss linear corrected"'


def test_var_multiple():
    tree = base_test_simple(
        """
        a  b;
        c  d;
    """,
        representation="InputFile(\nchildren={'a': 'b', 'c': 'd'}\n)",
        cls=FoamInputFile,
        check_dump=True,
    )


def test_strange_names():
    tree = base_test_simple(
        """
        "(U|k|epsilon|R)Final"
        {
            $U;
            tolerance    1e-07;
            relTol       0;
        }

        thermalPhaseChange:dmdtf  1.0;
        thermo:rho
        {
            solver    PCG;
        }

        alpha.water
        {
            solver    PCG;
        }

    """,
        check_dump=True,
    )


def test_list_simple():
    tree = base_test_simple(
        """
        faces
        (
            (1 5 4 0)
            (2 3 4 5)
        );
    """,
        cls=Assignment,
        check_dump=True,
    )


def test_list_assignment():
    tree = base_test_simple(
        """
        faces  (1 5 4 0);
    """,
        cls=Assignment,
        check_dump=True,
    )


def test_dict_simple():
    # we add a space on purpose...
    space = " "
    tree = base_test_simple(
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


def test_dict_nested():
    tree = base_test_simple(
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
    )

    my_nested_dict = tree.value
    assert my_nested_dict["p"]["solver"] == "PCG"
    assert my_nested_dict["U"]["tolerance"] == 1e-05


def test_dict_with_list():
    tree = base_test_simple(
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
    base_test_simple(
        """
    boundary
    (
        upperBoundary
        {
            type              cyclic;
            neighbourPatch    lowerBoundary;
            faces
            (
                (3 7 6 2)
            );

        }

    );
    """,
        cls=Assignment,
        check_dump=True,
    )


def test_list_with_str():
    base_test_simple(
        """
        blocks
        (
            hex (0 1 2 3 4 5 6 7) (40 40 40) simpleGrading (1 1 1)
        );
    """,
        check_dump=True,
    )


def test_file_simple():
    tree = base_test_simple(
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
    """,
        cls=FoamInputFile,
    )


def test_file():
    tree = base_test_simple(
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
    )
    assert tree.children["my_dict"]["a"] == 1


def test_directive():
    base_test_simple(
        """
        FoamFile
        {
            version     2.0;
        }

        #include  "initialConditions";
    """,
        cls=FoamInputFile,
        check_dump=True,
    )


def test_code():
    base_test_simple(
        r"""
        code_name
        #{
            -I$(LIB_SRC)/finiteVolume/lnInclude \
            -I$(LIB_SRC)/meshTools/lnInclude
        #};
    """,
        check_dump=False,
    )


def test_macro():
    tree = base_test_simple(
        """
        FoamFile
        {
            version     2.0;
        }

        relTol  $p;
        Phi
        {
            $p;
        }

        p_rbghFinal
        {
            $p_rbgh;
            tolerance    1e-08;
            relTol       0;
        }

        relaxationFactors  $relaxationFactors-SIMPLE;
    """,
        check_dump=True,
    )


def test_empty_dict():
    tree = base_test_simple(
        """
        solvers
        {
        }
        relaxationFactors
        {}
    """,
        check_dump=False,
    )


def test_dict_isolated_key():
    tree = base_test_simple(
        """
        cache
        {
            grad(U);
        }
    """,
        check_dump=True,
    )


def test_dimension_set():
    tree = base_test_simple(
        """
        dimension  [0 2 -1 0 0 0 0];
        nu  [0 2 -1 0 0 0 0] 1e-05;
        nu1  nu [0 2 -1 0 0 0 0] 1e-06;
        SIMPLE
        {
            rhoMin  rhoMin [1 -3 0 0 0 0 0] 0.3;
        }

        """,
        cls=FoamInputFile,
        check_dump=True,
    )
    assert isinstance(tree.children["nu"], Value)
    assert isinstance(tree.children["dimension"], DimensionSet)


def test_named_values():
    tree = base_test_simple(
        """
        a  b;
        ft  limitedLinear01 1;
        """,
        cls=FoamInputFile,
        check_dump=True,
    )
    assert isinstance(tree.children["ft"], Value)


def test_macro_ugly():
    tree = base_test_simple(
        """
        relaxationFactors
        {
            ${_${FOAM_EXECUTABLE}};
        }
        """,
        check_dump=True,
    )


def test_list_on_1_line():
    tree = base_test_simple(
        """
        libs            (overset rigidBodyDynamics);

        functions
        {
            minMax1
            {
                libs            (fieldFunctionObjects);
                type            fieldMinMax;
                fields          (U p);
            }
        }
        """,
        check_dump_parse=True,
    )


def test_double_value():
    tree = base_test_simple(
        """
        FoamFile
        {
            format    ascii;
            object    controlDict.1st;
        }
        """,
        check_dump=True,
    )


def test_for_blockmesh():
    tree = base_test_simple(
        """
        negHalfWidth  #neg $halfWidth;
        blocks
        (
            hex (4 6 14 12 0 2 10 8) (1 $upstreamCells $cylinderBoxCells) $expandBlock
        );
        """,
        check_dump=True,
    )


def test_for_U():
    tree = base_test_simple(
        """
        internalField  uniform $include/caseSettings!internalField/U;
        """,
        check_dump=True,
    )


def test_code_with_directive():
    tree = base_test_simple(
        """
        nx  #eval #{ round(5 * $NSLABS) #};
        """,
        check_dump_parse=True,
    )


def test_blocks():
    tree = base_test_simple(
        """
        FoamFile
        {
            version     2.0;
        }

        blocks
        (
            hex (0 1 2 3 4 5 6 7) inletChannel (40 1 64) simpleGrading (1 1 1)
            hex (4 5 6 7 8 9 10 11 12) inletChannel (40 1 16) simpleGrading (1 1 1)
            hex (12 13 14 15 16 17 18 19) (96 1 8) simpleGrading (1 1 1)
            hex (16 17 18 19 20 21 22 23) (96 1 72) simpleGrading (1 1 1)
        );
        """,
        check_dump=True,
    )


def test_macro_signed():
    tree = base_test_simple(
        """
        vertices
        (
            ($x0 $y0 -$w2)
            (0 -$h2 -$w2)
            (0 $h2 -$w2)
            ($x1 $y1 -$w2)
        );
        """,
        check_dump=True,
    )


def test_list_numbered():
    tree = base_test_simple(
        """
        internalField nonuniform
        List<vector>
        4096
        (
            (-0.0376011 0.020584 -0.0051027)
            (-0.0262359 0.0149309 -0.0048244)
            (-0.0141003 0.00810973 -0.00427023)
        );

        """,
        check_dump=True,
    )


def test_list_u():
    tree = base_test_simple(
        """
        FoamFile
        {
            version     2.0;
        }
        (
        (4.507730000e+00 1.799630000e+00 0.000000000e+00)
        (6.062080000e+00 2.408310000e+00 0.000000000e+00)
        (6.874000000e+00 2.720790000e+00 0.000000000e+00)
        (7.429290000e+00 2.931000000e+00 0.000000000e+00)
        (7.850950000e+00 3.088050000e+00 0.000000000e+00)
        (8.192020000e+00 3.213060000e+00 0.000000000e+00)
        (1.750000000e+01 1.925590000e-09 0.000000000e+00)
        (1.750000000e+01 6.810450000e-12 0.000000000e+00)
        (1.750000000e+01 6.810450000e-12 0.000000000e+00)
        );

        """,
        check_dump_parse=True,
    )


def test_list_numbered_u():
    tree = base_test_simple(
        """
        70
        (
            (5.74803 0 0)
            (5.74803 0 0)
            (11.3009 0 0)
            (13.4518 0 0)
            (13.4518 0 0)
            (14.0472 0 0)
        );
        """,
        check_dump=True,
    )


def test_colon_double_name():
    """In controlDict files (found once)"""
    tree = base_test_simple(
        """
        DebugSwitches
        {
            compressible::alphatWallBoilingWallFunction                 0;
            compressible::turbulentTemperatureTwoPhaseRadCoupledMixed   0;
        }
        """,
        check_dump_parse=True,
    )


def test_assignment_strange_name():
    tree = base_test_simple(
        """
        equations
        {
            "(U|e|k).*"  0.7;
            "(U|e|k|epsilon).*" table ((0 0.4) (0.5 0.7));
        }
    """,
        check_dump_parse=True,
    )


def test_code_with_directive_and_macro():
    """In controlDict files (found once)"""
    tree = base_test_simple(
        """
        timeStart  #eval #{ 1.0/3.0 * ${/endTime} #};
        U
        {
            mean          on;
            prime2Mean    on;
            base          time;
        }
        """,
        check_dump_parse=True,
    )


def test_list_edges():
    tree = base_test_simple(
        """
        edges
        (
            spline 1 2 ((0.6 0.0124 0.0) (0.7 0.0395 0.0) (0.8 0.0724 0.0) (0.9 0.132 0.0) (1 0.172 0.0) (1.1 0.132 0.0) (1.2 0.0724 0.0) (1.3 0.0395 0.0) (1.4 0.0124 0.0))
            spline 6 5 ((0.6 0.0124 0.05) (0.7 0.0395 0.05) (0.8 0.0724 0.05) (0.9 0.132 0.05) (1 0.172 0.05) (1.1 0.132 0.05) (1.2 0.0724 0.05) (1.3 0.0395 0.05) (1.4 0.0124 0.05))
        );
        """,
        check_dump=True,
    )


def test_list_blocks():
    tree = base_test_simple(
        """
        blocks
        (
            hex (0 1 9 8 7 6 14 15) (50 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
            hex (1 2 10 9 6 5 13 14) (50 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
            hex (2 3 11 10 5 4 12 13) (225 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
        );
        """,
        check_dump=True,
    )
