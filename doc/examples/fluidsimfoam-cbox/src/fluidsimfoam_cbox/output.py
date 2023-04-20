from fluidsimfoam.foam_input_files import DEFAULT_HEADER, Dict, FoamInputFile
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

    def make_tree_transport_properties(self, params):
        return FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "object": "transportProperties",
            },
            children={
                "transportModel": "Newtonian",
                # // Laminar viscosity
                "nu": 1e-03,
                # // Thermal expansion coefficient
                "beta": 1.88583,
                # // Reference temperature
                "TRef": 300,
                # // Laminar Prandtl number
                "Pr": 1.0,
                # // Turbulent Prandtl number
                "Prt": 1.0,
            },
            header=DEFAULT_HEADER,
            comments={
                "nu": "Laminar viscosity",
                "beta": "Thermal expansion coefficient",
                "TRef": "Reference temperature",
                "Pr": "Laminar Prandtl number",
                "Prt": "Turbulent Prandtl number",
            },
        )


OutputCBox.system_files_names.append("blockMeshDict")
OutputCBox.constant_files_names.append("g")
