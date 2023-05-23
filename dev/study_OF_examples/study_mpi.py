import os
from pathlib import Path
from pprint import pprint

from fluidsimfoam.foam_input_files import dump, parse

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])
# tutorials_dir = Path.home() / "Dev/sedfoam/tutorials/"

print(f"{tutorials_dir = }")

methods = set()


for path in tutorials_dir.rglob("*"):
    if path.is_dir() or path.name != "decomposeParDict":
        continue

    print(path)

    text = path.read_text()
    tree = parse(text)

    try:
        method = tree.children["method"]
    except (TypeError, KeyError):
        method = None
        print("no method!!!")
        continue

    methods.add(method)

    if method == "simple":
        code = dump(tree)
        print(code)


print("methods:")
pprint(methods)
