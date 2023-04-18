from abc import ABC, abstractmethod
from inspect import getmodule
from pathlib import Path

import jinja2
from inflection import underscore


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
        with open(self.output.sim.path_run / self.rel_path, "w") as file:
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

            if (
                self.output.input_files.templates_dir / self.template_name
            ).exists():
                raise RuntimeError(
                    "Fluidsimfoam solver issue: "
                    f"2 concurrent methods to produce {self.rel_path}:\n"
                    f"- template in {self.output.input_files.templates_dir},\n"
                    f"- function output.make_code_{self._name}.\n"
                    "Remove the file or the function (or make it equal to None)."
                )

            return method(self.output.sim.params)
        except AttributeError:
            template = self.output.input_files.get_template(self.template_name)
            return template.render(params=self.output.sim.params)


class BlockMeshGenerator(FileGenerator):
    rel_path = "system/blockMeshDict"
    template_name = "blockMeshDict.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("block_mesh_dict", doc="""TODO""")


class FvSolutionGenerator(FileGenerator):
    rel_path = "system/fvSolution"
    template_name = "fvSolution.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("fv_solution", doc="""TODO""")
        solvers = params.fv_solution._set_child("solvers", doc="""TODO""")
        attribs = {
            "solver": "PCG",
            "preconditioner": "DIC",
            "tolerance": 1e-06,
            "relTol": 0.01,
        }

        solvers._set_child("p", attribs=attribs)
        solvers._set_child("pFinal", attribs=attribs)
        solvers.pFinal.relTol = 0
        solvers._set_child(
            "U",
            attribs={
                "solver": "PBiCGStab",
                "preconditioner": "DILU",
                "tolerance": 1e-08,
                "relTol": 0,
            },
        )

        params.fv_solution._set_child(
            "piso",
            attribs={
                "nCorrectors": 2,
                "nNonOrthogonalCorrectors": 1,
                "pRefPoint": "(0 0 0)",
                "pRefValue": 0,
            },
        )


class ControlDictGenerator(FileGenerator):
    rel_path = "system/controlDict"
    template_name = "controlDict.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("control_dict", doc="""TODO""")


class FvSchemesGenerator(FileGenerator):
    rel_path = "system/fvSchemes"
    template_name = "fvSchemes.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        fv_schemes = params._set_child("fv_schemes", doc="""TODO""")
        fv_schemes._set_child("ddtSchemes", attribs={"default": "backward"})
        fv_schemes._set_child("gradSchemes", attribs={"default": "leastSquares"})
        fv_schemes._set_child("divSchemes", attribs={"default": "none"})
        fv_schemes._set_child(
            "laplacianSchemes", attribs={"default": "Gauss linear corrected"}
        )
        fv_schemes._set_child(
            "interpolationSchemes", attribs={"default": "linear"}
        )
        fv_schemes._set_child("snGradSchemes", attribs={"default": "corrected"})


class TransportPropertiesGenerator(FileGenerator):
    rel_path = "constant/transportProperties"
    template_name = "transportProperties.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("transport_properties", doc="""TODO""")


class TurbulencePropertiesGenerator(FileGenerator):
    rel_path = "constant/turbulenceProperties"
    template_name = "turbulenceProperties.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child(
            "turbulence_properties",
            attribs={"simulation_type": "laminar"},
            doc="""TODO""",
        )


class PGenerator(FileGenerator):
    rel_path = "0/p"
    template_name = "p.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("p", doc="""TODO""")


class UGenerator(FileGenerator):
    rel_path = "0/U"
    template_name = "U.jinja"

    @classmethod
    def _complete_params_with_default(cls, params):
        params._set_child("u", doc="""TODO""")
