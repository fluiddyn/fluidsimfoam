from pathlib import Path

from fluidsimfoam_dam import Simul

from fluidsimfoam.testing import check_saved_case, skipif_executable_not_available

here = Path(__file__).absolute().parent


def test_generate_base_case():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/dam"
    params.parallel.method = "simple"
    params.parallel.nsubdoms = 4
    params.parallel.nsubdoms_xyz = [2, 2, 1]
    sim = Simul(params)
    check_saved_case(here / "saved_cases/case0", sim.path_run)


@skipif_executable_not_available("interFoam")
def test_run():
    params = Simul.create_default_params()
    params.output.sub_directory = "tests_fluidsimfoam/dam"
    params.parallel.nsubdoms = 1
    params.control_dict.end_time = 0.1
    sim = Simul(params)
    sim.make.exec("run")

    sim.output.fields.plot_mesh(color="w", show=False)

    sim.output.fields.plot_boundary(
        "lowerWall", color="r", mesh_opacity=0.05, show=False
    )

    sim.output.fields.plot_contour(
        variable="U", mesh_opacity=0.1, component=1, show=False
    )

    sim.output.fields.plot_contour(
        variable="p_rgh", mesh_opacity=0.1, time=10, show=False
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
