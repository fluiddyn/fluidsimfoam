import os
from pathlib import Path

from fluidsimfoam_multi_region_snappy import Simul

from fluidsimfoam.testing import (
    check_saved_case,
    skipif_executable_not_available,
    skipif_openfoam_too_old,
)

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
    sim.output.fields.plot_mesh(color="w", show=False)

    sim.make.exec("clean")


@skipif_executable_not_available("chtMultiRegionFoam")
@skipif_openfoam_too_old
def test_run_parallel():
    os.environ["OMPI_MCA_rmaps_base_oversubscribe"] = "true"
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/multi-region-snappy"
    params.parallel.nsubdoms = 4
    params.parallel_mesh.nsubdoms = 6
    # change parameters to get a very short and small simulation
    params.control_dict.end_time = 0.002
    params.control_dict.write_interval = 0.002
    sim = Simul(params)
    sim.make.exec("run")

    assert len(list(p.name for p in sim.path_run.glob("0.002/*"))) == 6
    assert len(list(p.name for p in sim.path_run.glob("0.002/topAir/*"))) == 8
    assert len(list(p.name for p in sim.path_run.glob("0.002/heater/*"))) == 2
