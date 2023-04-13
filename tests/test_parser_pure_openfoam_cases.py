from pathlib import Path
import pytest
from rich.progress import track
from test_parser import base_test

here = Path(__file__).absolute().parent

path_files = here / "pure_openfoam_cases/"

paths_in_dirs = [
    path.relative_to(path_files)
    for path in path_files.rglob("*")
    if not path.is_dir() and not path.name.startswith("README")
]


@pytest.mark.xfail
def test_files():
    for name in track(paths_in_dirs):
        path_manual = path_files / name
        text_manual = path_manual.read_text()
        if str(name) == "phill/sim_turb/0/rhok":
            continue
        try:
            tree = base_test(text_manual, check_dump=False, check_dump_parse=True)
        except Exception as err:
            print(f"{path_manual}, Error: {type(err)}")
