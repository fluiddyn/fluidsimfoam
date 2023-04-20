from pathlib import Path
from subprocess import run


class MakeInvoke:
    def __init__(self, sim=None):
        self.sim = sim

    def exec(self, task_name):
        process = run(["inv", task_name], cwd=self.sim.path_run)
        process.check_returncode()

    def list(self):
        self.exec("--list")
