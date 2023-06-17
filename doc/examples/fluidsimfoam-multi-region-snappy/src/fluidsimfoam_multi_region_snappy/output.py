from fluidsimfoam.output import Output


class OutputMultiRegionSnappy(Output):
    name_variables = ["T", "U", "alphat", "epsilon", "k", "p", "p_rgh", "rho"]
    name_system_files = [
        "blockMeshDict",
        "controlDict",
        "decomposeParDict",
        "decomposeParDict.6",
        "fvSchemes",
        "fvSolution",
        "meshQualityDict",
        "snappyHexMeshDict",
        "surfaceFeatureExtractDict",
    ]
    name_constant_files = ["g", "regionProperties"]

    _helper_control_dict = None
    # can be replaced by:
    # _helper_control_dict = Output._helper_control_dict.new()

    # remove these lines to get fluidsimfoam default helpers
    _helper_decompose_par_dict = None
    _helper_turbulence_properties = None
    _complete_params_block_mesh_dict = None
