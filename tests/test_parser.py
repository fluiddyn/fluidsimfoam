from textwrap import dedent

import pytest
from lark.exceptions import LarkError

from fluidsimfoam.foam_input_files import dump, parse
from fluidsimfoam.foam_input_files.ast import (
    CodeStream,
    Dict,
    DimensionSet,
    FoamInputFile,
    Node,
    Value,
)


def base_test(
    text,
    representation=None,
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
        assert dumped_text.strip() == dedent(text).strip()
    if check_dump_parse:
        try:
            assert tree == parse(dumped_text, grammar=grammar)
        except LarkError as err:
            print(dumped_text)
            raise RuntimeError from err
    return tree


both_grammars = pytest.mark.parametrize("grammar", ("simple", "advanced"))


@both_grammars
def test_var_simple(grammar):
    base_test(
        """
        a  b;
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_var_quoted_string(grammar):
    tree = base_test(
        """
        laplacianSchemes
        {
            default    "Gauss linear corrected";
        }
    """,
        grammar=grammar,
        check_dump=True,
    )
    assert tree.value["default"] == '"Gauss linear corrected"'


@both_grammars
def test_var_multiple(grammar):
    tree = base_test(
        """
        a    b;

        c    d;
    """,
        grammar=grammar,
        representation="InputFile(\nchildren={'a': 'b', 'c': 'd'}\n)",
        check_dump=True,
    )


@both_grammars
def test_strange_names(grammar):
    tree = base_test(
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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_simple(grammar):
    tree = base_test(
        """
        faces
        (
            (1 5 4 0)
            (2 3 4 5)
        );
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_assignment(grammar):
    tree = base_test(
        """
        faces
        (
            1
            5
            4
            0
        );
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_dict_simple(grammar):
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
        grammar=grammar,
        check_dump_parse=True,
    )

    my_dict = tree.value
    assert isinstance(my_dict, Dict)
    assert my_dict["version"] == 2.0
    assert my_dict["format"] == "ascii"
    assert my_dict["location"] == '"system"'


@both_grammars
def test_dict_nested(grammar):
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
        grammar=grammar,
        check_dump=True,
    )

    my_nested_dict = tree.value
    assert my_nested_dict["p"]["solver"] == "PCG"
    assert my_nested_dict["U"]["tolerance"] == 1e-05


@both_grammars
def test_dict_with_list(grammar):
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
        grammar=grammar,
        check_dump_parse=True,
    )
    assert tree.value["pRefPoint"]._name == "pRefPoint"


@both_grammars
def test_list_with_dict(grammar):
    base_test(
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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_with_str(grammar):
    base_test(
        """
        blocks
        (
            hex (0 1 2 3 4 5 6 7) (40 40 40) simpleGrading (1 1 1)
        );
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_file_simple(grammar):
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
    """,
        grammar=grammar,
    )


@both_grammars
def test_file(grammar):
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       volScalarField;
            object      p;
        }

        a    1;

        b    2;

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
        grammar=grammar,
        check_dump=True,
    )
    assert tree.children["my_dict"]["a"] == 1


@both_grammars
def test_directive(grammar):
    base_test(
        """
        FoamFile
        {
            version     2.0;
        }

        #include  "initialConditions";
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_directives_in_dict(grammar):
    tree = base_test(
        """
        functions
        {
            #includeFunc fieldAverage(cylindrical(U))
            #includeFunc Qdot
            #includeFunc components(U)
            #includeFunc Qdot(region=gas)
            #includeFunc residuals(region = shell, p_rgh, U, h)
            #includeFunc residuals(region = tube, p_rgh, U, h)
            #includeFunc patchAverage
            (
                funcName=cylinderT,
                region=fluid,
                patch=fluid_to_solid,
                field=T
            )
            #includeFunc streamlinesLine(funcName=streamlines, start=(0 0.5 0), end=(9 0.5 0), nPoints=24, U)
            #includeFunc streamlinesLine
            (
                funcName=streamlines,
                start=(-0.0205 0.001 0.00001),
                end=(-0.0205 0.0251 0.00001),
                nPoints=10,
                fields=(p k U)
            )
            #includeFunc writeObjects(kEpsilon:G)
            #includeFunc fieldAverage(U, p, alpha.vapour)
            #includeFunc writeObjects
            (
                d.particles,
                a.particles,
                phaseTransfer:dmidtf.TiO2.particlesAndVapor,
                phaseTransfer:dmidtf.TiO2_s.particlesAndVapor
            )
            #includeFunc  graphUniform
            (
                funcName=graph,
                start=(0 0 0.89),
                end=(0.025 0 0.89),
                nPoints=100,
                fields=
                (
                    alpha.air1
                    alpha.air2
                    alpha.bubbles
                    liftForce.water
                    wallLubricationForce.water
                    turbulentDispersionForce.water
                )
            )
        }
        """,
        grammar=grammar,
        check_dump_parse=True,
    )


@both_grammars
def test_code(grammar):
    base_test(
        r"""
        code_name
        #{
            -I$(LIB_SRC)/finiteVolume/lnInclude \
            -I$(LIB_SRC)/meshTools/lnInclude
        #};
    """,
        grammar=grammar,
        check_dump=False,
    )


@both_grammars
def test_macro(grammar):
    tree = base_test(
        """
        FoamFile
        {
            version     2.0;
        }

        relTol            $p;

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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_empty_dict(grammar):
    tree = base_test(
        """
        solvers
        {
        }
        relaxationFactors
        {}
    """,
        grammar=grammar,
        check_dump=False,
    )


@both_grammars
def test_dict_isolated_key(grammar):
    tree = base_test(
        """
        cache
        {
            grad(U);
        }
    """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_dimension_set(grammar):
    tree = base_test(
        """
        dimensions    [0 2 -1 0 0 0 0];

        nu            [0 2 -1 0 0 0 0] 1e-05;

        nu1           nu [0 2 -1 0 0 0 0] 1e-06;

        SIMPLE
        {
            rhoMin    rhoMin [1 -3 0 0 0 0 0] 0.3;
        }
        """,
        grammar=grammar,
        check_dump=True,
    )
    assert isinstance(tree.children["nu"], Value)
    assert isinstance(tree.children["dimensions"], DimensionSet)


@both_grammars
def test_dimension_assigment(grammar):
    tree = base_test(
        """
        dimensions  [0 1 -1 0 0 0 0];
        """,
        grammar=grammar,
        check_dump=True,
    )
    assert isinstance(tree.value, DimensionSet)


@both_grammars
def test_named_values(grammar):
    tree = base_test(
        """
        a     b;

        ft    limitedLinear01 1;
        """,
        grammar=grammar,
        check_dump=True,
    )
    assert isinstance(tree.children["ft"], Value)


@both_grammars
def test_macro_ugly(grammar):
    tree = base_test(
        """
        relaxationFactors
        {
            ${_${FOAM_EXECUTABLE}};
        }
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_on_1_line(grammar):
    tree = base_test(
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
        grammar=grammar,
        check_dump_parse=True,
    )


@both_grammars
def test_double_value(grammar):
    tree = base_test(
        """
        FoamFile
        {
            format    ascii;
            object    controlDict.1st;
        }
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_for_blockmesh(grammar):
    tree = base_test(
        """
        negHalfWidth    #neg $halfWidth;

        blocks
        (
            hex (4 6 14 12 0 2 10 8) (1 $upstreamCells $cylinderBoxCells) $expandBlock
        );
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_for_U(grammar):
    tree = base_test(
        """
        internalField  uniform $include/caseSettings!internalField/U;
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_blocks(grammar):
    tree = base_test(
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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_macro_signed(grammar):
    tree = base_test(
        """
        vertices
        (
            ($x0 $y0 -$w2)
            (0 -$h2 -$w2)
            (0 $h2 -$w2)
            ($x1 $y1 -$w2)
        );
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_numbered(grammar):
    tree = base_test(
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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_numbered_u(grammar):
    tree = base_test(
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
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_colon_double_name(grammar):
    """In controlDict files (found once)"""
    tree = base_test(
        """
        DebugSwitches
        {
            compressible::alphatWallBoilingWallFunction                 0;
            compressible::turbulentTemperatureTwoPhaseRadCoupledMixed   0;
        }
        """,
        grammar=grammar,
        check_dump_parse=True,
    )


@both_grammars
def test_list_edges(grammar):
    tree = base_test(
        """
        edges
        (
            spline 1 2 ((0.6 0.0124 0.0) (0.7 0.0395 0.0) (0.8 0.0724 0.0) (0.9 0.132 0.0) (1 0.172 0.0) (1.1 0.132 0.0) (1.2 0.0724 0.0) (1.3 0.0395 0.0) (1.4 0.0124 0.0))
            spline 6 5 ((0.6 0.0124 0.05) (0.7 0.0395 0.05) (0.8 0.0724 0.05) (0.9 0.132 0.05) (1 0.172 0.05) (1.1 0.132 0.05) (1.2 0.0724 0.05) (1.3 0.0395 0.05) (1.4 0.0124 0.05))
        );
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_edges_arcs(grammar):
    tree = base_test(
        """
        edges
        (
            arc 0 5 origin (0 0 0)
            arc 5 10 origin (0 0 0)
        );
        """,
        grammar=grammar,
        check_dump=True,
    )


@both_grammars
def test_list_blocks(grammar):
    tree = base_test(
        """
        blocks
        (
            hex (0 1 9 8 7 6 14 15) (50 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
            hex (1 2 10 9 6 5 13 14) (50 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
            hex (2 3 11 10 5 4 12 13) (225 100 1) simpleGrading (1 ((0.1 0.25 41.9) (0.9 0.75 1)) 1)
        );
        """,
        grammar=grammar,
        check_dump=True,
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
        check_dump=True,
    )

    code_stream = tree.value
    assert isinstance(code_stream, CodeStream)
    for name in ("code_include", "code_options", "code_libs", "code"):
        assert hasattr(code_stream, name)
    assert code_stream.code.strip().startswith("const IOdictionary")
    code_stream.code_include = "toto"
    code_stream["codeInclude"] == "toto"


def test_list_uniform():
    tree = base_test(
        r"""
        a    1;

        internalField uniform
        (
            0.1
            0
            0
        );
        """,
        check_dump=True,
    )

    assert tree["internalField"]._name == "internalField uniform"
