from pathlib import Path

from fluidsimfoam_sed import Simul
from fluidsimfoam.foam_input_files import dump, parse

here = Path(__file__).absolute().parent

path_pure_openfoam_case = here / "pure_openfoam_cases/RAS/1DBedLoadTurb"
paths_in_sim = [
    path.relative_to(path_pure_openfoam_case)
    for path in path_pure_openfoam_case.rglob("*")
    if not path.is_dir()
    and not any(path.name.startswith(s) for s in ("README", "All"))
]


def test_ras_1dbedloadturb():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/sed"

    sim = Simul(params)

    for name in paths_in_sim:
        path_manual = path_pure_openfoam_case / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists(), name
        text_produced = path_produced.read_text()
        assert text_produced == text_manual, name