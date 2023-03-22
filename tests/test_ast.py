from fluidsimfoam.of_input_files.ast import Value


def test_value():
    value = Value(1e-06, name="nu", dimension=[0, 2, -1, 0, 0, 0, 0])
    assert repr(value) == 'Value(1e-06, name="nu", dimension="m^2/s")'
    assert value.dump() == "nu [ 0 2 -1 0 0 0 0 ] 1e-06;"

    value = Value(1e-06, name="nu")
    assert repr(value) == 'Value(1e-06, name="nu")'
    assert value.dump() == "nu 1e-06;"

    value = Value(1e-06, dimension=[0, 2, -1, 0, 0, 0, 0])
    assert repr(value) == 'Value(1e-06, dimension="m^2/s")'
    assert value.dump() == "[ 0 2 -1 0 0 0 0 ] 1e-06;"
