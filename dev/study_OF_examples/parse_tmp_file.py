from pathlib import Path

from fluidsimfoam.foam_input_files import parse, dump

tree = parse(Path("tmp_file").read_text())

dumped = tree.dump()
assert tree == parse(dumped)