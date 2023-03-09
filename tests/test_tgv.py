from fluidsimfoam_tgv import Simul

from fluidsimfoam import load


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
