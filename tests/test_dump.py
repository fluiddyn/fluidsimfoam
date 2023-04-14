import pytest
from test_parser import base_test


@pytest.mark.xfail(reason="check this space")
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
        check_dump=True,
    )


@pytest.mark.xfail(reason="bad dumping list")
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
        check_dump=True,
    )


@pytest.mark.xfail(reason="bad dumping list")
def test_directives_in_dict():
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
        check_dump=True,
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
    )


@pytest.mark.xfail(reason="bad dumping lists in one line")
def test_list_on_1_line():
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
        check_dump=True,
    )


@pytest.mark.xfail(reason="bad dumping lists without name")
def test_list_u():
    tree = base_test(
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
        check_dump=True,
    )


@pytest.mark.xfail(reason="bad dumping lists in one line")
def test_assignment_strange_name():
    tree = base_test(
        """
        equations
        {
            "(U|e|k).*"  0.7;
            "(U|e|k|epsilon).*" table ((0 0.4) (0.5 0.7));
        }
    """,
        check_dump=True,
    )
