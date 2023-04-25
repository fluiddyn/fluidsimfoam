import shutil
from pathlib import Path

import pytest
from fluidsimfoam_cbox import Simul

from fluidsimfoam.foam_input_files import dump, parse

here = Path(__file__).absolute().parent


@pytest.mark.parametrize("index_sim", [0, 1, 2])
def test_init_simul_sim0(index_sim):
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/sim0"

    if index_sim == 1:
        params.transport_properties.nu = 0.002
    elif index_sim == 2:
        params.transport_properties.nu = 0.003

    sim = Simul(params)

    path_pure_openfoam_case = here / f"pure_openfoam_cases/cbox/sim{index_sim}"
    paths_in_sim = [
        path.relative_to(path_pure_openfoam_case)
        for path in path_pure_openfoam_case.rglob("*")
        if not path.is_dir() and not path.name.startswith("README")
    ]

    for name in paths_in_sim:
        path_manual = path_pure_openfoam_case / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists(), name
        text_produced = path_produced.read_text()
        if str(name) != "system/blockMeshDict":
            assert text_produced == text_manual, name
        else:
            tree_saved_file = parse(text_manual)
            tree_from_py = parse(text_produced)

            assert dump(tree_saved_file).strip() == dump(tree_from_py).strip()


path_foam_executable = shutil.which("buoyantBoussinesqPimpleFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/"

    params.control_dict.end_time = 10

    sim = Simul(params)

    sim.make.exec("run")
