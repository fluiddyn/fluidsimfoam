from pathlib import Path

from rich.progress import track
from test_parser import base_test

here = Path(__file__).absolute().parent

path_phill = here / "pure_openfoam_cases/phill/"


paths_in_phill = [
    path.relative_to(path_phill)
    for path in path_phill.rglob("*")
    if not path.is_dir() and not path.name.startswith("README")
]

for name in track(paths_in_phill):
    path_manual = path_phill / name
    text_manual = path_manual.read_text()
    if str(name) == "sim_turb/0/rhok":
        continue
    try:
        tree = base_test(text_manual, check_dump=False, check_dump_parse=True)
    except:
        print(f"{path_manual}")
