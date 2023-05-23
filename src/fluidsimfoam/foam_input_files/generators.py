"""Internal machinery to generate the OpenFOAM input files"""

from abc import ABC, abstractmethod
from inspect import getmodule
from pathlib import Path

import jinja2
from inflection import camelize, underscore

from fluiddyn.util import import_class
from fluidsimfoam.foam_input_files import FileHelper, parse, read_field_file


class InputFiles:
    """Container of the generator objects"""

    def __init__(self, output):
        self.output = output
        mod = getmodule(type(output.sim))
        self.templates_dir = Path(mod.__file__).absolute().parent / "templates"

        loader = jinja2.ChoiceLoader(
            [
                jinja2.PackageLoader(mod.__package__, "templates"),
                jinja2.PackageLoader("fluidsimfoam", "resources"),
            ]
        )

        self.jinja_env = jinja2.Environment(
            loader=loader,
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True,
        )

    def get_template(self, template_name):
        return self.jinja_env.get_template(template_name)


class FileGeneratorABC(ABC):
    rel_path: str

    def __init__(self, output):
        self.output = output
        self.input_files = output.input_files

    def generate_file(self, params=None):
        """Generate the file"""
        if params is None:
            params = self.output.sim.params

        code = self.generate_code(params)
        if code is False:
            return

        with open(self.output.path_run / self.rel_path, "w") as file:
            file.write(code)

    @abstractmethod
    def generate_code(self):
        """Generate the code of the file"""

    def read(self):
        path = self.output.path_run / self.rel_path
        if any(
            self.rel_path.startswith(start) for start in ["system", "constant"]
        ):
            tree = parse(path.read_text())
            tree.path = path
            return tree
        else:
            return read_field_file(path)

    def overwrite(self, dumpable):
        with open(self.output.path_run / self.rel_path, "w") as file:
            file.write(dumpable.dump())


class FileGenerator(FileGeneratorABC):
    template_name: str

    def __init__(self, output):
        super().__init__(output)

    def generate_code(self, params=None):
        """Generate the code of the file from ...

        - a method named like `sim.output._make_code_block_mesh_dict`,
        - or a Jinja template.
        """
        if params is None:
            params = self.output.sim.params

        try:
            make_code = getattr(self.output, "_make_code_" + self._name)
        except AttributeError:
            make_code = None

        if make_code is None:
            try:
                make_tree = getattr(self.output, "_make_tree_" + self._name)
            except AttributeError:
                make_tree = None

            if make_tree is None:
                try:
                    helper = getattr(self.output, "_helper_" + self._name)
                except AttributeError:
                    pass
                else:
                    if isinstance(helper, FileHelper):
                        make_tree = helper.make_tree

            if make_tree is not None:

                def make_code(params_):
                    tree = make_tree(params_)
                    if tree is False:
                        return False
                    return tree.dump()

        if make_code is None:
            template = self.input_files.get_template(self.template_name)
            return template.render(params=params)

        if (self.input_files.templates_dir / self.template_name).exists():
            raise RuntimeError(
                "Fluidsimfoam solver issue: "
                f"2 concurrent methods to produce {self.rel_path}:\n"
                f"- template in {self.input_files.templates_dir},\n"
                f"- function output._make_code_{self._name}.\n"
                "Remove the file or the function (or make it equal to None)."
            )

        return make_code(params)

    @classmethod
    def _complete_params_with_default(cls, params, info_solver):
        output_cls = import_class(
            info_solver.classes.Output.module_name,
            info_solver.classes.Output.class_name,
        )
        try:
            complete_params = getattr(output_cls, "_complete_params_" + cls._name)
        except AttributeError:
            complete_params = None

        if complete_params is None:
            try:
                helper = getattr(output_cls, "_helper_" + cls._name)
            except AttributeError:
                pass
            else:
                if isinstance(helper, FileHelper):
                    complete_params = helper.complete_params

        if complete_params is not None:
            complete_params(params)


def new_file_generator_class(file_name, dir_name="0"):
    cls_name = f"FileGenerator{camelize(file_name)}"
    return type(
        cls_name,
        (FileGenerator,),
        {
            "dir_name": dir_name,
            "rel_path": f"{dir_name}/{file_name}",
            "template_name": f"{file_name}.jinja",
            "_name": underscore(file_name.replace(".", "_")),
        },
    )
