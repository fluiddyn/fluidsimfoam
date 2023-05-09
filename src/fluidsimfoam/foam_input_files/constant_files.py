"""Helper to create constant files"""

from copy import deepcopy

from inflection import underscore

from fluidsimfoam.foam_input_files import FileHelper, FoamInputFile


def _update_dict_with_params(data, params_data):
    for key, value in data.items():
        name = underscore(key)
        if isinstance(value, dict):
            _update_dict_with_params(value, params_data[name])
        else:
            data[key] = params_data[name]


class ConstantFileHelper(FileHelper):
    def __init__(
        self,
        file_name: str,
        default: dict,
        default_dimension: str = False,
        dimensions: dict = None,
        comments: dict = None,
        doc=None,
    ):
        self.file_name = file_name
        self.default = default
        self.default_dimension = default_dimension
        self.dimensions = dimensions
        self.comments = comments
        self.doc = doc

    def complete_params(self, params):
        self._complete_params_dict(params, self.file_name, self.default, self.doc)

    def _complete_params_dict(self, subparams, name, default, doc=None):
        name = underscore(name)
        subsubparams = subparams._set_child(name, doc=doc)

        for key, value in default.items():
            if isinstance(value, dict):
                self._complete_params_dict(subsubparams, key, value)
                continue

            subsubparams._set_attrib(underscore(key), value)

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": "dictionary",
                "location": '"constant"',
                "object": self.file_name,
            },
            comments=self.comments,
        )

        params_file = params[underscore(self.file_name)]

        default = deepcopy(self.default)
        _update_dict_with_params(default, params_file)

        tree.init_from_py_objects(
            default,
            dimensions=self.dimensions,
            default_dimension=self.default_dimension,
            comments=self.comments,
        )

        return tree
