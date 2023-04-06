import os
import sys
from pathlib import Path
from pprint import pprint

import lark
from rich.progress import track

from fluidsimfoam.foam_input_files import dump, parse

CHECK = "check" in sys.argv

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])

# name_studied_file = "fvSolution"  # No parser issue
# name_studied_file = "controlDict"  # No parser issue
# name_studied_file = "fvSchemes"  # No parser issue
name_studied_file = "blockMeshDict"
# name_studied_file = "turbulenceProperties"  # No parser issue
# name_studied_file = "U"
# name_studied_file = "decomposeParDict"  # No parser issue
# name_studied_file = "transportProperties"  # No parser issue
# name_studied_file = "g"
# name_studied_file = "p"

print(f"Parse all {name_studied_file} files in {tutorials_dir}")

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


bad_files = set(
    [
        # semicolon missing
        "heatTransfer/chtMultiRegionSimpleFoam/cpuCabinet/system/domain0/fvSolution",
        "heatTransfer/chtMultiRegionFoam/coolingCylinder2D/system/fluid/fvSolution",
        "heatTransfer/chtMultiRegionFoam/coolingSphere/templates/system/fluid/fvSolution",
        # too much }
        "heatTransfer/chtMultiRegionFoam/coolingCylinder2D/system/controlDict",
        "incompressible/pimpleFoam/RAS/wingMotion/wingMotion_snappyHexMesh/system/controlDict",
        "incompressible/pimpleFoam/laminar/filmPanel0/0.orig/U",
        # dict named "(oil mercury)"
        "multiphase/multiphaseEulerFoam/laminar/damBreak4phase/constant/transportProperties",
        # wrong dimension style [m s^-1]
        "incompressible/pimpleFoam/RAS/TJunctionFan/0.orig/U",
        "mesh/snappyHexMesh/addLayersToFaceZone/0.orig/U",
    ]
)

errors = {"Empty file": 0, "parser error": 0, "wrong files": 0}


file_classes = {}
names_level0 = {}
names_level1 = {}
names_level2 = {}

issues = []

paths = []

for path_dir in tutorials_dir.rglob("*"):
    if not path_dir.is_dir() or not is_example_dir(path_dir):
        continue

    for path_file in path_dir.rglob("*"):
        if path_file.name != name_studied_file:
            continue

        nb_examples += 1
        path_rel = path_file.relative_to(tutorials_dir)

        if str(path_rel) in bad_files:
            errors["wrong files"] += 1
            continue

        paths.append(path_file)

print(f"{len(paths)} files found")
if not paths:
    sys.exit()

for path_file in track(paths):
    text = path_file.read_text()
    try:
        tree = parse(text)
        if CHECK:
            assert tree == parse(dump(tree))
    except (lark.exceptions.LarkError, AssertionError):
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

        if isinstance(tree.children[f"{name}"], dict):
            for name1 in tree.children[f"{name}"].keys():
                key = f"{name}/{name1}"
                try:
                    names_level1[key] += 1
                except KeyError:
                    names_level1[key] = 1

                if isinstance(tree.children[f"{name}"][f"{name1}"], dict):
                    for name2 in tree.children[f"{name}"][f"{name1}"].keys():
                        key = f"{name}/{name1}/{name2}"
                        try:
                            names_level2[key] += 1
                        except KeyError:
                            names_level2[key] = 1


print(f"{nb_examples = }")

pprint(errors, sort_dicts=False)

names_level0 = {key: val for key, val in names_level0.items() if val > 5}
names_level0 = dict(
    sorted(names_level0.items(), key=lambda item: item[1], reverse=True)
)
pprint(names_level0, sort_dicts=False)

names_level1 = {key: val for key, val in names_level1.items() if val > 50}
names_level1 = dict(
    sorted(names_level1.items(), key=lambda item: item[1], reverse=True)
)
if names_level1:
    print("\nnames_level1:")
    pprint(names_level1, sort_dicts=False)

names_level2 = {key: val for key, val in names_level2.items() if val > 100}
names_level2 = dict(
    sorted(names_level2.items(), key=lambda item: item[1], reverse=True)
)

if names_level2:
    print("\nnames_level2:")
    pprint(names_level2, sort_dicts=False)

print("FoamInfo classes:")
pprint(file_classes)

if not CHECK:
    print("Warning: tree == parse(dump(tree)) not checked")

if issues:
    txt_issues = "\n".join(str(p) for p in issues)
    with open("tmp_issues.txt", "w") as file:
        file.write(txt_issues + "\n")
    print(
        f"Fluidsimfoam issues ({len(issues)/nb_examples*100:.2f} % of files): "
        "(saved in tmp_issues.txt)\n" + txt_issues
    )
else:
    print(f"No parser issue for {name_studied_file}!")
