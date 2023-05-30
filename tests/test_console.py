import sys
from pathlib import Path
from subprocess import run
from tempfile import mkdtemp
from unittest.mock import patch

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


def test_initiate_solver():
    path_case = Path(__file__).absolute().parent / "saved_cases/tiny-tgv"
    assert path_case.exists()

    tmp_dir = mkdtemp()

    short_name = "tgv2"

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

    relative_paths = ["LICENSE", "README.md", "pyproject.toml"]
    relative_paths.extend(
        "src/fluidsimfoam_tgv2/" + name for name in ["__init__.py", "output.py"]
    )
    relative_paths.extend(
        [
            "src/fluidsimfoam_tgv2/templates/tasks.py",
            "tests/test_tgv2.py",
            "tests/saved_cases/case0",
        ]
    )

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
