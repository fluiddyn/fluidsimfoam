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

    _helper_control_dict = Output._helper_control_dict.new(
        """
        application       chtMultiRegionFoam
        startFrom         latestTime
        startTime         0.001
        stopAt            endTime
        endTime           75
        deltaT            0.001
        writeControl      adjustable
        writeInterval     15
        purgeWrite        0
        writeFormat       ascii
        writePrecision    7
        writeCompression  off
        timeFormat        general
        timePrecision     6
        runTimeModifiable  true
        maxCo             0.3
        maxDi             10.0
        adjustTimeStep    yes
    """
    )

    # remove these lines to get fluidsimfoam default helpers
    _helper_decompose_par_dict = None
    _helper_turbulence_properties = None
    _complete_params_block_mesh_dict = None
