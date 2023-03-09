from pathlib import Path

from fluidsimfoam_tgv import Simul
from fluidsimfoam import load

here = Path(__file__).absolute().parent

path_tiny = here / "pure_openfoam_cases/tiny-tgv"


def test_init_simul():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    params.fv_solution.solvers.p.solver = "PCG"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run
    for name in ("fvSolution", "fvSchemes"):
        path_produced = sim.path_run / "system" / name
        path_manual = path_tiny / "system" / name

        text_manual = path_manual.read_text()
        assert path_produced.exists()

        text_produced = path_produced.read_text()

        assert text_manual == text_produced
