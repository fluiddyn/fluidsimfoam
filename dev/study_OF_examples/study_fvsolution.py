import os
from pathlib import Path
from pprint import pprint

import lark
from rich.progress import track

from fluidsimfoam.foam_input_files import dump, parse

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])

print(f"Parse all fvSolution files in {tutorials_dir}")

input_files = {}

nb_examples = 0
ignore_files = [
    "Allrun",
    "Allclean",
    "Allrun.pre",
    "README",
    "README.md",
    "Allrun-parallel",
]


def is_example_dir(path):
    return (path / "constant").is_dir() and (path / "system").is_dir()


bad_files = set([])

errors = {"Empty file": 0, "parser error": 0, "wrong files": 0}


file_classes = {}
names_level0 = {}

issues = []

paths = []

for path_dir in tutorials_dir.rglob("*"):
    if not path_dir.is_dir() or not is_example_dir(path_dir):
        continue

    for path_file in path_dir.rglob("*"):
        if path_file.name != "fvSolution":
            continue

        nb_examples += 1
        path_rel = path_file.relative_to(tutorials_dir)

        if str(path_rel) in bad_files:
            errors["wrong files"] += 1
            continue

        paths.append(path_file)


for path_file in track(paths):
    text = path_file.read_text()
    try:
        tree = parse(text)
        assert tree == parse(dump(tree))
    except lark.exceptions.LarkError:
        errors["parser error"] += 1
        issues.append(path_file)
        continue

    if not hasattr(tree, "children"):
        errors["Empty file"] += 1
        continue

    try:
        file_classes[tree.info["class"]] += 1
    except KeyError:
        file_classes[tree.info["class"]] = 1

    for name in tree.children.keys():
        try:
            names_level0[name] += 1
        except KeyError:
            names_level0[name] = 1


print(f"{nb_examples = }")

txt_issues = "\n".join(str(p) for p in issues)
with open("tmp_issues.txt", "w") as file:
    file.write(txt_issues + "\n")
print("Fluidsimfoam issues: (saved in tmp_issues.txt)\n" + txt_issues)

pprint(errors, sort_dicts=False)

names_level0 = dict(
    sorted(names_level0.items(), key=lambda item: item[1], reverse=True)
)
pprint(names_level0, sort_dicts=False)
print("FoamInfo classes:")
pprint(file_classes)
