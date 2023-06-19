from fluidsimfoam.foam_input_files.format import _unidiff_output, format_code


def test_unidiff_output():
    _unidiff_output("a", "b")


def test_format():
    format_code(
        """
    a  1;
    internalField   uniform (0.1 0 0);
    """
    )
