from fluidsimfoam_tgv import Simul


def test_init_simul():
    params = Simul.create_default_params()

    sim = Simul(params)
