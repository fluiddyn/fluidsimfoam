"""Invoke tasks to be used from the ``tasks.py`` file in the solvers"""

import re
from pathlib import Path
from subprocess import Popen
from time import sleep, time

from invoke import task

from fluiddyn.util import time_as_str
from fluidsimfoam.foam_input_files import parse


@task
def clean(context):
    context.run("foamCleanTutorials", warn=True)


@task
def block_mesh(context):
    if (
        Path("system/blockMeshDict").exists()
        and not Path("constant/polyMesh").is_dir()
    ):
        context.run("blockMesh")


@task(block_mesh)
def polymesh(context):
    """Create the polymesh directory"""


@task
def set_fields(context, force=False):
    if Path("system/setFieldsDict").exists():
        path_setFields_called = Path(".data_fluidsim/setFields_called")
        path_setFields_called.parent.mkdir(exist_ok=True)
        if force or not path_setFields_called.exists():
            path_setFields_called.touch()
            context.run("setFields")


@task(polymesh, set_fields)
def run(context):
    """Main target to launch a simulation"""
    with open("system/controlDict") as file:
        ctr_dict = file.read()
    ctr_dict = parse(ctr_dict)

    application = ctr_dict.children["application"]
    end_time = ctr_dict["endTime"]
    start_time = ctr_dict["startTime"]

    path_run = Path.cwd()

    path_decompose_par_dict = path_run / "system/decomposeParDict"
    parallel = path_decompose_par_dict.exists()
    if parallel:
        context.run("decomposePar")
        nsubdoms = None
        with open(path_decompose_par_dict) as file:
            for line in file:
                if "numberOfSubdomains" in line:
                    line = line.strip().removesuffix(";")
                    nsubdoms = int(line.split()[-1])
                    break
        if nsubdoms is None:
            raise RuntimeError(f"Bad decomposeParDict {path_decompose_par_dict}")
        command = ["mpirun", "-np", str(nsubdoms), application, "-parallel"]
    else:
        command = application

    path_log = path_run / f"log_{time_as_str()}.txt"
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
