#!/usr/bin/env python3

import sys
from pathlib import Path

from fluidsimfoam.foam_input_files import dump, parse

if len(sys.argv) == 2:
    path = Path(sys.argv[-1])
else:
    path = Path("tmp_file")

assert path.exists()

text = path.read_text()
tree = parse(text)

dumped = dump(tree)

here = Path(__file__).absolute().parent
tmp_dumped = here / "tmp_dumped.txt"
tmp_dumped.write_text(dumped)

assert tree == parse(dumped)
