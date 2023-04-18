from pathlib import Path

from invoke import task


@task
def clean(context):
    context.run("foamCleanTutorials", warn=True)


@task
def block_mesh(context):
    here = Path(__file__).absolute().parent
    if not (here / "system/blockMeshDict").exists():
        print("blockMeshDict not found!")

    elif not (here / "constant/polyMesh").is_dir():
        context.run("blockMesh")


@task(block_mesh)
def run(context):
    context.run("icoFoam")
