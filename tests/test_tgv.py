from pathlib import Path
from time import sleep

import numpy as np
import pytest
from fluidsimfoam_tgv import Simul

from fluidsimfoam import load
from fluidsimfoam.foam_input_files import (
    FoamInputFile,
    VolScalarField,
    VolVectorField,
)
from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent

path_saved_case = here / "saved_cases/tiny-tgv"


@pytest.fixture(scope="function")
def sim_tgv():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/tgv"

    params.control_dict.end_time = 0.3
    params.control_dict.delta_t = 0.05
    params.control_dict.write_interval = 0.05
    params.control_dict.write_control = "adjustableRunTime"
    params.control_dict.write_precision = 12
    params.control_dict.time_precision = 12

    params.fv_solution.solvers.p.solver = "PCG"

    params.init_fields.type = "codestream"
    return Simul(params)


def test_init(sim_tgv):
    sim = sim_tgv
    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )
    check_saved_case(path_saved_case, sim.path_run)


def test_list(sim_tgv):
    sim = sim_tgv
    sim.make.list()
    # problem: clean remove .xml files (bash function cleanAuxiliary)
    # sim.make.exec("clean")

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run


@skipif_executable_not_available("foamCleanTutorials")
def test_clean_load(sim_tgv):
    sim = sim_tgv
    sim.make.exec("clean")
    sim2 = load(sim.path_run)
    assert sim2.path_run == sim.path_run


def test_read_files_overwrite(sim_tgv):
    sim = sim_tgv
    input_files = sim.input_files

    field_p = input_files.p.read()
    field_u = input_files.u.read()
    tree_control_dict = input_files.control_dict.read()

    assert isinstance(field_p, VolScalarField)
    assert isinstance(field_u, VolVectorField)
    assert isinstance(tree_control_dict, FoamInputFile)

    field_p.tree.info["object"] = "bar"
    input_files.p.overwrite(field_p)

    field_p.tree.info["object"] = "foo"
    field_p.overwrite()
    field_p = input_files.p.read()
    assert field_p.tree.info["object"] == "foo"

    tree_control_dict.children["startTime"] = 10.0
    input_files.control_dict.overwrite(tree_control_dict)

    tree_control_dict.children["startTime"] = 1.0
    tree_control_dict.overwrite()

    tree_control_dict = input_files.control_dict.read()
    assert tree_control_dict.children["startTime"] == 1.0

    sim.params.control_dict.write_precision = precision = 6
    input_files.control_dict.generate_file()
    tree_control_dict = input_files.control_dict.read()
    assert tree_control_dict.children["writePrecision"] == precision


@skipif_executable_not_available("blockMesh")
def test_get_cells_coords():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/tgv"
    sim = Simul(params)
    x, y, z = sim.oper.get_cells_coords()
    nx = sim.params.block_mesh_dict.nx
    assert len(x) == nx**3
    assert x[1] - x[0] - 6.28318530718 / nx < 1e-10

    input_files = sim.input_files
    field_u = input_files.u.read()
    arr = field_u.get_array()
    arr.fill(10.0)
    field_u.set_values(arr)
    field_u.overwrite()

    field_u = input_files.u.read()
    arr1 = field_u.get_array()
    assert np.allclose(arr1, arr)


@skipif_executable_not_available("icoFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/tgv"
    params.control_dict.end_time = 0.02
    params.fv_solution.solvers.p.solver = "PCG"
    sim = Simul(params)
    sim.make.exec("run")


@skipif_executable_not_available("icoFoam")
def test_run_exec_async():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/tgv"
    sim = Simul(params)
    process = sim.make.exec_async("run")
    # we need to be sure that the time loop is started before stopping it
    while sim.output.log.time_last is None:
        sleep(0.02)

    time_last = sim.output.log.time_last

    while sim.output.log.time_last == time_last:
        sleep(0.02)

    time, residual = sim.output.log.get_last_residual()

    assert isinstance(time, float)
    assert isinstance(residual, float)

    sim.stop_time_loop()
    assert process.returncode == 0

    sim.output.log.plot_residuals(tmin=0.02)
    sim.output.log.plot_clock_times()
    field = sim.output.fields.read_field("U", time_approx="last")
    arr = field.get_array()
    assert isinstance(arr, np.ndarray)

    sim.output.fields.get_saved_times()

    sim.output.fields.plot_boundary(
        "lowerBoundary", color="g", mesh_opacity=0.05, show=False
    )
    sim.output.fields.plot_boundary(
        "lowerBoundary", color="b", mesh_opacity=0.05, add_legend=True, show=False
    )
    sim.output.fields.plot_mesh(color="g", style="points", show=False)
    sim.output.fields.plot_profile(
        show=False,
        point0=[0, 0, 0],
        point1=[0, 0, 7],
        variable="U",
        ylabel="U(m/s)",
        title="Velocity",
    )
    sim.output.fields.plot_contour(
        variable="U", equation="y=1.95", mesh_opacity=0.1, component=1, show=False
    )
    sim.output.fields.plot_contour(
        equation="z=5.111",
        mesh_opacity=0.1,
        variable="U",
        contour=True,
        show=False,
    )
