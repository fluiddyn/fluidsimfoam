import pytest

from fluidsimfoam.foam_input_files.ast import (
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
