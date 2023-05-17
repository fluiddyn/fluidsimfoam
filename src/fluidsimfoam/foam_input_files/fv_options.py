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


def get_selection_mode(cell_zone, cell_set, points):
    is_not_none = [var is not None for var in (cell_zone, cell_set, points)]
    nb_var_not_none = sum(is_not_none)

    if nb_var_not_none == 0:
        return "all"
    elif nb_var_not_none > 1:
        raise ValueError

    if cell_zone is not None:
        selection_mode = "cellZone"
    elif cell_set is not None:
        selection_mode = "cellSet"
    elif points is not None:
        selection_mode = "points"
    else:
        raise RuntimeError

    return selection_mode


class FvOption:
    def __init__(
        self,
        type,
        name,
        active=True,
        cell_zone=None,
        cell_set=None,
        points=None,
        coeffs=None,
        parameters=None,
        default=None,
    ):
        self.type = type
        self.name = name

        if parameters is None:
            parameters = set()
        else:
            parameters = set(parameters)

        if default is None:
            default = {}

        default["type"] = type
        self.active = active

        self.coeffs = coeffs
        if coeffs is not None:
            if "coeffs" in default:
                raise ValueError
            default["coeffs"] = coeffs
            self.name_coeffs_key = type + "Coeffs"

        self.cell_zone = cell_zone
        self.cell_set = cell_set
        self.points = points

        self.default = default
        self.parameters = parameters

    def complete_params(self, params_fv_options):
        default_params = {
            "active": self.active,
            "selection": {
                "cell_zone": self.cell_zone,
                "cell_set": self.cell_set,
                "points": self.points,
            },
        }
        _make_default_params_dict(self.default, self.parameters, default_params)
        if "__coeffs__" in default_params:
            default_params["coeffs"] = default_params.pop("__coeffs__")
        _complete_params_dict(params_fv_options, self.name, default_params)

    def get_dict_for_tree(self, params_fv_options):
        params_option = params_fv_options[_as_py_name(self.name)]

        dict_for_tree = {"type": self.type, "active": None}

        select = params_option.selection
        dict_for_tree["selectionMode"] = get_selection_mode(
            select.cell_zone, select.cell_set, select.points
        )

        for key in ("cellZone", "cellSet", "points"):
            key_as_py_name = _as_py_name(key)
            if select[key_as_py_name] is not None:
                dict_for_tree[key] = select[key_as_py_name]

        dict_for_tree.update(self.default)

        _update_dict_with_params(dict_for_tree, params_option)

        active = params_option.active
        if isinstance(active, bool):
            active = ("no", "yes")[int(active)]
        dict_for_tree["active"] = active
        if self.coeffs is not None:
            dict_for_tree[self.name_coeffs_key] = dict_for_tree.pop("coeffs")
        return dict_for_tree


class FvOptionsHelper(FileHelper):
    def __init__(self):
        self.options = {}

    def add_option(
        self,
        type,
        name=None,
        active=True,
        cell_zone=None,
        cell_set=None,
        points=None,
        coeffs=None,
        parameters=None,
        default=None,
    ):
        if name is None:
            name = type

        self.options[name] = FvOption(
            type,
            name,
            active,
            cell_zone,
            cell_set,
            points,
            coeffs,
            parameters,
            default,
        )

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
                "location": '"system"',
                "object": "fvOptions",
            }
        )
        for name, option in self.options.items():
            tree.init_from_py_objects(
                {name: option.get_dict_for_tree(params.fv_options)}
            )
        return tree
