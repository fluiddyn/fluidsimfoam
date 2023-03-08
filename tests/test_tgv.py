from pathlib import Path

from fluidsimfoam_tgv import Simul
from fluidsimfoam import load

here = Path(__file__).absolute().parent

path_tiny = here / "pure_openfoam_cases/tiny-tgv"

path_fvsolution = path_tiny / "system/fvSolution"


def test_init_simul():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    params.fv_solutions.solvers.p.solver = "PCG"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run

    text_manual = path_fvsolution.read_text()

    path_sim_fvsolution = sim.path_run / "system/fvSolution"

    assert path_sim_fvsolution.exists()

    text_produced = path_sim_fvsolution.read_text()

    assert text_manual == text_produced
