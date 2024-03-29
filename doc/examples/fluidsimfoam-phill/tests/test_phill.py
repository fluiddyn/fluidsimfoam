from pathlib import Path

import pytest
from fluidsimfoam_phill import Simul
from fluidsimfoam_phill.blockmesh import (
    make_code_2d_phill,
    make_code_3d_phill,
    make_code_sinus,
)

from fluidsimfoam.foam_input_files import dump, parse
from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available


@skipif_executable_not_available("postProcess")
def test_reproduce_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/phill"
    params.block_mesh_dict.nx = 11
    params.block_mesh_dict.ny = 7
    params.block_mesh_dict.n_porosity = 4
    params.fv_options.atm_coriolis_u_source.active = True
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


path_data = Path(__file__).absolute().parent / "saved_cases"


@pytest.mark.parametrize(
    "name",
    ["sinus", "2d_phill", "3d_phill"],
)
def test_blockmesh(name):
    params = Simul.create_default_params()

    if name == "sinus":
        params.block_mesh_dict.nx = 11
        params.block_mesh_dict.ny = 7
        params.block_mesh_dict.n_porosity = 4
        path_saved_file = path_data / "case0/system/blockMeshDict"
    elif name == "2d_phill":
        params.block_mesh_dict.nx = 60
        params.block_mesh_dict.ny = 30
        params.block_mesh_dict.nz = 1
        params.block_mesh_dict.n_porosity = 15
        params.block_mesh_dict.lx = 6
        params.block_mesh_dict.ly = 1
        params.block_mesh_dict.lz = 0.01
        params.block_mesh_dict.h_max = 0.2
        params.block_mesh_dict.ly_porosity = 1
        path_saved_file = path_data / "blockmeshdicts/blockMeshDict_2d_phill"
    elif name == "3d_phill":
        params.block_mesh_dict.nx = 20
        params.block_mesh_dict.ny = 20
        params.block_mesh_dict.nz = 20
        params.block_mesh_dict.n_porosity = 10
        params.block_mesh_dict.lx = 10
        params.block_mesh_dict.ly = 10
        params.block_mesh_dict.lz = 10
        params.block_mesh_dict.h_max = 3
        params.block_mesh_dict.ly_porosity = 10
        path_saved_file = path_data / "blockmeshdicts/blockMeshDict_3d_phill"

    make_blockmesh = globals()["make_code_" + name]
    code_from_py = make_blockmesh(params.block_mesh_dict)

    code_saved = path_saved_file.read_text()

    tree_saved_file = parse(code_saved)
    tree_from_py = parse(code_from_py)

    assert dump(tree_saved_file).strip() == dump(tree_from_py).strip()
