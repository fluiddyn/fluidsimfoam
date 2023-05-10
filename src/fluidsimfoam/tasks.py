"""Invoke tasks to be used from the ``tasks.py`` file in the solvers"""
import io
import re
from pathlib import Path
from time import sleep, time

from invoke import task

from fluiddyn.io.tee import MultiFile
from fluiddyn.util import time_as_str
from fluidsimfoam.foam_input_files import parse


@task
def clean(context):
    context.run("foamCleanTutorials", warn=True)


@task
def block_mesh(context):
    if not Path("system/blockMeshDict").exists():
        print("blockMeshDict not found!")

    elif not Path("constant/polyMesh").is_dir():
        context.run("blockMesh")


@task(block_mesh)
def polymesh(context):
    pass


@task(polymesh)
def run(context):
    with open("system/controlDict") as file:
        ctr_dict = file.read()
    ctr_dict = parse(ctr_dict)

    application = ctr_dict.children["application"]
    end_time = ctr_dict["endTime"]

    path_run = Path.cwd()
    print(f"Starting simulation in \n{path_run}")
    with open(f"log_{time_as_str()}.txt", "w") as file_log:
        str_io = io.StringIO()
        out_stream = MultiFile([str_io, file_log])

        pattern_time = re.compile(r"\nTime = [\d]+\.[\d]+")

        with context.run(
            application, asynchronous=True, out_stream=out_stream
        ) as promise:
            t_last = time() - 2.0
            while not promise.runner.process_is_finished:
                if time() - t_last > 1:
                    log = str_io.getvalue()
                    if log:
                        groups = pattern_time.findall(log)
                        if groups:
                            time_simul = float(groups[-1].rsplit(None, 1)[1])
                            print(
                                f"time / end_time: {time_simul:12.3f} / {end_time}"
                            )
                            str_io = io.StringIO()
                            out_stream._files[0] = str_io
                sleep(0.1)

    print(f"Simulation done. path_run:\n{path_run}")
