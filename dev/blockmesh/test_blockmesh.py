from pathlib import Path
from textwrap import dedent

import pytest
from cboxmesh import make_block_mesh
from ofblockmeshdicthelper import BlockMeshDict, SimpleGrading, Vertex

from fluidsimfoam.foam_input_files import dump, parse

here = Path(__file__).absolute().parent


def test_cbox_mesh():
    cbox_mesh_produced = make_block_mesh("cbox")
    cbox_mesh_path = here / "blockMeshDict"
    text_cbox_mesh = cbox_mesh_path.read_text()

    tree_cbox_mesh = parse(text_cbox_mesh, grammar="advanced")
    tree_cbox_mesh_produced = parse(cbox_mesh_produced, grammar="advanced")

    assert dump(tree_cbox_mesh).strip() == dump(tree_cbox_mesh_produced).strip()
    # assert text_cbox_mesh == cbox_mesh_produced
