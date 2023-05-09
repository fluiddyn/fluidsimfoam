import shutil
from pathlib import Path

import pytest
from fluidsimfoam_sed import Simul

from fluidsimfoam.testing import check_saved_case

here = Path(__file__).absolute().parent

path_saved_case = here / "saved_cases/RAS/1DBedLoadTurb"


def test_ras_1dbedloadturb():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sed"
    params.init_fields.type = "codestream"
    sim = Simul(params)
    check_saved_case(path_saved_case, sim.path_run)


path_foam_executable = shutil.which("sedFoam_rbgh")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable sedFoam_rbgh not available"
)
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/sed"
    params.init_fields.type = "tanh"
    params.control_dict.end_time = 0.001
    sim = Simul(params)
    sim.make.exec("run")
