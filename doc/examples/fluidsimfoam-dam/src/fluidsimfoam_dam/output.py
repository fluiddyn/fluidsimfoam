from fluidsimfoam.output import Output


class OutputDam(Output):
    name_variables = ["U", "alpha.water", "p_rgh"]
    name_system_files = [
        "blockMeshDict",
        "controlDict",
        "decomposeParDict",
        "fvSchemes",
        "fvSolution",
        "sampling",
        "setFieldsDict",
    ]
    name_constant_files = ["g", "transportProperties", "turbulenceProperties"]

    _helper_control_dict = None
    # can be replaced by:
    # _helper_control_dict = Output._helper_control_dict.new()
