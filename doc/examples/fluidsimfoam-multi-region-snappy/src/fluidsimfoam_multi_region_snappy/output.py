from fluidsimfoam.output import Output


class OutputMultiRegionSnappy(Output):
    name_variables = ["T", "U", "alphat", "epsilon", "k", "p", "p_rgh", "rho"]
    name_system_files = [
        "blockMeshDict",
        "bottomAir/changeDictionaryDict",
        "bottomAir/fvSchemes",
        "bottomAir/fvSolution",
        "controlDict",
        "decomposeParDict",
        "decomposeParDict.6",
        "fvSchemes",
        "fvSolution",
        "heater/changeDictionaryDict",
        "heater/fvSchemes",
        "heater/fvSolution",
        "leftSolid/changeDictionaryDict",
        "leftSolid/fvSolution",
        "meshQualityDict",
        "rightSolid/changeDictionaryDict",
        "rightSolid/fvSolution",
        "snappyHexMeshDict",
        "surfaceFeatureExtractDict",
        "topAir/changeDictionaryDict",
        "topAir/fvSolution",
    ]
    name_constant_files = [
        "bottomAir/radiationProperties",
        "bottomAir/thermophysicalProperties",
        "bottomAir/turbulenceProperties",
        "g",
        "heater/radiationProperties",
        "heater/thermophysicalProperties",
        "regionProperties",
    ]
    internal_symlinks = {
        "system/leftSolid/fvSchemes": "../heater/fvSchemes",
        "system/leftSolid/decomposeParDict": "../heater/decomposeParDict",
        "system/rightSolid/fvSchemes": "../heater/fvSchemes",
        "system/rightSolid/decomposeParDict": "../heater/decomposeParDict",
        "system/topAir/fvSchemes": "../bottomAir/fvSchemes",
        "system/topAir/decomposeParDict": "../bottomAir/decomposeParDict",
        "system/bottomAir/decomposeParDict": "../decomposeParDict",
        "system/heater/decomposeParDict": "../decomposeParDict",
        "constant/leftSolid/thermophysicalProperties": "../heater/thermophysicalProperties",
        "constant/leftSolid/radiationProperties": "../heater/radiationProperties",
        "constant/rightSolid/thermophysicalProperties": "../heater/thermophysicalProperties",
        "constant/rightSolid/radiationProperties": "../heater/radiationProperties",
        "constant/topAir/turbulenceProperties": "../bottomAir/turbulenceProperties",
        "constant/topAir/thermophysicalProperties": "../bottomAir/thermophysicalProperties",
        "constant/topAir/radiationProperties": "../bottomAir/radiationProperties",
    }

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
    _helper_turbulence_properties = None
    _complete_params_block_mesh_dict = None

    @classmethod
    def _complete_params_with_default(cls, params, info_solver):
        super()._complete_params_with_default(params, info_solver)
        params.resources = (
            "package-data(fluidsimfoam_multi_region_snappy.templates)/geom.stl.gz"
            " -> constant/triSurface/geom.stl.gz"
        )

    _helper_decompose_par_dict = Output._helper_decompose_par_dict.new()
    _helper_decompose_par_dict.add_region(
        "heater",
        {
            "numberOfSubdomains": 1,
            "method": "simple",
            "coeffs": {"n": [1, 1, 1]},
        },
    )
