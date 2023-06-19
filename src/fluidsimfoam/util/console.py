"""Console script functions

"""

import argparse
import datetime
import re
import sys
from functools import partial
from importlib import resources
from pathlib import Path
from pprint import pprint
from shutil import copy, which
from string import Template
from subprocess import run

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
    from fluidsimfoam.foam_input_files import FoamFormatError, format_code

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

    if args.from_solver is not None:
        raise NotImplementedError("Sorry, option -s is not yet implemented...")

    if args.from_case is not None:
        path_case = Path(args.from_case)
        if not path_case.exists():
            print(f"{path_case} does not exist.")
            sys.exit(1)

    if args.destination is not None:
        path_destination = Path(args.destination).resolve()
    else:
        path_destination = path_dir_results

    name_project = f"fluidsimfoam-{args.name}"
    suffix_for_module = args.name.replace("-", "_")
    name_package = f"fluidsimfoam_{suffix_for_module}"
    path_result = path_destination / name_project

    if path_result.exists():
        print(f"{path_result} already exists.")
        sys.exit(1)

    print(f"Let's initiate the solver {path_result}")

    if args.from_case is not None:
        print(f"Using case {path_case}")

        path_files = {}
        for name_dir in ("system", "constant", "0", "0.orig"):
            paths_in_dir = sorted(path_case.glob(name_dir + "/*"))

            path_files[name_dir] = [
                path.relative_to(path_case)
                for path in paths_in_dir
                if path.is_file() and not path.is_symlink()
            ]

            path_subdirs = [
                path
                for path in paths_in_dir
                if path.is_dir() and path.name != "polyMesh"
            ]

            for path_subdir in path_subdirs:
                path_files[name_dir].extend(
                    sorted(
                        path.relative_to(path_case)
                        for path in path_subdir.glob("*")
                        if path.is_file() and not path.is_symlink()
                    )
                )

        internal_symlinks = {}
        for path in path_case.rglob("*"):
            if not path.is_symlink():
                continue
            path_resolved = path.resolve()
            if path_case not in path_resolved.parents:
                raise NotImplementedError("External symlinks not implemented")
            internal_symlinks[str(path.relative_to(path_case))] = str(
                path.readlink()
            )

        if internal_symlinks:
            print("internal_symlinks:")
            pprint(internal_symlinks)

        paths_orig = path_files.pop("0.orig")
        if paths_orig:
            path_files["0"] = paths_orig

        name_files = {}
        for name_dir in path_files.keys():
            name_files[name_dir] = sorted(
                str(Path(*p.parts[1:])) for p in path_files[name_dir]
            )

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
        "suffix_for_class": camelize(suffix_for_module),
        "name_variables": str(name_files["0"]),
        "name_system_files": str(name_files["system"]),
        "name_constant_files": str(name_files["constant"]),
        "internal_symlinks": str(internal_symlinks),
    }

    templates = {}

    for name in ["LICENSE", "README.md", "pyproject.toml"]:
        relative_path = name
        templates[relative_path] = name + ".template"

    path_package = path_result / f"src/{name_package}"
    for name in ["__init__.py", "output.py"]:
        relative_path = path_package / name
        templates[relative_path] = name + ".template"

    path_templates = path_package / "templates"
    path_templates.mkdir(parents=True)
    (path_templates / "__init__.py").touch()
    name = "tasks.py"
    templates[path_templates / name] = name + ".template"

    path_tests = path_result / "tests"
    path_tests.mkdir()
    templates[
        path_tests / f"test_{suffix_for_module}.py"
    ] = "test_generated_solver.py.template"

    for relative_path, template in templates.items():
        template_res = resources.files("fluidsimfoam.resources").joinpath(
            template
        )
        with resources.as_file(template_res) as path:
            code = path.read_text()
        code = Template(code).substitute(substitutions)
        (path_result / relative_path).write_text(code)

    path_saved_case = path_tests / "saved_cases/case0"
    path_saved_case.mkdir(parents=True)

    for name_dir, path_files_dir in path_files.items():
        as_field = name_dir == "0"
        path_dir_saved_case = path_saved_case / name_dir
        path_dir_saved_case.mkdir()

        for relative_path in path_files_dir:
            code = (path_case / relative_path).read_text()
            try:
                code = format_code(code, as_field=as_field)
            except FoamFormatError:
                print(f"Not able to format file {relative_path}")

            # Trim trailing whitespaces
            code = re.sub(r"\s+\n", "\n", code).strip() + "\n"

            if "{{" in code:
                # Escape jinja syntax
                code_template = "{% raw %}" + code.strip() + "{% endraw %}\n"
            else:
                code_template = code

            if name_dir == "0":
                parts = list(relative_path.parts)
                if parts[0] == "0.orig":
                    parts[0] = "0"
                    relative_path = Path(*parts)

            path_in_saved_case = path_saved_case / relative_path
            path_in_saved_case.parent.mkdir(exist_ok=True)
            path_in_saved_case.write_text(code)

            path_template = path_templates / relative_path
            path_template = path_template.with_name(path_template.name + ".jinja")
            path_template.parent.mkdir(exist_ok=True)
            path_template.write_text(code_template)

    # create the symlinks
    for relative_path, target in internal_symlinks.items():
        path_in_saved_case = path_saved_case / relative_path
        path_in_saved_case.parent.mkdir(exist_ok=True)
        path_in_saved_case.symlink_to(target)

    if args.from_case is not None:
        for path in path_case.glob("All*"):
            if path.exists():
                copy(path, path_saved_case)

    if which("black") is not None:
        run(["black", "-l", "82", str(path_result)])

    print(
        f"""

New solver {name_project} created! You can now install and test it to check if
it reproduces your initial case.

```
cd {path_result}
pip install -e .
pytest tests -vv
```

You can then improve your fluidsimfoam solver by modifying its files
(especially the file src/{name_package}/output.py). Examples can be found in
https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples

    """
    )
