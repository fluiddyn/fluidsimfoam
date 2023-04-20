from fluidsimfoam.foam_input_files.ast import Dict
from fluidsimfoam.output import Output


class OutputCBox(Output):
    """Output for the cbox solver"""

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    def make_tree_turbulence_properties(self, params):
        tree = super().make_tree_turbulence_properties(params)
        # TODO: fix this bad API (need for `Dict` and `name`)
        tree.children["RAS"] = Dict(
            {"RASModel": "kEpsilon", "turbulence": "on", "printCoeffs": "on"},
            name="RAS",
        )
        return tree


OutputCBox.system_files_names.append("blockMeshDict")
