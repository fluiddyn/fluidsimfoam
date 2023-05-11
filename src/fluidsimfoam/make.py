"""Base class for the ``sim.make`` object

"""


from subprocess import PIPE, Popen, run


class MakeInvoke:
    def __init__(self, sim=None):
        self.sim = sim

    def exec(self, task_name, stdout=None):
        process = run(["inv", task_name], cwd=self.sim.path_run, stdout=stdout)
        process.check_returncode()

    def list(self):
        self.exec("--list")

    def exec_async(self, task_name):
        return Popen(["inv", task_name], cwd=self.sim.path_run, stdout=PIPE)
