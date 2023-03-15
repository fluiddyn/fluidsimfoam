import os
from pathlib import Path
from pprint import pprint

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
        if path_file.is_dir() or any(
            name in path_file.name for name in ignore_files
        ):
            continue
        path_file = str(path_file.relative_to(path_dir))
        if path_file not in input_files:
            input_files[path_file] = 1
        else:
            input_files[path_file] += 1


input_files = {key: val for key, val in input_files.items() if val > 4}
sorted_input_files = sorted(
    input_files.items(), key=lambda item: item[1], reverse=True
)
sorted_input_files_dict = dict(sorted_input_files)
print(f"{nb_examples = }")
pprint(sorted_input_files_dict, sort_dicts=False)
