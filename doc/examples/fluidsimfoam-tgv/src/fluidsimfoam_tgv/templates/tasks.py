from pathlib import Path

from invoke import task


@task
def clean(command):
    return command.run("foamCleanTutorials")


@task
def block_mesh(command):
    here = Path(__file__).absolute().parent
    if not (here / "system/blockMeshDict").exists():
        print("blockMeshDict not found!")

    elif not (here / "constant/polyMesh").is_dir():
        return command.run("blockMesh")


@task(block_mesh)
def run(command):
    return command.run("icoFoam")
