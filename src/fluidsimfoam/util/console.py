"""Console script functions

"""

import argparse
import datetime
import sys
from functools import partial
from importlib import resources
from pathlib import Path
from pprint import pprint
from string import Template

from inflection import camelize

from fluidsim_core.ipy_load import (
    start_ipython_load_sim as _start_ipython_load_sim,
)
from fluidsim_core.paths import path_dir_results
from fluidsimfoam import __version__ as fluidsimfoam_version
from fluidsimfoam.solvers import available_solvers


def print_versions():
    import fluiddyn
    import fluidsim_core
    import fluidsimfoam

    versions = {"Package": "Version", "-------": "-------"}

    packages = [fluidsimfoam, fluiddyn, fluidsim_core]
    for package in packages:
        versions[package.__name__] = package.__version__

    for pkg_name, version in versions.items():
        print(f"{pkg_name.ljust(15)} {version}")

    names = sorted(set([entry_point.name for entry_point in available_solvers()]))
    print("\nInstalled solvers: " + ", ".join(names))


start_ipython_load_sim = partial(
    _start_ipython_load_sim, load_import="from fluidsimfoam import load"
)


def initiate_solver():
    parser = argparse.ArgumentParser(
        prog="fluidsimfoam-initiate-solver",
        description="Initiate a new solver",
    )

    parser.add_argument("name")

    parser.add_argument("-c", "--from-case")
    parser.add_argument("-s", "--from-solver")
    parser.add_argument("-a", "--author", default="Fluidsimfoam developers")
    parser.add_argument("-d", "--destination")

    args = parser.parse_args()

    print(args)

    if args.from_case is None and args.from_solver is None:
        print("You should at least provide a case (-c) or a solver (-s)")
        sys.exit(1)

    if args.from_case is not None:
        path_case = Path(args.from_case)
        if not path_case.exists():
            print(f"{path_case} does not exist.")
            sys.exit(1)

    if args.destination is not None:
        path_destination = Path(args.destination)
    else:
        path_destination = path_dir_results

    name_project = f"fluidsimfoam-{args.name}"
    suffix_for_module = args.name.replace("-", "_")
    name_package = f"fluidsimfoam_{suffix_for_module}"
    path_result = path_destination / name_project

    if path_result.exists():
        print(f"{path_result} already exists.")
        sys.exit(1)

    print("Let's initiate the solver " f"{name_project} in {path_destination}")

    if args.from_case is not None:
        print(f"Using case {path_case}")

        path_files = {}
        name_files = {}

        for name_dir in ("system", "constant", "0", "0.orig"):
            path_files[name_dir] = sorted(path_case.glob(name_dir + "/*"))

        path_orig = path_files.pop("0.orig")
        if path_orig:
            path_files["0"] = path_orig

        for name_dir in path_files.keys():
            name_files[name_dir] = [p.name for p in path_files[name_dir]]

        pprint(name_files)

    print(f"Making {path_result}")
    path_result.mkdir()

    substitutions = {
        "year": str(datetime.date.today().year),
        "author": args.author,
        "name_short": args.name,
        "name_project": name_project,
        "name_package": name_package,
        "fluidsimfoam_version": fluidsimfoam_version,
        "suffix_for_class": camelize(args.name),
    }

    templates = {}

    for name in ["LICENSE", "README.md", "pyproject.toml"]:
        suffix_path = name
        templates[suffix_path] = name + ".template"

    path_package = path_result / f"src/{name_package}"
    for name in ["__init__.py", "output.py", "tasks.py"]:
        suffix_path = path_package / name
        templates[suffix_path] = name + ".template"

    path_templates = path_package / "templates"
    path_templates.mkdir(parents=True)
    name = "tasks.py"
    templates[path_templates / name] = name + ".template"

    path_tests = path_result / "tests"
    path_tests.mkdir()
    templates[
        path_tests / f"test_{suffix_for_module}.py"
    ] = "test_generated_solver.py.template"

    for suffix_path, template in templates.items():
        template_res = resources.files("fluidsimfoam.resources").joinpath(
            template
        )
        with resources.as_file(template_res) as path:
            code = path.read_text()
        code = Template(code).substitute(substitutions)
        with open(path_result / suffix_path, "w") as file:
            file.write(code)

    path_saved_case = path_tests / "saved_cases/case0"
    path_saved_case.mkdir(parents=True)
