import shutil
from pathlib import Path

import pytest
from fluidsimfoam_phill import Simul

from fluidsimfoam.foam_input_files import dump, parse

here = Path(__file__).absolute().parent


path_foam_executable = shutil.which("interFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/phill/"

    params.control_dict.end_time = 0.002

    sim = Simul(params)

    sim.make.exec("run")
    sim.make.exec("clean")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run_2d_topo_3d():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/phill/"

    params.control_dict.end_time = 0.001
    params.block_mesh_dict.lz = 0.2
    params.block_mesh_dict.nz = 4
    sim = Simul(params)

    sim.make.exec("run")
    sim.make.exec("clean")
