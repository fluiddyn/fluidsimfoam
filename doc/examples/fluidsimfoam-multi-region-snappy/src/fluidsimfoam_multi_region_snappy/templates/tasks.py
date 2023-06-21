import subprocess
from pathlib import Path

import fluidsimfoam.tasks
from fluidsimfoam.tasks import (
    block_mesh,
    clean,
    polymesh,
    run,
    snappy_hex_mesh,
    surface_feature_extract,
    task,
)

path_decomp_dict = "system/decomposeParDict.mesh"

fluidsimfoam.tasks.PATH_DECOMPOSE_PAR_DICT_MESH = path_decomp_dict


@task
def split_mesh_regions(ctx):
    ctx.run_appl_once(
        "splitMeshRegions -cellZones -overwrite",
        check_dict_file=False,
        parallel_if_needed=True,
        path_decompose_par_dict=path_decomp_dict,
    )


@task
def decompose_par(context):
    command = "decomposePar"
    if context.parallel:
        command += f" -decomposeParDict {path_decomp_dict}"
    context.run_appl_once(command)


polymesh.pre = [
    block_mesh,
    surface_feature_extract,
    decompose_par,
    snappy_hex_mesh,
    split_mesh_regions,
]


@task(polymesh)
def init_run(ctx):
    process = subprocess.run(
        "foamListRegions solid".split(), capture_output=True, text=True
    )
    regions_solid = process.stdout.split()

    # Remove fluid fields from solid regions (important for post-processing)
    for region in regions_solid:
        bases = [Path("0")]
        bases.extend(Path(".").glob("processor*/0"))
        for base in bases:
            for name in ["nut", "alphat", "epsilon", "k", "U", "p_rgh"]:
                (base / region / name).unlink(missing_ok=True)

    process = subprocess.run("foamListRegions", capture_output=True, text=True)
    regions = process.stdout.split()

    for region in regions:
        ctx.run_appl_once(
            f"changeDictionary -region {region}",
            suffix_log=region,
            check_dict_file=False,
        )


run.pre = [polymesh, init_run]
