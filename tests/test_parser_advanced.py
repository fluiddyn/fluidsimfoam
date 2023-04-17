from functools import partial

import pytest
from test_parser import base_test

from fluidsimfoam.foam_input_files.ast import CodeStream

base_test_advanced = partial(base_test, grammar="advanced")


def test_dict_strange_name():
    """As in fvSchemes"""
    tree = base_test_advanced(
        """
        div(phi,ft_b_ha_hau) Gauss multivariateSelection
        {
            ft              limitedLinear01 1;
            b               limitedLinear01 1;
        }
    """,
        check_dump_parse=True,
    )


def test_dict_strange_keys():
    """As in fvSchemes"""
    tree = base_test_advanced(
        """
        div(phi,U)      Gauss linear;
        divSchemes
        {
            field       cylindrical(U)Mean;
            default         none;
            div(phi,U)      Gauss linear;
            div((nuEff*dev2(T(grad(U))))) Gauss linear;
            ".*"           1;
            div(rhoPhi,U)   Gauss cellCoBlended 2 linearUpwind grad(U) 5 upwind;
        }
    """,
        check_dump_parse=True,
    )


def test_var_value_with_space():
    tree = base_test_advanced(
        """
        laplacianSchemes
        {
            default         Gauss linear corrected;
        }
    """,
        check_dump_parse=True,
    )
    assert tree.value["default"] == "Gauss linear corrected"


def test_strange_dict_macro():
    tree = base_test_advanced(
        """
        relaxationFactors { $relaxationFactors-SIMPLE }
        """,
        check_dump_parse=True,
    )


def test_directive_eval():
    tree = base_test_advanced(
        """
        transform
        {
            origin  (#eval{0.5 * $SLAB_OFFSET} 0 0);
            rotation none;
        }
        """,
        check_dump_parse=True,
    )


def test_directive_if():
    tree = base_test_advanced(
        """
        #if 0
        xin     #eval{ $xin / 5 };
        xout    #eval{ $xout / 5 };
        zmax    #eval{ $zmax / 5 };

        nxin    #eval{ round ($nxin / 5) };
        nxout   #eval{ round ($nxout / 5) };
        nz      #eval{ round ($nz / 5) };
        #endif
        """,
        check_dump_parse=True,
    )


def test_directive_if_in_file():
    tree = base_test_advanced(
        """
        #if 0
        xin     #eval{ $xin / 5 };
        xout    #eval{ $xout / 5 };
        zmax    #eval{ $zmax / 5 };

        nxin    #eval{ round ($nxin / 5) };
        nxout   #eval{ round ($nxout / 5) };
        nz      #eval{ round ($nz / 5) };
        #endif

        zmin    #eval{ -$zmax };
        """,
        check_dump_parse=True,
    )


def test_macro_with_dict():
    tree = base_test_advanced(
        """
        rInner45    ${{ $rInner * sqrt(0.5) }};
        rOuter45    ${{ $rOuter * sqrt(0.5) }};
        xmin        ${{ -$xmax }};
        """,
        check_dump_parse=True,
    )


def test_directive_strange():
    tree = base_test_advanced(
        """
        #remove ( "r(Inner|Outer).*"  "[xy](min|max)" )
        """,
        check_dump=True,
    )


@pytest.mark.xfail(reason="In controlDict files (found once)")
def test_directive_with_macro():
    tree = base_test_advanced(
        """
        timeStart       #eval{ 0.1 * ${/endTime} };
        """,
        check_dump_parse=True,
    )


@pytest.mark.xfail(reason="In fvSchemes files (found 3 times)")
def test_strange_assignment():
    tree = base_test_advanced(
        """
        divSchemes
        {
            div(phi,U)      Gauss DEShybrid
                linear                    // scheme 1
                linearUpwind grad(U)      // scheme 2
                hmax
                0.65                      // DES coefficient, typically = 0.65
                1                         // Reference velocity scale
                0.028                     // Reference length scale
                0                         // Minimum sigma limit (0-1)
                1                         // Maximum sigma limit (0-1)
                1; // 1.0e-03;                  // Limiter of B function, typically 1e-03
        }

        """,
        check_dump_parse=True,
    )


def test_dict_with_list_name():
    """In transportProperties files (found 4 times)"""
    tree = base_test_advanced(
        """
        drag
        (
            (air water)
            {
                type blended;

                residualPhaseFraction 1e-3;
                residualSlip 1e-3;
            }
        );
        """,
        check_dump_parse=True,
    )


@pytest.mark.xfail(reason="In g files (found once)")
def test_list_name_eq():
    tree = base_test_advanced(
        """
        value #eval
        {
            -9.81 * vector
            (
                sin(degToRad($alphax)),
                sin(degToRad($alpha)),
                cos(degToRad($alpha))
            )
        };
        """,
        check_dump_parse=True,
    )


def test_list_triple_named():
    tree = base_test_advanced(
        """
        velocity-inlet-5
        {
            type            fixedValue;
            value           uniform (1 0 0);
        }
        """,
        check_dump_parse=True,
    )


def test_directives_in_dict():
    tree = base_test_advanced(
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
        check_dump_parse=True,
    )


def test_code_stream():
    tree = base_test_advanced(
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

        }
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


def test_assignment_strange_name():
    tree = base_test_advanced(
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
    tree = base_test_advanced(
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


def test_code_with_directive():
    tree = base_test_advanced(
        """
        nx  #eval #{ round(5 * $NSLABS) #};
        """,
        check_dump_parse=True,
    )


def test_list_u():
    tree = base_test_advanced(
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
