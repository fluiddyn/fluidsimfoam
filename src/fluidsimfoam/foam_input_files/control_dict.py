"""Helper to create controlDict files"""

from inflection import underscore

from fluidsimfoam.foam_input_files import (
    DEFAULT_HEADER,
    FileHelper,
    FoamInputFile,
    _complete_params_dict,
)
from fluidsimfoam.foam_input_files.util import as_dict

# taken from https://doc.cfd.direct/openfoam/user-guide-v6/controldict
DEFAULT_CONTROL_DICT = dict(
    application="icoFoam",
    startFrom="startTime",
    startTime=0,
    stopAt="endTime",
    endTime=0.5,
    deltaT=0.005,
    writeControl="timeStep",
    writeInterval=20,
    purgeWrite=0,
    writeFormat="ascii",
    writePrecision=6,
    writeCompression="off",
    timeFormat="general",
    timePrecision=6,
    runTimeModifiable="true",
)


class Function:
    def __init__(self, type, libs, entries=None):
        self.type = type
        self.libs = libs
        self.entries = entries

    def make_dict(self):
        data = {"type": self.type, "libs": self.libs}
        if self.entries is not None:
            data.update(as_dict(self.entries, filter_comments=False))
        return data


class ControlDictHelper(FileHelper):
    def __init__(self, default=None):
        self.default_control_dict_params = DEFAULT_CONTROL_DICT.copy()
        if default is not None:
            self.default_control_dict_params.update(as_dict(default))

        self.functions = {}
        self.functions_included = {}

    def complete_params(self, params):
        _complete_params_dict(
            params, "control_dict", self.default_control_dict_params
        )

    def make_tree(self, params):
        tree = FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "location": '"system"',
                "object": "controlDict",
            },
            children={
                key: params.control_dict[underscore(key)]
                for key in self.default_control_dict_params.keys()
            },
            header=DEFAULT_HEADER,
        )

        data = {}
        for name, kind in self.functions_included.items():
            if kind is None:
                kind = "#includeFunc"
            data[f"{kind} {name}"] = None
        for name, function in self.functions.items():
            data[name] = function.make_dict()
        if data:
            tree.init_from_py_objects({"functions": data})

        return tree

    def new(self, default=None):
        return type(self)(default)

    def add_function(self, key, type, libs, entries=None):
        self.functions[key] = Function(type, libs, entries)

    def include_function(self, name, kind=None):
        self.functions_included[name] = kind

    def include_functions(self, names, kind=None):
        for name in names:
            self.include_function(name, kind)
