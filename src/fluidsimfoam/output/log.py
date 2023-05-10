import re

import numpy as np

from fluidsim_core.output.remaining_clock_time import RemainingClockTime


class Log(RemainingClockTime):
    _tag = "log"

    def __init__(self, output):
        self.output = output
        self._path_file = None

    def _load_times(self):
        """Load remaining time data.

        - equation_times
        - remaining_clock_times
        - clock_times_per_timestep
        - equation_time_start
        - full_clock_time

        """
        text = self.text

        eq_times = re.findall(r"\nTime = [\d]+\.[\d]+", text)
        eq_times = np.array([float(word.rsplit(" ", 1)[-1]) for word in eq_times])

        clock_times = re.findall(r"\nExecutionTime = [\d]+\.[\d]+", text)
        clock_times = np.array(
            [float(word.rsplit(" ", 1)[-1]) for word in clock_times]
        )

        data = {"equation_times": eq_times, "equation_time_start": 0.0}

        breakpoint()

        raise NotImplementedError

        return data

    @property
    def path_file(self):
        output = self.output
        if output and not self._path_file:
            path_run = output.path_run
            logfiles = sorted(path_run.glob("log*.txt"))
            if logfiles:
                self._path_file = logfiles[-1]

        return self._path_file.resolve()

    @path_file.setter
    def path_file(self, path_log_file):
        self._path_file = path_log_file

    @property
    def text(self):
        with open(self.path_file) as file:
            return file.read()
