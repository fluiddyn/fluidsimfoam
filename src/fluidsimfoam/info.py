"""Base class for ``Simul.InfoSolver``"""

from fluidsim_core.info import InfoSolverCore


class InfoSolver(InfoSolverCore):
    """Contains the information on which classes are used in a solver"""

    def _init_root(self):
        super()._init_root()

        self.classes._set_child(
            "Output",
            attribs={
                "module_name": "fluidsimfoam.output",
                "class_name": "Output",
            },
        )
        self.classes._set_child(
            "Oper",
            attribs={
                "module_name": "fluidsimfoam.operators",
                "class_name": "Operators",
            },
        )
        self.classes._set_child(
            "InitFields",
            attribs={
                "module_name": "fluidsimfoam.init_fields",
                "class_name": "InitFields",
            },
        )
        self.classes._set_child(
            "Make",
            attribs={
                "module_name": "fluidsimfoam.make",
                "class_name": "MakeInvoke",
            },
        )

    def complete_with_classes(self):
        """Populate info solver by executing ``_complete_info_solver`` class
        methods
        """
        dict_classes = self.import_classes()
        for Class in list(dict_classes.values()):
            if hasattr(Class, "_complete_info_solver"):
                Class._complete_info_solver(self)
