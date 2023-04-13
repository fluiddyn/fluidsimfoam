import pytest
from test_parser import base_test


def test_dict_strange_name():
    """As in fvSchemes"""
    tree = base_test(
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
    tree = base_test(
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


def test_strange_dict_macro():
    tree = base_test(
        """
        relaxationFactors { $relaxationFactors-SIMPLE }
        """,
        check_dump_parse=True,
    )


def test_directive_eval():
    tree = base_test(
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
    tree = base_test(
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
    tree = base_test(
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
    tree = base_test(
        """
        rInner45    ${{ $rInner * sqrt(0.5) }};
        rOuter45    ${{ $rOuter * sqrt(0.5) }};
        xmin        ${{ -$xmax }};
        """,
        check_dump_parse=True,
    )


def test_directive_strange():
    tree = base_test(
        """
        #remove ( "r(Inner|Outer).*"  "[xy](min|max)" )
        """,
        check_dump_parse=True,
        check_dump=True,
    )


@pytest.mark.xfail(reason="In controlDict files (found once)")
def test_directive_with_macro():
    tree = base_test(
        """
        timeStart       #eval{ 0.1 * ${/endTime} };
        """,
        check_dump_parse=True,
    )


@pytest.mark.xfail(reason="In fvSchemes files (found 3 times)")
def test_strange_assignment():
    tree = base_test(
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
    tree = base_test(
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
    tree = base_test(
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