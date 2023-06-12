"""Class for the ``sim.output.fields`` object"""

import shutil
from numbers import Number
from subprocess import PIPE, run

import matplotlib.pyplot as plt
import numpy as np

from fluidsim_core.output.phys_fields_snek5000 import PhysFields4Snek5000
from fluidsimfoam.foam_input_files import read_field_file


def is_time_name(name):
    return all(c.isdigit() or c == "." for c in name)


import fluidsim_core.hexa_files
from fluidsim_core.hexa_files import HexaField as HexaFieldNek5000
from fluidsim_core.hexa_files import SetOfPhysFieldFiles as _Base


class HexaField(HexaFieldNek5000):
    pass


fluidsim_core.hexa_files.HexaField = HexaField


class SetOfPhysFieldFiles(_Base):
    def get_saved_times(self):
        if self.sim.params.parallel.nsubdoms > 1:
            str_glob = "processor0/*"
        else:
            str_glob = "*"

        return sorted(
            float(path.name)
            for path in self.output.path_run.glob(str_glob)
            if is_time_name(path.name)
        )

    def update_times(self):
        if self.output.sim.params.parallel.nsubdoms > 1:
            str_glob = "processor0/*"
        else:
            str_glob = "*"

        self.path_files = sorted(
            path
            for path in self.output.path_run.glob(str_glob)
            if is_time_name(path.name)
        )

        self.times = np.array([float(path.name) for path in self.path_files])

    def _get_glob_pattern(self):
        return None

    def get_key_field_to_plot(self, key_prefered=None):
        if key_prefered is None:
            variables = self.output.name_variables
            if "T" in variables:
                return "temperature"
            else:
                raise NotImplementedError()
        else:
            return key_prefered


class Fields(PhysFields4Snek5000):
    _cls_set_of_files = SetOfPhysFieldFiles

    def __init__(self, output):
        self.output = output
        self.sim = output.sim
        super().__init__(output)
        del self.plot_hexa_stat, self.read_hexadata_stat

    def get_saved_times(self):
        if self.sim.params.parallel.nsubdoms > 1:
            str_glob = "processor0/*"
        else:
            str_glob = "*"

        return sorted(
            float(path.name)
            for path in self.output.path_run.glob(str_glob)
            if is_time_name(path.name)
        )

    def get_path_dir_time(self, time_approx="last", dirname=None):
        if time_approx != "last":
            raise NotImplementedError

        if dirname is None:
            str_glob = "*"
        else:
            str_glob = dirname + "/*"

        path_times = sorted(
            (
                path
                for path in self.output.path_run.glob(str_glob)
                if path.name[0].isdigit()
            ),
            key=lambda p: float(p.name),
        )
        path_dir = path_times[-1]
        last_time = float(path_dir.name)
        return path_dir, last_time

    def read_field(self, name, time_approx="last"):
        if time_approx != "last":
            raise NotImplementedError

        path_dir, last_time = self.get_path_dir_time(time_approx)

        if self.sim.params.parallel.nsubdoms > 1:
            _, last_time_proc0 = self.get_path_dir_time(
                time_approx, dirname="processor0"
            )
            if last_time_proc0 != last_time:
                self.reconstruct_par(fields=[name], time=last_time_proc0)
            path_dir, last_time = self.get_path_dir_time(time_approx)
            assert last_time == last_time_proc0

        field = read_field_file(path_dir / name)
        field.time = float(path_dir.name)
        return field

    def reconstruct_par(self, fields=None, latest_time=None, time=None):
        path_command = shutil.which("reconstructPar")

        if path_command is None:
            raise RuntimeError("OpenFOAM not available")

        command = ["reconstructPar"]

        if fields is not None:
            command.extend(["-fields", f"({' '.join(fields)})"])

        if latest_time is not None and time is not None:
            raise ValueError

        if latest_time is not None:
            command.append("-latestTime")

        if time is not None:
            if isinstance(time, Number):
                time = str(time)

            command.extend(["-time", time])

        run(command, cwd=self.sim.path_run, stdout=PIPE)

    def plot_field(self, name, time_approx="last"):
        field = self.read_field(name, time_approx)

        x, y, z = self.output.sim.oper.get_cells_coords()

        fig, ax = plt.subplots()

        ax.plot(y, field.get_array())
