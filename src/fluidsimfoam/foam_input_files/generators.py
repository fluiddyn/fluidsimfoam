from abc import ABC, abstractmethod

import jinja2


class InputFiles:
    """Contain the generator objects"""


class OFInputFileGenerator(ABC):
    rel_path: str

    def __init__(self, output):
        self.output = output

    def generate_file(self):
        """Generate the file"""
        with open(self.output.sim.path_run / self.rel_path, "w") as file:
            file.write(self.generate_code())

    @abstractmethod
    def generate_code(self):
        """Generate the code of the file"""


class FileGeneratorTemplate(OFInputFileGenerator):
    template_name: str

    def generate_code(self):
        """Generate the code of the file from the Jinja template"""

        loader = jinja2.ChoiceLoader(
            [
                jinja2.PackageLoader("fluidsimfoam_tgv", "templates"),
                jinja2.PackageLoader("fluidsimfoam", "resources"),
            ]
        )

        env = jinja2.Environment(
            loader=loader,
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True,
        )

        template = env.get_template(self.template_name)
        return template.render(data=self.output.sim.params)


class BlockMeshGeneratorPython(OFInputFileGenerator):
    pass


class BlockMeshGeneratorTemplate(FileGeneratorTemplate):
    rel_path = "system/blockMeshDict"
    template_name = "blockMeshDict.jinja"
