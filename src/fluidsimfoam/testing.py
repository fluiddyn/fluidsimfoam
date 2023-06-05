"""Testing utilities"""

import shutil
from pathlib import Path

import pytest

from fluidsimfoam.foam_input_files import dump, parse


class skipif_executable_not_available:
    def __init__(self, command_name):
        path_foam_executable = shutil.which(command_name)

        self.skipif = pytest.mark.skipif(
            path_foam_executable is None,
            reason=f"executable '{command_name}' not available",
        )

    def __call__(self, func):
        return self.skipif(func)


def check_saved_case(path_saved_case, path_run, files_compare_tree=None):
    if files_compare_tree is None:
        files_compare_tree = []

    paths_in_sim = [
        path.relative_to(path_saved_case)
        for path in path_saved_case.rglob("*")
        if not path.is_dir()
        and not any(path.name.startswith(s) for s in ("README", "All"))
        and not path.parent.name == "polyMesh"
    ]

    for relative_path in paths_in_sim:
        path_manual = path_saved_case / relative_path
        text_manual = path_manual.read_text()
        if str(relative_path.parent) == "0_org":
            relative_path = Path("0") / relative_path.name
        path_produced = path_run / relative_path
        assert path_produced.exists(), relative_path
        text_produced = path_produced.read_text()

        if relative_path.name in files_compare_tree:
            tree_saved_file = parse(text_manual)
            tree_from_py = parse(text_produced)
            assert dump(tree_saved_file).strip() == dump(tree_from_py).strip()
        else:
            if text_produced != text_manual:
                print(f"meld {path_produced} {path_manual}")
            assert text_produced == text_manual, relative_path
