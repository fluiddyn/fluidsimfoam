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
    ConstantFileHelper,
    FoamInputFile,
)
from fluidsimfoam.foam_input_files.generators import (
    InputFiles,
    new_file_generator_class,
)
from fluidsimfoam.log import logger
from fluidsimfoam.solvers import get_solver_package


class Output(OutputCore):
    variable_names = ["p", "U"]
    constant_files_names = ["transportProperties", "turbulenceProperties"]
    system_files_names = ["controlDict", "fvSchemes", "fvSolution"]
    default_control_dict_params = DEFAULT_CONTROL_DICT

    helper_turbulence_properties = ConstantFileHelper(
        "turbulenceProperties", {"simulationType": "laminar"}
    )

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
            classes[variable_name.replace(".", "_")] = new_file_generator_class(
                variable_name
            )

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
        for cls_name, Class in dict_classes.items():
            if isinstance(self, Class):
                continue
            obj_name = underscore(cls_name)
            self.sim._objects_to_print += "{:28s}{}\n".format(
                f"sim.output.{obj_name}: ", Class
            )
            setattr(self, obj_name, Class(self))

        if not hasattr(self, "_file_generators_classes"):
            self._setup_file_generators_classes()
        for_str_input_files = {}
        for cls_name, Class in self._file_generators_classes.items():
            obj_name = underscore(cls_name)

            if Class.dir_name not in for_str_input_files:
                for_str_input_files[Class.dir_name] = [cls_name]
            else:
                for_str_input_files[Class.dir_name].append(cls_name)
            setattr(self.input_files, obj_name, Class(self))

        if for_str_input_files:
            self.sim._objects_to_print += "input_files:\n"
            for dir_name, input_files in for_str_input_files.items():
                self.sim._objects_to_print += (
                    f"  - in {dir_name + ':':12s}{' '.join(input_files)}\n"
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

        for file_generator in vars(self.input_files).values():
            if hasattr(
                file_generator, "generate_file"
            ) and file_generator.rel_path.startswith("system"):
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
        path_tasks_py = self.input_files.templates_dir / "tasks.py"
        if not path_tasks_py.exists():
            raise RuntimeError(
                "tasks.py missing in solver templates_dir "
                f"{self.input_files.templates_dir}"
            )
        shutil.copy(path_tasks_py, self.sim.path_run)

        for file_generator in vars(self.input_files).values():
            if hasattr(
                file_generator, "generate_file"
            ) and not file_generator.rel_path.startswith("system"):
                # system files are already generated
                file_generator.generate_file()

    @classmethod
    def _complete_params_control_dict(cls, params):
        attribs = {
            underscore(key): value
            for key, value in cls.default_control_dict_params.items()
        }

        params._set_child(
            "control_dict",
            attribs=attribs,
            doc="""See https://doc.cfd.direct/openfoam/user-guide-v6/controldict""",
        )

    def make_tree_control_dict(self, params):
        children = {
            key: params.control_dict[underscore(key)]
            for key in self.default_control_dict_params.keys()
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
