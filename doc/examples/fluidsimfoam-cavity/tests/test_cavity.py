import shutil
from pathlib import Path

import pytest
from fluidsimfoam_cavity import Simul

from fluidsimfoam.testing import check_saved_case

here = Path(__file__).absolute().parent

path_saved_case = here / "saved_cases/cavity"


def test_reproduce_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cavity"
    sim = Simul(params)
    check_saved_case(path_saved_case, sim.path_run)


path_foam_executable = shutil.which("icoFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cavity"
    params.control_dict.end_time = 0.001
    sim = Simul(params)
    sim.make.exec("run")
