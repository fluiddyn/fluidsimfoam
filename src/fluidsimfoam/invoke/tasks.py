"""Invoke tasks to be used from the ``tasks.py`` file in the solvers"""

import re
from pathlib import Path
from subprocess import Popen
from time import sleep, time

import invoke.context
from invoke import task
from invoke.exceptions import Exit

from fluidsimfoam.foam_input_files import parse

from .context import Context

invoke.tasks.Context = Context


@task
def clean(context):
    context.run("foamCleanTutorials", warn=True)
    for path in Path(".").glob(".data_fluidsim/*_called*"):
        path.unlink()


@task
def block_mesh(context):
    context.run_appl_once("blockMesh")


@task
def surface_feature_extract(context):
    context.run_appl_once("surfaceFeatureExtract")


PATH_DECOMPOSE_PAR_DICT_MESH = None


@task
def snappy_hex_mesh(context):
    context.run_appl_once(
        "snappyHexMesh -overwrite",
        parallel_if_needed=True,
        path_decompose_par_dict=PATH_DECOMPOSE_PAR_DICT_MESH,
    )


@task(pre=[block_mesh, surface_feature_extract, snappy_hex_mesh])
def polymesh(context):
    """Create the polymesh directory"""


@task
def set_fields(context, force=False):
    context.run_appl_once("setFields")


@task
def decompose_par(context):
    context.run_appl_once("decomposePar")


@task(pre=[polymesh, set_fields, decompose_par])
def run(context):
    """Main target to launch a simulation"""
    with open("system/controlDict") as file:
        ctr_dict = file.read()
    ctr_dict = parse(ctr_dict)

    application = ctr_dict.children["application"]
    end_time = ctr_dict["endTime"]
    start_time = ctr_dict["startTime"]

    path_run = Path.cwd()

    if context.parallel:
        # Options '-n' and '-np' are synonymous, but msmpi only supports '-n'
        command = [
            context.mpi_command,
            "-n",
            str(context.nsubdoms),
            application,
            "-parallel",
        ]
    else:
        command = application

    path_log = path_run / f"log_{context.time_as_str}.txt"
    print(f"Starting simulation in \n{path_run}")
    with open(path_log, "w") as file_log:
        file_log.write(f"{start_time = }\n{end_time = }\n")
        file_log.flush()
        print(f"{end_time = }")
        pattern_time = re.compile(r"\nTime = ([\d]+\.[\d]+)")
        t_start = time()
        process = Popen(command, stdout=file_log)
        t_last = time() - 10.0
        while process.poll() is None:
            sleep(0.2)
            t_now = time()
            if t_now - t_last > 2:
                t_last = t_now
                log_size = path_log.stat().st_size
                with open(path_log, "r") as file_log_read:
                    file_log_read.seek(max(0, log_size - 1000))
                    log = file_log_read.read()
                if log:
                    groups = pattern_time.findall(log)
                    if groups:
                        time_simul = float(groups[-1])
                        print(
                            f"eq_time: {time_simul:12.3f} "
                            f"({100 * time_simul/end_time:6.2f} %), "
                            f"clock_time: {t_now - t_start: 12.3f} s"
                        )

    print(f"Simulation done. path_run:\n{path_run}")
    if process.returncode:
        raise Exit(process.returncode)
