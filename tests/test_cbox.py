from pathlib import Path

from rich.progress import track
from test_parser import base_test

here = Path(__file__).absolute().parent

path_cbox = here / "pure_openfoam_cases/cbox/"


paths_in_cbox = [
    path.relative_to(path_cbox)
    for path in path_cbox.rglob("*")
    if not path.is_dir() and not path.name.startswith("README")
]

for name in track(paths_in_cbox):
    path_manual = path_cbox / name
    text_manual = path_manual.read_text()
    try:
        tree = base_test(text_manual, check_dump=False, check_dump_parse=True)
    except:
        print(f"{path_manual}")
