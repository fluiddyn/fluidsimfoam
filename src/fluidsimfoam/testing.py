"""Testing utilities"""

from pathlib import Path

from fluidsimfoam.foam_input_files import dump, parse


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
            assert text_produced == text_manual, relative_path
