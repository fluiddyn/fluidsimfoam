import inspect
import shutil
import textwrap
from pathlib import Path

from inflection import underscore

from fluiddyn.io import stdout_redirected
from fluiddyn.util import mpi
from fluidsim_core.output import OutputCore
from fluidsim_core.params import iter_complete_params
from fluidsimfoam.foam_input_files import (
    DEFAULT_CONTROL_DICT,
    DEFAULT_HEADER,
    FoamInputFile,
)
from fluidsimfoam.foam_input_files.generators import (
    FileGeneratorABC,
    InputFiles,
    new_file_generator_class,
)
from fluidsimfoam.log import logger
from fluidsimfoam.solvers import get_solver_package


class Output(OutputCore):
    variable_names = ["p", "U"]
    constant_files_names = ["transportProperties", "turbulenceProperties"]
    system_files_names = ["controlDict", "fvSchemes", "fvSolution"]

    @classmethod
    def _complete_info_solver(cls, info_solver):
        """Complete the info_solver instance with child class details (module
        and class names).

        """
        classes = info_solver.classes.Output._set_child("classes")
        cls._set_info_solver_classes(classes)
        # iteratively call _complete_info_solver of the above classes
        info_solver.classes.Output.complete_with_classes()

    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the classes for info_solver.classes.Output"""

    @classmethod
    def _setup_file_generators_classes(cls):
        classes = cls._file_generators_classes = {}
        for variable_name in cls.variable_names:
            classes[variable_name] = new_file_generator_class(variable_name)

        for file_name in cls.constant_files_names:
            classes[file_name] = new_file_generator_class(file_name, "constant")

        for file_name in cls.system_files_names:
            classes[file_name] = new_file_generator_class(file_name, "system")

    @classmethod
    def _complete_params_with_default(cls, params, info_solver):
        """This static method is used to complete the *params* container."""

        cls._setup_file_generators_classes()
        iter_complete_params(
            params, info_solver, cls._file_generators_classes.values()
        )

        # Bare minimum
        params._set_attribs(dict(NEW_DIR_RESULTS=True, short_name_type_run="run"))
        params._set_child(
            "output", attribs={"HAS_TO_SAVE": True, "sub_directory": ""}
        )
        params.output._set_doc(
            textwrap.dedent(
                """
    - ``HAS_TO_SAVE``: bool (default: True) If False, nothing new is saved in
      the directory of the simulation.
    - ``sub_directory``: str (default: "") A name of a sub-directory (relative
      to $FLUIDDYN_PATH_SCRATCH) wherein the directory of the simulation
      (``path_run``) is saved.

