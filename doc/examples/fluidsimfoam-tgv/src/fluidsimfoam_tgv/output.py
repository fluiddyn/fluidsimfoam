from fluidsimfoam.output import Output
from fluidsimfoam.resources import get_base_template


class OutputTGV(Output):
    template_fv_solution = get_base_template("fvSolution.jinja")
    template_fv_schemes = get_base_template("fvSchemes.jinja")
