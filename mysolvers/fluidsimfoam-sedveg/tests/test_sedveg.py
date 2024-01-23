from pathlib import Path

from fluidsimfoam_sedveg import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_generate_base_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sedveg"
    #params.init_fields.type = "codestream"
    sim = Simul(params)
    check_saved_case(here / "saved_cases/case0", sim.path_run)


@skipif_executable_not_available("sedFoam_rbgh")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sedveg"
    #params.init_fields.type = "tanh"
    # change parameters to get a very short and small simulation
    params.control_dict.end_time = 2
    params.control_dict.write_interval = 1
    sim = Simul(params)
    sim.make.exec("run")
