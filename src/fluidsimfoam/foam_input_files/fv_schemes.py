"""Helper to create fvSchemes files

"""

from inflection import underscore

from fluidsimfoam.foam_input_files import FoamInputFile


class FvSchemesHelper:
    keys = ["ddt", "grad", "div", "laplacian", "interpolation", "snGrad"]

    def __init__(
        self,
        ddt=None,
        grad=None,
        div=None,
        laplacian=None,
        interpolation=None,
        sn_grad=None,
    ):
        for key in self.keys:
            loc = locals()
            arg_name = underscore(key)
            if loc[arg_name] is None:
                loc[arg_name] = {}
            setattr(self, arg_name, loc[arg_name])

    def modif_params(self, params):
        fv_schemes = params._set_child("fv_schemes", doc="""TODO""")
        for key in self.keys:
            name = underscore(key)
            fv_schemes._set_child(name, attribs=getattr(self, name))

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": "dictionary",
                "object": "fvSchemes",
            }
        )

        for key in self.keys:
            params_key = params.fv_schemes[underscore(key)]
            attribs = {k: params_key[k] for k in params_key._key_attribs}
            attribs = {k: v for k, v in attribs.items() if v is not False}
            tree.set_child(key, attribs)

        return tree
