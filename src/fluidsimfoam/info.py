from fluidsim_core.info import InfoSolverCore


class InfoSolver(InfoSolverCore):
    def _init_root(self):
        super()._init_root()

        # self._set_child("classes")
        # self.classes._set_child(
        #     "Oper",
        #     attribs={"module_name": "snek5000.operators", "class_name": "Operators"},
        # )
        self.classes._set_child(
            "Output",
            attribs={
                "module_name": "fluidsimfoam.output",
                "class_name": "Output",
            },
        )
        # self.classes._set_child(
        #     "Make", attribs={"module_name": "snek5000.make", "class_name": "Make"}
        # )

    def complete_with_classes(self):
        """Populate info solver by executing ``_complete_info_solver`` class
        methods
        """
        dict_classes = self.import_classes()
        for Class in list(dict_classes.values()):
            if hasattr(Class, "_complete_info_solver"):
                Class._complete_info_solver(self)
