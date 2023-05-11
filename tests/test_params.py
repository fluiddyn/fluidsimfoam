from fluidsimfoam.params import get_indent_after_tag


def test():
    assert get_indent_after_tag('    <div a="b"') == " " * 9
    assert get_indent_after_tag('<div a="b"') == " " * 5
