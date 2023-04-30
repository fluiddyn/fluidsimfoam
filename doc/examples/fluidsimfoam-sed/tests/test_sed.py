from pathlib import Path

from fluidsimfoam_sed import Simul

here = Path(__file__).absolute().parent

path_pure_openfoam_case = here / "saved_cases/RAS/1DBedLoadTurb"
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

    for relative_path in paths_in_sim:
        path_manual = path_pure_openfoam_case / relative_path
        text_manual = path_manual.read_text()

        if str(relative_path.parent) == "0_org":
            relative_path = Path("0") / relative_path.name

        path_produced = sim.path_run / relative_path
        assert path_produced.exists(), relative_path
        text_produced = path_produced.read_text()
        assert text_produced == text_manual, relative_path
