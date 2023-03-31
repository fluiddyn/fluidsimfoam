import os
from pathlib import Path
from pprint import pprint

import lark

from fluidsimfoam.foam_input_files import parse, dump

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])

print(f"{tutorials_dir = }")

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
        "heatTransfer/chtMultiRegionFoam/coolingCylinder2D/system/fluid/fvSolution",
        "heatTransfer/chtMultiRegionFoam/coolingSphere/templates/system/fluid/fvSolution",
        "incompressible/pimpleFoam/laminar/movingCone/system/fvSolution",
    ]
)

content = {"Empty file": 0, "parser error": 0, "wrong files": 0}
content_detailed = {"dictionary": 0}

issues = []

for path_dir in tutorials_dir.rglob("*"):
    if not path_dir.is_dir() or not is_example_dir(path_dir):
        continue

    for path_file in path_dir.rglob("*"):
        if path_file.name != "fvSolution":
            continue

        nb_examples += 1
        path_rel = path_file.relative_to(tutorials_dir)

        if str(path_rel) in bad_files:
            content["wrong files"] += 1
            continue

        text = path_file.read_text()

        try:
            tree = parse(text)
            try:
                if tree.info["class"] == "dictionary":
                    content_detailed["dictionary"] += 1
                for key in tree.children.keys():
                    if key not in content:
                        content[key] = 1
                    else:
                        content[key] += 1
                    if isinstance(tree.children[key], dict):
                        for key1 in tree.children[key].keys():
                            if key1 not in content_detailed:
                                content_detailed[key1] = 1
                            else:
                                content_detailed[key1] += 1

            except AttributeError:
                content["Empty file"] += 1
                continue
            assert tree == parse(dump(tree))
        except lark.exceptions.LarkError:
            content["parser error"] += 1
            print(f"Lark exception for file\n{path_file}")
            issues.append(path_file)
            continue
        print(f"{nb_examples:4d}: {path_rel}")


txt_issues = "\n".join(str(p) for p in issues)

with open("tmp_issues.txt", "w") as file:
    file.write(txt_issues + "\n")

print("Issues:\n" + txt_issues + "\n(saved in tmp_issues.txt)")


sorted_content = sorted(content.items(), key=lambda item: item[1], reverse=True)
sorted_content_dict = dict(sorted_content)
print(f"{nb_examples = }")

sorted_content_detailed = sorted(
    content_detailed.items(), key=lambda item: item[1], reverse=True
)
sorted_content_detailed_dict = dict(sorted_content_detailed)

pprint(sorted_content_dict, sort_dicts=False)
pprint(sorted_content_detailed_dict, sort_dicts=False)
