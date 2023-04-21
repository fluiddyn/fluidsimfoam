from textwrap import dedent

from fluidsimfoam.output import Output

code_control_dict_functions = dedent(
    """
    functions
    {
        minmaxdomain
        {
            type fieldMinMax;
            //type banana;

            libs ("libfieldFunctionObjects.so");

            enabled true;

            mode component;

            writeControl timeStep;
            writeInterval 1;

            log true;

            fields (p U);
        }
    };
"""
)


class OutputTGV(Output):
    """Output for the TGV solver"""

    system_files_names = Output.system_files_names + ["blockMeshDict"]

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    def make_code_control_dict(self, params):
        code = super().make_code_control_dict(params)
        return code + code_control_dict_functions
