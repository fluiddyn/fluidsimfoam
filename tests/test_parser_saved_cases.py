from pathlib import Path

import pytest
from test_parser import base_test

here = Path(__file__).absolute().parent
path_cases = here / "saved_cases/"


def get_paths_input_files(directory):
    return {
        path.name: path
        for path in (path_cases / directory).rglob("*")
        if path.is_file()
        and not path.parent.name == "polyMesh"
        and all(
            word not in path.name for word in ("README", "Allrun", "Allclean")
        )
    }


paths_tiny_tgv = get_paths_input_files("tiny-tgv")
paths_cbox = get_paths_input_files("cbox/sim0")


def base_test_file(path):
    text = path.read_text()
    base_test(text, check_dump_parse=True)


@pytest.mark.parametrize("path_name", paths_tiny_tgv)
def test_tiny_tgv(path_name, request):
    base_test_file(paths_tiny_tgv[path_name])


@pytest.mark.parametrize("path_name", paths_cbox)
def test_cbox(path_name, request):
    if path_name == "topoSetDict":
        request.applymarker(pytest.mark.xfail())
    base_test_file(paths_cbox[path_name])
