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

        match = re.search(r"start_time = [\d\.]+\n", text)
        if match is not None:
            equation_time_start = float(match.group().rsplit(None, 1)[-1])
        else:
            equation_time_start = 0.0

        match = re.search(r"end_time = [\d\.]+\n", text)
        if match is not None:
            eq_time_end = float(match.group().rsplit(None, 1)[-1])
        else:
            raise RuntimeError

        eq_times = re.findall(r"\nTime = [\d\.]+", text)
        eq_times = np.array([float(word.rsplit(" ", 1)[-1]) for word in eq_times])

        clock_times = re.findall(r"\nExecutionTime = [\d\.]+", text)
        clock_times = np.array(
            [float(word.rsplit(" ", 1)[-1]) for word in clock_times]
        )

        remaining_eq_times = eq_time_end - eq_times

        delta_clock_times = np.diff(clock_times)
        delta_eq_times = np.diff(eq_times)

        remaining_clock_times = (
            remaining_eq_times[:-1] / delta_eq_times * delta_clock_times
        )

        data = {
            "equation_times": eq_times[:-1],
            "remaining_clock_times": remaining_clock_times,
            "clock_times_per_timestep": delta_clock_times,
            "equation_time_start": equation_time_start,
            "full_clock_time": clock_times[-1],
        }

        return data

    @property
    def path_file(self):
        output = self.output
        if output and not self._path_file:
            path_run = output.path_run
            logfiles = sorted(path_run.glob("log*.txt"))
            if logfiles:
                self._path_file = logfiles[-1]
            else:
                print("No log file found")
                return None

        return self._path_file.resolve()

    @path_file.setter
    def path_file(self, path_log_file):
        self._path_file = path_log_file

    @property
    def text(self):
        if self.path_file is None:
            return None

        with open(self.path_file) as file:
            return file.read()

    @property
    def time_last(self):
        if self.text is None:
            return None
        text = self.text[-1000:]
        index = text.rfind("\nTime = ")
        if index == -1:
            print("'Time = ' not found")
            return None
        text = text[index + 8 :]
        return float(text.split(None, 1)[0])
