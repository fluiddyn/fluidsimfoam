import shutil
from pathlib import Path

import pytest
from fluidsimfoam_cavity import Simul

here = Path(__file__).absolute().parent

path_saved_case = here / "saved_cases/cavity"
paths_in_sim = [
    path.relative_to(path_saved_case)
    for path in path_saved_case.rglob("*")
    if not path.is_dir()
    and not any(path.name.startswith(s) for s in ("README", "All"))
    and not path.parent.name == "polyMesh"
]


def test_reproduce_case():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cavity"

    sim = Simul(params)

    for relative_path in paths_in_sim:
        path_manual = path_saved_case / relative_path
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / relative_path
        assert path_produced.exists(), relative_path
        text_produced = path_produced.read_text()
        assert text_produced == text_manual, relative_path


path_foam_executable = shutil.which("icoFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cavity"
    params.control_dict.end_time = 0.001
    sim = Simul(params)
    sim.make.exec("run")
