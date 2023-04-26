from abc import ABC, abstractmethod
from inspect import getmodule
from pathlib import Path

import jinja2
from inflection import camelize, underscore

from fluiddyn.util import import_class


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

    def generate_file(self):
        """Generate the file"""
        with open(self.output.path_run / self.rel_path, "w") as file:
            file.write(self.generate_code())

    @abstractmethod
    def generate_code(self):
        """Generate the code of the file"""


class FileGenerator(FileGeneratorABC):
    template_name: str

    def __init__(self, output):
        super().__init__(output)
        self._name = underscore(Path(self.rel_path).name)

    def generate_code(self):
        """Generate the code of the file from ...

        - a method named like `sim.output.make_code_block_mesh_dict`,
        - or a Jinja template.
        """
        try:
            method = getattr(self.output, "make_code_" + self._name)
            if method is None:
                raise AttributeError
        except AttributeError:
            try:
                make_tree = getattr(self.output, "make_tree_" + self._name)
                if make_tree is None:
                    raise AttributeError
            except AttributeError:
                template = self.output.input_files.get_template(
                    self.template_name
                )
                return template.render(params=self.output.sim.params)
            else:

                def method(params):
                    return make_tree(params).dump()

        if (self.output.input_files.templates_dir / self.template_name).exists():
            raise RuntimeError(
                "Fluidsimfoam solver issue: "
                f"2 concurrent methods to produce {self.rel_path}:\n"
                f"- template in {self.output.input_files.templates_dir},\n"
                f"- function output.make_code_{self._name}.\n"
                "Remove the file or the function (or make it equal to None)."
            )

        return method(self.output.sim.params)

    @classmethod
    def _complete_params_with_default(cls, params, info_solver):
        output_cls = import_class(
            info_solver.classes.Output.module_name,
            info_solver.classes.Output.class_name,
        )

        try:
            method = getattr(output_cls, "_complete_params_" + cls._name)
            if method is None:
                raise AttributeError
        except AttributeError:
            pass
        else:
            method(params)


def new_file_generator_class(file_name, dir_name="0"):
    cls_name = f"FileGenerator{camelize(file_name)}"
    return type(
        cls_name,
        (FileGenerator,),
        {
            "rel_path": f"{dir_name}/{file_name}",
            "template_name": f"{file_name}.jinja",
            "_name": underscore(file_name),
        },
    )
