"""Invoke tasks to be used from the ``tasks.py`` file in the solvers"""
from pathlib import Path

from invoke import task


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
        for line in file:
            if line.startswith("application  "):
                application = line.split()[-1]
                break

    context.run(application)
