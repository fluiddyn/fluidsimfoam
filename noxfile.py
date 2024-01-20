import os
from pathlib import Path
from shutil import rmtree

import nox

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
nox.options.reuse_existing_virtualenvs = 1


@nox.session
def test(session):
    session.run_always(
        "pdm", "sync", "-G", "test", "-G", "pyvista", "--clean", external=True
    )
    command = (
        "pdm run pytest tests doc/examples --cov --cov-report term --cov-report xml"
    )
    session.run(*command.split(), external=True)


@nox.session
def doc(session):
    session.run_always("pdm", "sync", "-G", "doc", "--clean", external=True)
    session.chdir("doc")
    session.run("make", "cleanall", external=True)
    session.run("make", external=True)
