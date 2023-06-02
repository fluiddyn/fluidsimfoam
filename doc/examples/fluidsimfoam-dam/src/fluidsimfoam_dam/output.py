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
                "nx": 1,
                "ny": 1,
                "nz": 120,
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

        bmd = BlockMeshDict()

        bmd.set_scale(params.block_mesh_dict.scale)

        bmd.add_vertex(0.0, 0.0, 0.0, name="bot_left")
        bmd.add_vertex(x_dam, 0.0, 0.0, name="bot_leftdam")
        bmd.add_vertex(x1_dam, 0.0, 0.0, name="bot_rightdam")
        bmd.add_vertex(lx, 0.0, 0.0, name="bot_right")

        bmd.add_vertex(0.0, height_dam, 0.0, name="topdam_left")
        bmd.add_vertex(x_dam, height_dam, 0.0, name="topdam_leftdam")
        bmd.add_vertex(x1_dam, height_dam, 0.0, name="topdam_rightdam")
        bmd.add_vertex(lx, height_dam, 0.0, name="topdam_right")

        bmd.add_vertex(0.0, ly, 0.0, name="top_left")
        bmd.add_vertex(x_dam, ly, 0.0, name="top_leftdam")
        bmd.add_vertex(x1_dam, ly, 0.0, name="top_rightdam")
        bmd.add_vertex(lx, ly, 0.0, name="top_right")

        for vertex_z0 in bmd.vertices.copy().values():
            vertex_z1 = vertex_z0.copy()
            vertex_z1.z = lz
            vertex_z1.name += "_z1"
            bmd.add_vertex(vertex_z1)

        def add_add_hexblock(vertex_names_z0, nxnynz, name_bloc):
            return bmd.add_hexblock(
                vertex_names_z0 + [name + "_z1" for name in vertex_names_z0],
                nxnynz,
                name_bloc,
            )

        b_bot_left = add_add_hexblock(
            ["bot_left", "bot_leftdam", "topdam_leftdam", "topdam_left"],
            [23, 8, 1],
            "bot_left",
        )

        b_bot_right = add_add_hexblock(
            ["bot_rightdam", "bot_right", "topdam_right", "topdam_rightdam"],
            [19, 8, 1],
            "bot_right",
        )

        b_top_left = add_add_hexblock(
            ["topdam_left", "topdam_leftdam", "top_leftdam", "top_left"],
            [23, 42, 1],
            "top_left",
        )

        b_top_dam = add_add_hexblock(
            ["topdam_leftdam", "topdam_rightdam", "top_rightdam", "top_leftdam"],
            [4, 42, 1],
            "top_dam",
        )

        b_top_right = add_add_hexblock(
            ["topdam_rightdam", "topdam_right", "top_right", "top_rightdam"],
            [19, 42, 1],
            "top_right",
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
