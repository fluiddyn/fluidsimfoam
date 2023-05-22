from pathlib import Path

import numpy as np
from fluidsimfoam_sed import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_ras_1dbedloadturb():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sed"
    params.init_fields.type = "codestream"
    sim = Simul(params)
    check_saved_case(here / "saved_cases/RAS/1DBedLoadTurb", sim.path_run)


@skipif_executable_not_available("sedFoam_rbgh")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sed"
    params.init_fields.type = "tanh"
    params.control_dict.end_time = 0.001
    sim = Simul(params)
    sim.make.exec("run")

    field = sim.output.fields.read_field("alpha.a", time_approx="last")
    arr = field.get_array()
    assert isinstance(arr, np.ndarray)

    sim.output.fields.plot_field("alpha.a")
