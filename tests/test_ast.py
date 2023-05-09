from textwrap import dedent

import pytest

from fluidsimfoam.foam_input_files.ast import (
    Dict,
    FoamInputFile,
    List,
    Value,
    foam_units2str,
    str2foam_units,
)


def test_value():
    value = Value(1e-06, name="nu", dimension=[0, 2, -1, 0, 0, 0, 0])
    assert repr(value) == 'Value(1e-06, name="nu", dimension="m^2/s")'
    assert value.dump_without_assignment() == "nu [0 2 -1 0 0 0 0] 1e-06"

    value = Value(1e-06, name="nu")
    assert repr(value) == 'Value(1e-06, name="nu")'
    assert value.dump_without_assignment() == "nu 1e-06"

    value = Value(1e-06, dimension=[0, 2, -1, 0, 0, 0, 0])
    assert repr(value) == 'Value(1e-06, dimension="m^2/s")'
    assert value.dump_without_assignment() == "[0 2 -1 0 0 0 0] 1e-06"


def test_foam_units2str():
    assert foam_units2str([0, 2, -1, 0, 0, 0, 0]) == "m^2/s"
    assert foam_units2str([-1, 2, -1, 0]) == "1/kg.m^2/s"


def test_str2foam_units():
    assert str2foam_units("m^2/s") == [0, 2, -1, 0, 0, 0, 0]
    assert str2foam_units("1/kg.m^2/s") == [-1, 2, -1, 0, 0, 0, 0]
    assert str2foam_units("K") == [0, 0, 0, 1, 0, 0, 0]


@pytest.mark.parametrize(
    "foam_units",
    ([0, 0, 0, 0, 0, 0, 0], [2, 2, -1, 0, 0, 0, 0], [-1, 2, -1, 3, 1, -2, -1]),
)
def test_convert_unit_format(foam_units):
    assert str2foam_units(foam_units2str(foam_units)) == foam_units


def test_dump_file():
    tree = FoamInputFile(
        info={
            "version": "2.0",
        },
        children={
            "transportModel": "Newtonian",
            "nu": 1e-03,
        },
        comments={
            "nu": "Laminar viscosity",
        },
    )
    result = dedent(
        """
        FoamFile
        {
            version     2.0;
        }

        transportModel    Newtonian;

        // Laminar viscosity
        nu                0.001;
    """
    )[1:]

    assert tree.dump() == result


def test_init_from_py_objects():
    tree = FoamInputFile(info={})

    tree.init_from_py_objects(
        {
            "simulationType": "RAS",
            "RAS": {
                "RASModel": "twophaseMixingLength",
                "twophaseMixingLengthCoeffs": {
                    "expoLM": 1.5,
                    "alphaMaxLM": 0.61,
                    "kappaLM": 0.41,
                },
            },
        }
    )

    ras = tree.children["RAS"]
    assert isinstance(ras, Dict)
    assert ras["twophaseMixingLengthCoeffs"]["expoLM"] == 1.5


def test_init_from_py_objects_list():
    tree = FoamInputFile(info={})

    tree.init_from_py_objects(
        {"gradPMEAN": [1000, 0, 0], "tilt": 1, "debugInfo": "true"}
    )
    grad = tree.children["gradPMEAN"]

    assert isinstance(grad, List)
    assert grad[0] == 1000
