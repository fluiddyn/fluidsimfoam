from pathlib import Path

from fluidsimfoam_phill import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available


@skipif_executable_not_available("postProcess")
def test_reproduce_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/phill"
    params.block_mesh_dict.nx = 11
    params.block_mesh_dict.ny = 7
    params.block_mesh_dict.ny_porosity = 4
    sim = Simul(params)
    here = Path(__file__).absolute().parent
    check_saved_case(here / "saved_cases/case0", sim.path_run)


@skipif_executable_not_available("icoFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/phill"
    params.control_dict.end_time = 0.001
    sim = Simul(params)
    sim.make.exec("run")