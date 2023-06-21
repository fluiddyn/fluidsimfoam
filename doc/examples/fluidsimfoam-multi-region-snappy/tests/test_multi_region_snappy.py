from pathlib import Path

from fluidsimfoam_multi_region_snappy import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_generate_base_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/multi-region-snappy"
    params.parallel.nsubdoms = 4
    params.parallel_mesh.nsubdoms = 6
    sim = Simul(params)
    check_saved_case(here / "saved_cases/case0", sim.path_run)


@skipif_executable_not_available("chtMultiRegionFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/multi-region-snappy"
    # change parameters to get a very short and small simulation
    params.control_dict.end_time = 0.002
    sim = Simul(params)
    sim.make.exec("run")
    sim.make.exec("clean")


@skipif_executable_not_available("chtMultiRegionFoam")
def test_run_parallel():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/multi-region-snappy"
    params.parallel.nsubdoms = 4
    params.parallel_mesh.nsubdoms = 6
    # change parameters to get a very short and small simulation
    params.control_dict.end_time = 0.002
    sim = Simul(params)
    sim.make.exec("run")
    sim.make.exec("clean")
