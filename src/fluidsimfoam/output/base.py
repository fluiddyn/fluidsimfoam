import inspect
import textwrap
from pathlib import Path

from inflection import underscore

from fluiddyn.io import stdout_redirected
from fluiddyn.util import mpi
from fluidsim_core.output import OutputCore
from fluidsim_core.params import iter_complete_params
from fluidsimfoam.foam_input_files import DEFAULT_HEADER, FoamInputFile
from fluidsimfoam.foam_input_files.generators import (
    FileGeneratorABC,
    InputFiles,
    new_file_generator_class,
)
from fluidsimfoam.log import logger
from fluidsimfoam.solvers import get_solver_package


class Output(OutputCore):
    do_use_blockmesh = False
    variable_names = ["p", "U"]
    constant_files_names = ["transportProperties", "turbulenceProperties"]

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

        module_name = "fluidsimfoam.foam_input_files.generators"

        for class_name in (
            "FvSolution",
            "ControlDict",
            "FvSchemes",
        ):
            classes._set_child(
                class_name,
                attribs={
                    "module_name": module_name,
                    "class_name": class_name + "Generator",
                },
            )

        if cls.do_use_blockmesh:
            classes._set_child(
                "BlockMesh",
                attribs={
                    "module_name": module_name,
                    "class_name": "BlockMeshGenerator",
                },
            )

    @classmethod
    def _setup_file_generators_classes(cls):
        classes = cls._file_generators_classes = {}
        for variable_name in cls.variable_names:
            classes[variable_name] = new_file_generator_class(variable_name)

        for file_name in cls.constant_files_names:
            classes[file_name] = new_file_generator_class(file_name, "constant")

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

        self.input_files = InputFiles(self)
        # initialize objects
        dict_classes = sim.info.solver.classes.Output.import_classes()

        if not self._file_generators_classes:
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

    def post_init_create_additional_source_files(self):
        """Create the files from their template"""
        (self.sim.path_run / "system").mkdir()
        (self.sim.path_run / "0").mkdir()
        (self.sim.path_run / "constant").mkdir()

        for file_generator in vars(self.input_files).values():
            if hasattr(file_generator, "generate_file"):
                file_generator.generate_file()

    def make_code_turbulence_properties(self, params):
        try:
            params.turbulence_properties
        except AttributeError:
            raise Exception

        tree = FoamInputFile(
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
        return tree.dump()

    @classmethod
    def _complete_params_turbulence_properties(cls, params):
        params._set_child(
            "turbulence_properties",
            attribs={"simulation_type": "laminar"},
            doc="""TODO""",
        )
