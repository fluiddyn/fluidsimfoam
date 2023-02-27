from fluidsimfoam_tgv import Simul


def test_init_simul():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )
