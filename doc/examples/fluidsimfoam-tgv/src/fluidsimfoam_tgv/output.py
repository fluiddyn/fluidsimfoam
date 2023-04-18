from fluidsimfoam.output import Output


class OutputTGV(Output):
    """Output for the TGV solver"""

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)


OutputTGV.system_files_names.append("blockMeshDict")
