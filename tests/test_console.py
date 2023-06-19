import os
import sys
from pathlib import Path
from subprocess import run
from tempfile import mkdtemp
from unittest.mock import patch

import pytest

from fluidsimfoam.util.console import (
    initiate_solver,
    print_versions,
    start_ipython_load_sim,
)


def test_info():
    print_versions()


def test_start_ipython_load_sim(mocker):
    mocker.patch("IPython.start_ipython")
    start_ipython_load_sim()


path_cases = [Path(__file__).absolute().parent / "saved_cases/tiny-tgv"]


path_foam_tutorials = os.environ.get("FOAM_TUTORIALS", None)
FLUIDSIMFOAM_LONG_TESTS = int(os.environ.get("FLUIDSIMFOAM_LONG_TESTS", 0))
if path_foam_tutorials is not None and FLUIDSIMFOAM_LONG_TESTS:
    # taken from https://www.openfoam.com/documentation/tutorial-guide
    main_tutorials = """
        incompressible/icoFoam/cavity/cavity
        electromagnetics/mhdFoam/hartmann
        basic/potentialFoam/cylinder
        incompressible/simpleFoam/pitzDaily
        compressible/sonicFoam/laminar/forwardStep
        compressible/sonicLiquidFoam/decompressionTank
        multiphase/interFoam/laminar/damBreak/damBreak
        stressAnalysis/solidDisplacementFoam/plateHole
    """.strip().split(
        "\n"
    )
    # advanced solver (multiRegion + snappyHexMesh)
    main_tutorials.append(
        "heatTransfer/chtMultiRegionFoam/snappyMultiRegionHeater"
    )
    path_foam_tutorials = Path(path_foam_tutorials)
    path_main_tutorials = [
        path_foam_tutorials / rel_path.strip() for rel_path in main_tutorials
    ]
    path_cases.extend(path_main_tutorials)


@pytest.mark.parametrize("path_case", path_cases)
def test_initiate_solver(path_case):
    assert path_case.exists()

    tmp_dir = mkdtemp()

    short_name = path_case.name + "_for_test"

    with patch.object(
        sys,
        "argv",
        [
            "fluidsimfoam-initiate-solver",
            short_name,
            "-c",
            str(path_case),
            "-d",
            str(tmp_dir),
        ],
    ):
        initiate_solver()

    name_project = f"fluidsimfoam-{short_name}"
    path_solver = Path(tmp_dir) / name_project
    assert path_solver.exists()

    name_4module = short_name.replace("-", "_")
    relative_paths = ["LICENSE", "README.md", "pyproject.toml"]
    relative_paths.extend(
        f"src/fluidsimfoam_{name_4module}/" + name
        for name in ["__init__.py", "output.py"]
    )
    relative_paths.extend(
        [
            f"src/fluidsimfoam_{name_4module}/templates/tasks.py",
            f"tests/test_{name_4module}.py",
        ]
    )
    if (path_case / "Allrun").exists():
        relative_paths.append("tests/saved_cases/case0/Allrun")

    for relative_path in relative_paths:
        path_to_check = path_solver / relative_path
        assert path_to_check.exists(), path_to_check

    for commands in (
        "pip install -e .",
        "pytest tests",
        f"pip uninstall {name_project} -y",
    ):
        process = run(commands.split(), cwd=path_solver)
        process.check_returncode()
