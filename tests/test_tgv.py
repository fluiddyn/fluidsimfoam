import shutil
from pathlib import Path

import numpy as np
import pytest
from fluidsimfoam_tgv import Simul

from fluidsimfoam import load
from fluidsimfoam.foam_input_files.ast import FoamInputFile
from fluidsimfoam.foam_input_files.fields import VolScalarField, VolVectorField

here = Path(__file__).absolute().parent

path_tiny = here / "pure_openfoam_cases/tiny-tgv"


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

    paths_in_tiny = [
        path.relative_to(path_tiny)
        for path in path_tiny.rglob("*")
        if not path.is_dir()
        and not path.name.startswith("README")
        and not path.parent.name == "polyMesh"
    ]

    for name in paths_in_tiny:
        path_manual = path_tiny / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists()
        text_produced = path_produced.read_text()
        assert text_produced == text_manual, name


def test_list(sim_tgv):
    sim = sim_tgv
    sim.make.list()
    # problem: clean remove .xml files (bash function cleanAuxiliary)
    # sim.make.exec("clean")

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run


path_foam_clean = shutil.which("foamCleanTutorials")


def test_clean_load(sim_tgv):
    sim = sim_tgv

    if path_foam_clean is not None:
        # problem: clean remove .xml files (bash function cleanAuxiliary)
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


path_blockmesh = shutil.which("blockMesh")


@pytest.mark.skipif(
    path_blockmesh is None, reason="executable blockMesh not available"
)
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


path_foam_executable = shutil.which("icoFoam")


@pytest.mark.skipif(
    path_foam_executable is None, reason="executable icoFoam not available"
)
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/tgv"
    params.control_dict.end_time = 0.02
    params.fv_solution.solvers.p.solver = "PCG"
    sim = Simul(params)
    sim.make.exec("run")
