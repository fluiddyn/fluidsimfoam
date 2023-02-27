from fluidsimfoam_tgv import Simul


def test_init_simul():
    params = Simul.create_default_params()

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )
