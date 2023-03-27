import pytest

from fluidsimfoam.of_input_files.ast import Value, of_units2str, str2of_units


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


def test_of_units2str():
    assert of_units2str([0, 2, -1, 0, 0, 0, 0]) == "m^2/s"
    assert of_units2str([-1, 2, -1, 0, 0, 0, 0]) == "1/kg.m^2/s"


def test_str2of_units():
    assert str2of_units("m^2/s") == [0, 2, -1, 0, 0, 0, 0]
    assert str2of_units("1/kg.m^2/s") == [-1, 2, -1, 0, 0, 0, 0]


@pytest.mark.parametrize(
    "of_units",
    ([0, 0, 0, 0, 0, 0, 0], [2, 2, -1, 0, 0, 0, 0], [-1, 2, -1, 3, 1, -2, -1]),
)
def test_convert_unit_format(of_units):
    assert str2of_units(of_units2str(of_units)) == of_units
