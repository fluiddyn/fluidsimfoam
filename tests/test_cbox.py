from inspect import getmodule
from pathlib import Path

import pandas as pd
import pytest
from fluidsimfoam_cbox import Simul

from fluidsimfoam.output import get_dataframe_from_paths
from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


@pytest.mark.parametrize("index_sim", [0, 1, 2])
def test_init_simul_sim0(index_sim):
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/sim0"

    if index_sim == 1:
        params.constant.transport.nu = 0.002
    elif index_sim == 2:
        params.constant.transport.nu = 0.003
    else:
        # testing params.output.resources
        mod = getmodule(Simul)
        templates_dir = Path(mod.__file__).absolute().parent / "templates"

        params.resources = [
            templates_dir,
            templates_dir / "0/epsilon.jinja",
            str(templates_dir / "0/k.jinja") + " -> 0",
            f"{templates_dir} -> system",
            "package-data(fluidsimfoam_cbox.templates) -> constant",
        ]

    sim = Simul(params)

    path_saved_case = here / f"saved_cases/cbox/sim{index_sim}"
    check_saved_case(
        path_saved_case, sim.path_run, files_compare_tree=["blockMeshDict"]
    )

    if index_sim == 0:
        # testing params.output.resources
        assert (sim.path_run / "templates/0/p_rgh.jinja").exists()
        assert (sim.path_run / "epsilon.jinja").exists()
        assert (sim.path_run / "0/k.jinja").exists()
        assert (sim.path_run / "system/templates/0/epsilon.jinja").exists()
        assert (sim.path_run / "constant/templates/0/epsilon.jinja").exists()


@skipif_executable_not_available("buoyantBoussinesqPimpleFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/cbox/"
    params.control_dict.end_time = 10
    params.control_dict.write_interval = 10
    sim = Simul(params)
    sim.make.exec("run")
    df = get_dataframe_from_paths([sim.path_run])
    assert isinstance(df, pd.DataFrame)
    assert len(df.index) == 1

    sim.output.fields.get_saved_times()
    x, y, z = sim.oper.get_cells_coords()
    assert z.max() - z.min() < 1e-15

    sim.output.fields.plot_mesh(color="w", show=False)

    sim.output.fields.plot_boundary(
        "hot", color="r", mesh_opacity=0.05, show=False
    )
    sim.output.fields.plot_contour(
        variable="U", mesh_opacity=0.1, component=1, show=False
    )
    sim.output.fields.plot_contour(
        variable="T", mesh_opacity=0.1, time=10, show=False
    )
    sim.output.fields.plot_profile(
        show_line_in_domain=False,
        point0=[0.5, 0, 0],
        point1=[0.5, 5, 0],
        variable="U",
        ylabel="U(m/s)",
        title="Velocity",
        show=False,
    )
