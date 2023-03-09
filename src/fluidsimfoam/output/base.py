import inspect
import textwrap
from pathlib import Path

from inflection import underscore

from fluiddyn.io import stdout_redirected
from fluiddyn.util import mpi
from fluidsim_core.output import OutputCore
from fluidsim_core.params import iter_complete_params
from fluidsimfoam.log import logger
from fluidsimfoam.solvers import get_solver_package


class Output(OutputCore):
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
        """Set the the classes for info_solver.classes.Output"""
        pass

    @staticmethod
    def _complete_params_with_default(params, info_solver):
        """This static method is used to complete the *params* container."""

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

        if sim:
            # initialize objects
            dict_classes = sim.info.solver.classes.Output.import_classes()
            for cls_name, Class in dict_classes.items():
                if isinstance(self, Class):
                    continue
                obj_name = underscore(cls_name)
                setattr(self, obj_name, Class(self))
                self.sim._objects_to_print += "{:28s}{}\n".format(
                    f"sim.output.{obj_name}: ", Class
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
        for name in (
            "fv_solution",
            "fv_schemes",
            "control_dict",
            "block_mesh_dict",
            "transport_properties",
            "turbulence_properties",
            "p",
            "u",
        ):
            try:
                template = getattr(self, f"template_{name}")
            except AttributeError:
                pass
            else:
                if template is not None:
                    getattr(self, f"write_{name}")(template)

    def write_fv_solution(self, template):
        output = template.render(data=self.sim.params.fv_solution)

        assert output.endswith("\n")

        output_path = self.sim.path_run / "system/fvSolution"

        with open(output_path, "w") as file:
            file.write(output)

    def write_fv_schemes(self, template):
        output = template.render(data=self.sim.params.fv_schemes)

        output_path = self.sim.path_run / "system/fvSchemes"

        with open(output_path, "w") as file:
            file.write(output)

    def write_control_dict(self, template):
        output = template.render(data=self.sim.params.control_dict)

        output_path = self.sim.path_run / "system/controlDict"

        with open(output_path, "w") as file:
            file.write(output)

    def write_block_mesh_dict(self, template):
        output = template.render(data=self.sim.params.block_mesh_dict)

        output_path = self.sim.path_run / "system/blockMeshDict"

        with open(output_path, "w") as file:
            file.write(output)

    def write_transport_properties(self, template):
        output = template.render(data=self.sim.params.transport_properties)

        output_path = self.sim.path_run / "constant/transportProperties"

        with open(output_path, "w") as file:
            file.write(output)

    def write_turbulence_properties(self, template):
        output = template.render(data=self.sim.params.turbulence_properties)

        output_path = self.sim.path_run / "constant/turbulenceProperties"

        with open(output_path, "w") as file:
            file.write(output)

    def write_p(self, template):
        output = template.render(data=self.sim.params.p)

        output_path = self.sim.path_run / "0/p"

        with open(output_path, "w") as file:
            file.write(output)

    def write_u(self, template):
        output = template.render(data=self.sim.params.u)

        output_path = self.sim.path_run / "0/U"

        with open(output_path, "w") as file:
            file.write(output)
