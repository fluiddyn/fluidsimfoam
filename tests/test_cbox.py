from pathlib import Path

from textwrap import dedent

from lark.exceptions import LarkError

from fluidsimfoam.foam_input_files import dump, parse


here = Path(__file__).absolute().parent

path_cbox = here / "pure_openfoam_cases/cbox/"


def base_test(text, check_dump=False, check_dump_parse=False):
    tree = parse(text)

    if check_dump:
        dump_text = dump(tree)
        assert dedent(text).strip() == dump_text.strip()
    if check_dump_parse:
        try:
            assert tree == parse(dump(tree))
        except LarkError as err:
            raise RuntimeError from err
    return tree


paths_in_cbox = [
    path.relative_to(path_cbox)
    for path in path_cbox.rglob("*")
    if not path.is_dir() and not path.name.startswith("README")
]

for name in paths_in_cbox:
    path_manual = path_cbox / name
    text_manual = path_manual.read_text()
    print(f"{path_manual}")
    tree = base_test(text_manual, check_dump=False, check_dump_parse=True)
