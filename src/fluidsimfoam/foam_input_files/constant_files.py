"""Helper to create constant files"""

from copy import deepcopy

from fluidsimfoam.foam_input_files import (
    FileHelper,
    FoamInputFile,
    _as_py_name,
    _complete_params_dict,
    _update_dict_with_params,
)


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
        _complete_params_dict(params, self.file_name, self.default, self.doc)

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

        params_file = params[_as_py_name(self.file_name)]

        default = deepcopy(self.default)
        _update_dict_with_params(default, params_file)

        tree.init_from_py_objects(
            default,
            dimensions=self.dimensions,
            default_dimension=self.default_dimension,
            comments=self.comments,
        )

        return tree
