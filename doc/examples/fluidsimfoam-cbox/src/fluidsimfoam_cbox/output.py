from fluidsimfoam.output import Output


class OutputCBOX(Output):
    do_use_blockmesh = True

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)
