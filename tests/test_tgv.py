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
        assert text_manual == text_produced
