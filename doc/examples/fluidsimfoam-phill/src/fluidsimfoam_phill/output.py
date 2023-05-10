from textwrap import dedent

from inflection import underscore

from fluidsimfoam.foam_input_files import DEFAULT_HEADER, Dict, FoamInputFile
from fluidsimfoam.foam_input_files.blockmesh import (
    BlockMeshDict,
    Point,
    SimpleGrading,
    Vertex,
)
from fluidsimfoam.output import Output

code_control_dict_functions = dedent(
    """
    adjustTimeStep   yes;
    libs            (atmosphericModels);

    functions
    {
        fieldAverage1
        {
            type            fieldAverage;
            libs            (fieldFunctionObjects);
            writeControl    writeTime;

            fields
            (
                U
                {
                    mean        on;
                    prime2Mean  off;
                    base        time;
                }
            );
        }
    }

"""
)

_attribs_transport_prop = {
    "transportModel": "Newtonian",
    "nu            nu  [0 2 -1 0 0 0 0]": 0.0001,
    "Pr            Pr [0 0 0 0 0 0 0]": 10,
    "beta": 3e-03,
    "TRef": 300,
    "Prt": 0.85,
}


class OutputPHill(Output):
    """Output for the phill solver"""

    variable_names = ["U", "rhok", "p_rgh", "T", "alphat"]
    system_files_names = Output.system_files_names + [
        "blockMeshDict",
        "topoSetDict",
        "funkySetFieldsDict",
    ]
    constant_files_names = Output.constant_files_names + [
        "g",
        "fvOptions",
        "MRFProperties",
    ]

    # @classmethod
    # def _set_info_solver_classes(cls, classes):
    #     """Set the the classes for info_solver.classes.Output"""
    #     super()._set_info_solver_classes(classes)

    @classmethod
    def _complete_params_control_dict(cls, params):
        super()._complete_params_control_dict(params)

        default = {
            "application": "buoyantBoussinesqPimpleFoam",
            "startFrom": "startTime",
            "endTime": 60,
            "deltaT": 0.05,
            "writeControl": "adjustableRunTime",
            "writeInterval": 1,
            "writeFormat": "ascii",
            "writeCompression": "off",
            "runTimeModifiable": "yes",
            "adjustTimeStep": "yes",
            "maxCo": 0.6,
            "maxAlphaCo": 0.6,
            "maxDeltaT": 1,
        }
        for key, value in default.items():
            try:
                params.control_dict[underscore(key)] = value
            except AttributeError:
                # TODO: Fix adding keys which are not in DEFAULT_CONTROL_DICT
                params.control_dict._set_attribs({underscore(key): value})

    def make_code_control_dict(self, params):
        code = super().make_code_control_dict(params)
        return code + code_control_dict_functions

    @classmethod
    def _complete_params_transport_properties(cls, params):
        params._set_child(
            "transport_properties",
            attribs=_attribs_transport_prop,
            doc="""TODO""",
        )

    def make_tree_transport_properties(self, params):
        return FoamInputFile(
            info={
                "version": "2.0",
                "format": "ascii",
                "class": "dictionary",
                "object": "transportProperties",
            },
            children={
                key: params.transport_properties[key]
                for key in _attribs_transport_prop.keys()
            },
            header=DEFAULT_HEADER,
        )

    @classmethod
    def _complete_params_block_mesh_dict(cls, params):
        super()._complete_params_block_mesh_dict(params)
        default = {"nx": 20, "ny": 30, "nz": 1}
        default.update({"lx": 1.0, "ly": 1.0, "lz": 0.01, "scale": 1})
        for key, value in default.items():
            params.block_mesh_dict[key] = value

    def make_code_block_mesh_dict(self, params):
        nx = params.block_mesh_dict.nx
        ny = params.block_mesh_dict.ny
        nz = params.block_mesh_dict.nz

        lx = params.block_mesh_dict.lx
        ly = params.block_mesh_dict.ly
        lz = params.block_mesh_dict.lz

        bmd = BlockMeshDict()
        bmd.set_scale(params.block_mesh_dict.scale)

        basevs = [
            Vertex(0, ly, 0, "v0"),
            Vertex(0.5, ly, 0, "v1"),
            Vertex(1.5, ly, 0, "v2"),
            Vertex(6, ly, 0, "v3"),
            Vertex(6, ly, lz, "v4"),
            Vertex(1.5, ly, lz, "v5"),
            Vertex(0.5, ly, lz, "v6"),
            Vertex(0, ly, lz, "v7"),
        ]

        for v in basevs:
            bmd.add_vertex(v.x, 0, v.z, v.name + "-0")
            bmd.add_vertex(v.x, v.y, v.z, v.name + "+y")

        b0 = bmd.add_hexblock(
            ("v0-0", "v1-0", "v1+y", "v0+y", "v7-0", "v6-0", "v6+y", "v7+y"),
            (nx, ny, nz),
            "b0",
            SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
        )

        b1 = bmd.add_hexblock(
            ("v1-0", "v2-0", "v2+y", "v1+y", "v6-0", "v5-0", "v5+y", "v6+y"),
            (nx, ny, nz),
            "b1",
            SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
        )

        b2 = bmd.add_hexblock(
            ("v2-0", "v3-0", "v3+y", "v2+y", "v5-0", "v4-0", "v4+y", "v5+y"),
            (225, ny, nz),
            "b2",
            SimpleGrading(1, [[0.1, 0.25, 41.9], [0.9, 0.75, 1]], 1),
        )

        bmd.add_splineedge(
            ["v1-0", "v2-0"],
            "spline0",
            [
                Point(0.6, 0.0124, 0),
                Point(0.7, 0.0395, 0),
                Point(0.8, 0.0724, 0),
                Point(0.9, 0.132, 0),
                Point(1, 0.172, 0),
                Point(1.1, 0.132, 0),
                Point(1.2, 0.0724, 0),
                Point(1.3, 0.0395, 0),
                Point(1.4, 0.0124, 0),
            ],
        )
        bmd.add_splineedge(
            ["v6-0", "v5-0"],
            "spline1",
            [
                Point(0.6, 0.0124, lz),
                Point(0.7, 0.0395, lz),
                Point(0.8, 0.0724, lz),
                Point(0.9, 0.132, lz),
                Point(1, 0.172, lz),
                Point(1.1, 0.132, lz),
                Point(1.2, 0.0724, lz),
                Point(1.3, 0.0395, lz),
                Point(1.4, 0.0124, lz),
            ],
        )

        bmd.add_boundary(
            "wall", "top", [b0.face("n"), b1.face("n"), b2.face("n")]
        )
        bmd.add_boundary(
            "wall", "bottom", [b0.face("s"), b1.face("s"), b2.face("s")]
        )
        bmd.add_cyclic_boundaries("outlet", "inlet", b2.face("e"), b0.face("w"))
        # bmd.add_boundary("inlet", "inlet", [b2.face("e")])
        # bmd.add_boundary("outlet", "outlet", [b0.face("w")])
        bmd.add_boundary(
            "empty",
            "frontandbackplanes",
            [
                b0.face("b"),
                b1.face("b"),
                b2.face("b"),
                b0.face("t"),
                b1.face("t"),
                b2.face("t"),
            ],
        )

        return bmd.format()
