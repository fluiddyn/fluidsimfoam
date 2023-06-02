"""Format OpenFOAM input files"""

import lark

from fluidsimfoam.foam_input_files.fields import create_field_from_code
from fluidsimfoam.foam_input_files.parser import dump, parse


def _unidiff_output(expected, actual):
    """
    Returns a string containing the unified diff of two multiline strings.

    Taken from https://stackoverflow.com/a/845432
    """
    import difflib

    expected = expected.splitlines(keepends=True)
    actual = actual.splitlines(keepends=True)
    diff = difflib.unified_diff(expected, actual)
    return "".join(diff)


class FoamFormatError(RuntimeError):
    pass


def format_code(code, as_field=False, check=True):
    if not as_field:
        tree = parse(code)
        result = dump(tree)
        if check:
            try:
                tree1 = parse(result)
            except lark.exceptions.LarkError:
                raise FoamFormatError(f"LarkError while formatting code\n{code}")
            else:
                result1 = dump(tree1)

            if result != result1:
                print(
                    "Not able to correctly parse this code:\n"
                    + _unidiff_output(result, result1)
                )
                raise FoamFormatError("Not able to correctly parse this code")
        return result
    else:
        return create_field_from_code(code).dump()
