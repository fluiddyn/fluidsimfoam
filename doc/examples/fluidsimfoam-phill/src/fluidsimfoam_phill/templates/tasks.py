from invoke import task

from fluidsimfoam.tasks import (
    block_mesh,
    clean,
    funky_set_fields,
    sets_to_zones,
    topo_set,
)


@task(funky_set_fields)
def run(context):
    with open("system/controlDict") as file:
        for line in file:
            if line.startswith("application  "):
                application = line.split()[-1]
                break

    context.run(application)
