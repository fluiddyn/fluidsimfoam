"""Helper to create fvOptions files

"""
from copy import deepcopy

from fluidsimfoam.foam_input_files import (
    FileHelper,
    FoamInputFile,
    _as_py_name,
    _complete_params_dict,
    _update_dict_with_params,
)


def _make_default_params_dict(default, name_parameters, result):
    for name, value in default.items():
        if isinstance(value, dict):
            name_parameters1 = []
            for full_name in name_parameters:
                if full_name.startswith(name + "/"):
                    name_parameters1.append(full_name[len(name) + 1 :])

            if name_parameters1:
                result[name] = {}
                _make_default_params_dict(value, name_parameters1, result[name])
        else:
            if name in name_parameters:
                result[name] = value

    return result


class FvOption:
    def __init__(self, name, default, parameters=None):
        self.name = name
        self.default = default
        self.parameters = parameters

    def complete_params(self, params_fv_options):
        default_params = {}
        _make_default_params_dict(self.default, self.parameters, default_params)
        _complete_params_dict(params_fv_options, self.name, default_params)

    def complete_tree(self, tree, params_fv_options):
        params_option = params_fv_options[_as_py_name(self.name)]

        default = deepcopy(self.default)
        _update_dict_with_params(default, params_option)

        tree.init_from_py_objects({self.name: default})

        return tree


class FvOptionsHelper(FileHelper):
    def __init__(self):
        self.options = {}

    def add_option(self, name, default, parameters=None):
        self.options[name] = FvOption(name, default, parameters)

    def remove_option(self, name):
        del self.options[name]

    def complete_params(self, params):
        params_fv_options = params._set_child("fv_options", doc="""TODO""")
        for option in self.options.values():
            option.complete_params(params_fv_options)

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": "dictionary",
                "location": '"constant"',
                "object": "fvOptions",
            }
        )
        for option in self.options.values():
            option.complete_tree(tree, params.fv_options)
        return tree
