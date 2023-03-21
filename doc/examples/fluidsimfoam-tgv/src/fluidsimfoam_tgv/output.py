from fluidsimfoam.output import Output
from fluidsimfoam.resources import get_base_template


class OutputTGV(Output):
    template_fv_solution = get_base_template("fvSolution.jinja")
    template_fv_schemes = get_base_template("fvSchemes.jinja")
    template_control_dict = get_base_template("controlDict.jinja")
    template_transport_properties = get_base_template("transportProperties.jinja")
    template_turbulence_properties = get_base_template(
        "turbulenceProperties.jinja"
    )
    template_p = get_base_template("p.jinja")
    template_u = get_base_template("U.jinja")

    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the the classes for info_solver.classes.Output"""
        super()._set_info_solver_classes(classes)
