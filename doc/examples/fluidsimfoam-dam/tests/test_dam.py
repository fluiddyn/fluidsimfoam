from pathlib import Path

from fluidsimfoam_dam import Simul

from fluidsimfoam.testing import check_saved_case

here = Path(__file__).absolute().parent


def test_generate_base_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/dam"
    params.parallel.method = "simple"
    params.parallel.nsubdoms = 4
    params.parallel.nsubdoms_xyz = [2, 2, 1]
    sim = Simul(params)
    check_saved_case(here / "saved_cases/case0", sim.path_run)
