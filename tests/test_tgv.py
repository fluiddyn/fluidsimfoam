import shutil
from pathlib import Path

import pytest
from fluidsimfoam_tgv import Simul

from fluidsimfoam import load

here = Path(__file__).absolute().parent

path_tiny = here / "pure_openfoam_cases/tiny-tgv"


@pytest.fixture(scope="function")
def sim_tgv():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    params.control_dict.end_time = 0.3
    params.control_dict.delta_t = 0.05
    params.control_dict.write_interval = 0.05
    params.control_dict.write_control = "adjustableRunTime"
    params.control_dict.write_precision = 12
    params.control_dict.time_precision = 12

    params.fv_solution.solvers.p.solver = "PCG"

    return Simul(params)


def test_init(sim_tgv):
    sim = sim_tgv

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    paths_in_tiny = [
        path.relative_to(path_tiny)
        for path in path_tiny.rglob("*")
        if not path.is_dir() and not path.name.startswith("README")
    ]

    for name in paths_in_tiny:
        path_manual = path_tiny / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists()
        text_produced = path_produced.read_text()
        assert text_produced == text_manual, name


def test_list(sim_tgv):
    sim = sim_tgv
    sim.make.list()
    # problem: clean remove .xml files (bash function cleanAuxiliary)
    # sim.make.exec("clean")

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run


path_foam_clean = shutil.which("foamCleanTutorials")


def test_clean_load(sim_tgv):
    sim = sim_tgv

    if path_foam_clean is not None:
        # problem: clean remove .xml files (bash function cleanAuxiliary)
        sim.make.exec("clean")

    sim2 = load(sim.path_run)
    assert sim2.path_run == sim.path_run


path_foam_executable = shutil.which("icoFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    params.control_dict.end_time = 0.02

    params.fv_solution.solvers.p.solver = "PCG"

    sim = Simul(params)

    sim.make.exec("run")
