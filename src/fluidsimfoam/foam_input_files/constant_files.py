"""Helper to create constant files"""

from copy import deepcopy

from fluidsimfoam.foam_input_files import (
    DimensionSet,
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
        doc: str = None,
        cls: str = "dictionary",
        dimension=None,
    ):
        self.file_name = file_name
        self.default = default
        self.default_dimension = default_dimension
        self.dimensions = dimensions
        self.comments = comments
        self.doc = doc
        self.cls = cls
        self.dimension = dimension
        self.name_params_child = _as_py_name(
            self.file_name.replace("Properties", "")
        )

    def complete_params(self, params):
        try:
            constant_params = params["constant"]
        except AttributeError:
            constant_params = params._set_child("constant")

        _complete_params_dict(
            constant_params, self.name_params_child, self.default, self.doc
        )

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": self.cls,
                "location": '"constant"',
                "object": self.file_name,
            },
            comments=self.comments,
        )

        if self.dimension is not None:
            tree.set_child("dimensions", DimensionSet(self.dimension))

        params_file = params.constant[self.name_params_child]

        default = deepcopy(self.default)
        _update_dict_with_params(default, params_file)

        tree.init_from_py_objects(
            default,
            dimensions=self.dimensions,
            default_dimension=self.default_dimension,
            comments=self.comments,
        )

        return tree