"""
            )
        )

        dict_classes = info_solver.classes.Output.import_classes()
        iter_complete_params(params, info_solver, dict_classes.values())

    def __init__(self, sim=None, params=None):
        self.sim = sim
        try:
            self.name_solver = sim.info.solver.short_name
        except AttributeError:
            pass
        else:
            self.package = get_solver_package(self.name_solver)

        self.path_solver_package = self.get_path_solver_package()

        if sim:
            # self.oper = sim.oper
            self.params = sim.params.output
            super().__init__(sim)
        elif params:
            # At least initialize params
            self.params = params.output
        else:
            self.params = None
            logger.warning(
                "Initializing Output class without sim or params might lead to errors."
            )

        if not sim:
            return

        self.path_run = Path(self.path_run)

        self.input_files = InputFiles(self)
        # initialize objects
        dict_classes = sim.info.solver.classes.Output.import_classes()

        if not hasattr(self, "_file_generators_classes"):
            self._setup_file_generators_classes()
        dict_classes.update(self._file_generators_classes)

        for_str_input_files = []
        for cls_name, Class in dict_classes.items():
            if isinstance(self, Class):
                continue
            obj_name = underscore(cls_name)

            if issubclass(Class, FileGeneratorABC):
                obj_containing = self.input_files
                for_str_input_files.append(cls_name)
            else:
                obj_containing = self
                self.sim._objects_to_print += "{:28s}{}\n".format(
                    f"sim.output.{obj_name}: ", Class
                )

            setattr(obj_containing, obj_name, Class(self))

        if for_str_input_files:
            self.sim._objects_to_print += (
                f"{'input files:':28s}{' '.join(for_str_input_files)}\n"
            )

        if not (
            mpi.rank == 0
            and self._has_to_save
            and self.sim.params.NEW_DIR_RESULTS
        ):
            return

        (self.path_run / "system").mkdir()
        (self.path_run / "0").mkdir()
        (self.path_run / "constant").mkdir()

        try:
            file_generator = getattr(self.input_files, "block_mesh_dict")
        except AttributeError:
            pass
        else:
            file_generator.generate_file()

    @classmethod
    def get_path_solver_package(cls):
        """Get the path towards the solver package."""
        return Path(inspect.getmodule(cls).__file__).parent

    def post_init(self):
        """Logs info on instantiated classes"""

        if mpi.rank == 0:
            print(f"path_run: {self.path_run}")

        # This also calls _save_info_solver_params_xml
        with stdout_redirected():
            super().post_init()

        logger.info(self.sim._objects_to_print)

        # Write input files of the simulation
        if (
            mpi.rank == 0
            and self._has_to_save
            and self.sim.params.NEW_DIR_RESULTS
        ):
            self.post_init_create_additional_source_files()

        # OpenFOAM cleanup removes .xml files!
        path_run = Path(self.path_run)
        path_info_fluidsim = path_run / ".data_fluidsim"
        path_info_fluidsim.mkdir(exist_ok=True)
        for file_name in ("info_solver.xml", "params_simul.xml"):
            path_new = path_info_fluidsim / file_name
            if path_new.exists():
                continue
            shutil.copy(path_run / file_name, path_new)

    def post_init_create_additional_source_files(self):
        """Create the files from their template"""
        for name, file_generator in vars(self.input_files).items():
            if name == "block_mesh_dict":
                # already produced during __init__
                continue
            if hasattr(file_generator, "generate_file"):
                file_generator.generate_file()

        path_tasks_py = self.input_files.templates_dir / "tasks.py"
        if not path_tasks_py.exists():
            raise RuntimeError(
                "tasks.py missing in solver templates_dir "
                f"{self.input_files.templates_dir}"
            )
        shutil.copy(path_tasks_py, self.sim.path_run)

    @classmethod
    def _complete_params_control_dict(cls, params):
        attribs = {
            underscore(key): value for key, value in DEFAULT_CONTROL_DICT.items()
        }

        params._set_child(
            "control_dict",
            attribs=attribs,
            doc="""See https://doc.cfd.direct/openfoam/user-guide-v6/controldict""",
        )

    def make_tree_control_dict(self, params):
        children = {
            key: params.control_dict[underscore(key)]
            for key in DEFAULT_CONTROL_DICT.keys()
        }

        tree = FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "location": '"system"',
                "object": "controlDict",
            },
            children=children,
            header=DEFAULT_HEADER,
        )
        return tree

    def make_code_control_dict(self, params):
        tree = self.make_tree_control_dict(params)
        return tree.dump()

    @classmethod
    def _complete_params_turbulence_properties(cls, params):
        params._set_child(
            "turbulence_properties",
            attribs={"simulation_type": "laminar"},
            doc="""TODO""",
        )

    def make_tree_turbulence_properties(self, params):
        return FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "object": "turbulenceProperties",
            },
            children={
                "simulationType": params.turbulence_properties.simulation_type
            },
            header=DEFAULT_HEADER,
        )

    @classmethod
    def _complete_params_fv_solution(cls, params):
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

    @classmethod
    def _complete_params_fv_schemes(cls, params):
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

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        default = {
            "nx": 40,
            "ny": 40,
            "nz": 40,
            "lx": 1.0,
            "ly": 1.0,
            "lz": 1.0,
            "metric": "m",
            "scale": None,
        }

        params._set_child(
            "block_mesh_dict",
            attribs=default,
            doc="""TODO""",
        )
