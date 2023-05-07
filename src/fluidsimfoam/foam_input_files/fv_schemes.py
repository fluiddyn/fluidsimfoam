"""Helper to create fvSchemes files

"""

from inflection import underscore

from fluidsimfoam.foam_input_files import FileHelper, FoamInputFile


class FvSchemesHelper(FileHelper):
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

            data = loc[arg_name]

            if isinstance(data, str):
                data_as_str = data
                data = {}
                for line in data_as_str.strip().split("\n"):
                    line = line.strip()
                    if any(
                        line.startswith(comment_char)
                        for comment_char in ("//", "#")
                    ):
                        continue

                    key, value = line.split(maxsplit=1)
                    data[key] = value

            setattr(self, arg_name, data)

        self.other_dict = {}

    def complete_params(self, params):
        fv_schemes = params._set_child("fv_schemes", doc="""TODO""")
        for key in self.keys:
            name = underscore(key)
            fv_schemes._set_child(name, attribs=getattr(self, name))

        for key, value in self.other_dict.items():
            name = underscore(key)
            fv_schemes._set_child(name, attribs=value)

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": "dictionary",
                "object": "fvSchemes",
            }
        )

        def set_child(key, name=None):
            if name is None:
                name = key + "Schemes"
            params_key = params.fv_schemes[underscore(key)]
            attribs = {k: params_key[k] for k in params_key._key_attribs}
            attribs = {k: v for k, v in attribs.items() if v is not False}
            tree.set_child(name, attribs)

        for key in self.keys:
            set_child(key)

        for key in self.other_dict:
            set_child(key, name=key)

        return tree

    def add_dict(self, name, data):
        self.other_dict[name] = data
