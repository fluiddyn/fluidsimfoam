from fluidsimfoam.foam_input_files import BlockMeshDict, ConstantFileHelper
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

    _helper_control_dict = Output._helper_control_dict.new(
        """
        application     interFoam
        endTime         1
        deltaT          0.001
        writeControl    adjustable
        writeInterval   0.05
        adjustTimeStep  true
        maxCo           1
        maxAlphaCo      1
        maxDeltaT       1
    """
    )

    _helper_control_dict.include_function('"sampling"', kind="#sinclude")

    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "phases": ["water", "air"],
            "water": {
                "transportModel": "Newtonian",
                "nu": 1e-06,
                "rho": 1000,
            },
            "air": {
                "transportModel": "Newtonian",
                "nu": 1.48e-05,
                "rho": 1,
            },
            "sigma": 0.07,
        },
    )

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        params.block_mesh_dict._update_attribs(
            {
                "nx": 46,
                "ny": 50,
                "nz": 1,
                "scale": 0.146,
                "lx": 4.0,
                "ly": 4.0,
                "lz": 0.1,
                "x_dam": 2.0,
                "width_dam": 0.16438,
                "height_dam": 0.32873,
            }
        )

    def _make_code_block_mesh_dict(self, params):
        p_bmd = params.block_mesh_dict
        nx = p_bmd.nx
        ny = p_bmd.ny
        nz = p_bmd.nz

        lx = p_bmd.lx
        ly = p_bmd.ly
        lz = p_bmd.lz

        x_dam = p_bmd.x_dam
        width_dam = p_bmd.width_dam
        x1_dam = x_dam + width_dam
        height_dam = p_bmd.height_dam

        dx = lx / nx
        nx_left = int(x_dam / dx)
        nx_dam = max(4, int(height_dam / dx))
        nx_right = nx - nx_dam - nx_left

        dy = ly / ny
        ny_bot = max(8, int(height_dam / dy))
        ny_top = ny - ny_bot

        bmd = BlockMeshDict()

        bmd.set_scale(params.block_mesh_dict.scale)

        for x_y_z_name in (
            # bottom
            (0, 0, 0, "left_bot"),
            (x_dam, 0, 0, "leftdam_bot"),
            (x1_dam, 0, 0, "rightdam_bot"),
            (lx, 0, 0, "right_bot"),
            # top dam
            (0, height_dam, 0, "left_topdam"),
            (x_dam, height_dam, 0, "leftdam_topdam"),
            (x1_dam, height_dam, 0, "rightdam_topdam"),
            (lx, height_dam, 0, "right_topdam"),
            # top
            (0, ly, 0, "left_top"),
            (x_dam, ly, 0, "leftdam_top"),
            (x1_dam, ly, 0, "rightdam_top"),
            (lx, ly, 0, "right_top"),
        ):
            bmd.add_vertex(*x_y_z_name)

        bmd.replicate_vertices_further_z(lz)

        b_bot_left = bmd.add_hexblock_from_2d(
            ["left_bot", "leftdam_bot", "leftdam_topdam", "left_topdam"],
            [nx_left, ny_bot, nz],
            "left_bot",
        )

        b_bot_right = bmd.add_hexblock_from_2d(
            ["rightdam_bot", "right_bot", "right_topdam", "rightdam_topdam"],
            [nx_right, ny_bot, nz],
            "right_bot",
        )

        b_top_left = bmd.add_hexblock_from_2d(
            ["left_topdam", "leftdam_topdam", "leftdam_top", "left_top"],
            [nx_left, ny_top, nz],
            "left_top",
        )

        b_top_dam = bmd.add_hexblock_from_2d(
            ["leftdam_topdam", "rightdam_topdam", "rightdam_top", "leftdam_top"],
            [nx_dam, ny_top, nz],
            "top_dam",
        )

        b_top_right = bmd.add_hexblock_from_2d(
            ["rightdam_topdam", "right_topdam", "right_top", "rightdam_top"],
            [nx_right, ny_top, nz],
            "right_top",
        )

        bmd.add_boundary(
            "wall", "leftWall", [b_bot_left.face("xm"), b_top_left.face("xm")]
        )

        bmd.add_boundary(
            "wall", "rightWall", [b_bot_right.face("xp"), b_top_right.face("xp")]
        )

        bmd.add_boundary(
            "wall",
            "lowerWall",
            b_bot_left.faces("ym", "xp")
            + b_top_dam.faces("ym")
            + b_bot_right.faces("xm", "ym"),
        )

        bmd.add_boundary(
            "patch",
            "atmosphere",
            [
                b_top_left.face("yp"),
                b_top_dam.face("yp"),
                b_top_right.face("yp"),
            ],
        )

        return bmd.format(sort_vortices="as_added")
