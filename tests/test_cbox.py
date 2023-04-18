from pathlib import Path

from fluidsimfoam_cbox import Simul

from fluidsimfoam import load

here = Path(__file__).absolute().parent

path_sim0 = here / "pure_openfoam_cases/cbox/sim0"
path_sim1 = here / "pure_openfoam_cases/cbox/sim1"
path_sim2 = here / "pure_openfoam_cases/cbox/sim2"


def test_init_simul_sim0():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/sim0"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run

    paths_in_sim = [
        path.relative_to(path_sim0)
        for path in path_sim0.rglob("*")
        if not path.is_dir() and not path.name.startswith("README")
    ]

    for name in paths_in_sim:
        path_manual = path_sim0 / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists()
        text_produced = path_produced.read_text()
        assert text_manual == text_produced


def test_init_simul_sim1():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/sim1"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run

    paths_in_sim = [
        path.relative_to(path_sim1)
        for path in path_sim1.rglob("*")
        if not path.is_dir() and not path.name.startswith("README")
    ]

    for name in paths_in_sim:
        path_manual = path_sim1 / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists()
        text_produced = path_produced.read_text()
        assert text_manual == text_produced


def test_init_simul_sim2():
    params = Simul.create_default_params()

    params.output.sub_directory = "tests_fluidsimfoam/cbox/sim2"

    sim = Simul(params)

    assert all(
        (sim.path_run / name).exists()
        for name in ("info_solver.xml", "params_simul.xml")
    )

    sim2 = load(sim.path_run)

    assert sim2.path_run == sim.path_run

    paths_in_sim = [
        path.relative_to(path_sim2)
        for path in path_sim2.rglob("*")
        if not path.is_dir() and not path.name.startswith("README")
    ]

    for name in paths_in_sim:
        path_manual = path_sim2 / name
        text_manual = path_manual.read_text()
        path_produced = sim.path_run / name
        assert path_produced.exists()
        text_produced = path_produced.read_text()
        assert text_manual == text_produced
