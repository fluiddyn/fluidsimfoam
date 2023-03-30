import os
from pathlib import Path
from pprint import pprint
from fluidsimfoam.foam_input_files import parse, dump

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])

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


for path_dir in tutorials_dir.rglob("*"):
    if not path_dir.is_dir() or not is_example_dir(path_dir):
        continue

    nb_examples += 1
    for path_file in path_dir.rglob("*"):
        if path_file.name != "fvSolution":
            continue

        print(f"{nb_examples}: {path_file}")
        text = path_file.read_text()

        tree = parse(text)

        assert tree == parse(dump(tree))

print(nb_examples)
