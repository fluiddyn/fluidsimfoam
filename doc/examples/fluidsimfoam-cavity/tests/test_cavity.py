from pathlib import Path

from fluidsimfoam_cavity import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_reproduce_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cavity"
    params.parallel.nsubdoms = 9
    params.parallel.method = "hierarchical"
    params.parallel.nsubdoms_xyz = "(3 3 1)"
    sim = Simul(params)
    check_saved_case(here / "saved_cases/cavity", sim.path_run)


@skipif_executable_not_available("icoFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cavity"
    delta_t = params.control_dict.delta_t
    params.control_dict.end_time = delta_t
    params.control_dict.write_interval = 1
    params.parallel.nsubdoms = 2
    params.parallel.method = "simple"
    params.parallel.nsubdoms_xyz = [2, 1, 1]
    sim = Simul(params)
    sim.make.exec("run")
    sim.output.fields.read_field("U", time_approx="last")
