from textwrap import dedent

from fluidsimfoam.foam_input_files.fields import VolScalarField, VolVectorField
from fluidsimfoam.output import Output

code_control_dict_functions = dedent(
    """
"""
)


class OutputSED(Output):
    """Output for the SED solver"""

    system_files_names = Output.system_files_names + ["blockMeshDict"]

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    def make_code_control_dict(self, params):
        code = super().make_code_control_dict(params)
        return code + code_control_dict_functions
