import re

import matplotlib.pyplot as plt
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

        match = re.search(r"start_time = ([\d\.]+)\n", text)
        if match is not None:
            equation_time_start = float(match.groups()[0])
        else:
            equation_time_start = 0.0

        match = re.search(r"end_time = ([\d\.]+)\n", text)
        if match is not None:
            eq_time_end = float(match.groups()[0])
        else:
            raise RuntimeError

        eq_times = re.findall(r"\nTime = ([\d\.]+e?[-\d]*)", text)
        clock_times = re.findall(r"\nExecutionTime = ([\d\.]+)", text)
        eq_times = eq_times[: len(clock_times)]

        eq_times = np.array([float(word) for word in eq_times])
        clock_times = np.array([float(word) for word in clock_times])

        estimation_clock_time_per_time_step = clock_times[-1] / len(clock_times)

        indices_time_step = np.arange(clock_times.size)

        # remove times with same clock time
        clock_times, indices_unique = np.unique(clock_times, return_index=True)
        eq_times = eq_times[indices_unique]
        indices_time_step = indices_time_step[indices_unique]

        # decimate if needed
        precision_clock = 0.01
        step = round(8 * precision_clock / estimation_clock_time_per_time_step)
        if step > 1:
            clock_times = clock_times[::step]
            eq_times = eq_times[::step]
            indices_time_step = indices_time_step[::step]

        delta_eq_times = np.diff(eq_times)

        eq_times = eq_times[:-1]
        remaining_eq_times = eq_time_end - eq_times

        delta_clock_times = np.diff(clock_times)

        remaining_clock_times = (
            remaining_eq_times / delta_eq_times * delta_clock_times
        )

        data = {
            "equation_times": eq_times,
            "remaining_clock_times": remaining_clock_times,
            "clock_times_per_timestep": delta_clock_times
            / np.diff(indices_time_step),
            "equation_time_start": equation_time_start,
            "full_clock_time": clock_times[-1],
            "remaining_eq_times": remaining_eq_times,
            "delta_eq_times": delta_eq_times,
            "delta_clock_times": delta_clock_times,
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
            print("'Time = ' not found in log file")
            return None
        text = text[index + 8 :]
        return float(text.split(None, 1)[0])

    def plot_residuals(self, variable_name=None, tmin=0.0):
        if (
            variable_name is not None
            and variable_name not in self.output.variable_names
        ):
            raise ValueError(
                f"variable_name has to be in {self.output.variable_names}"
            )

        if variable_name is None:
            for key in ("p", "p_rbgh"):
                if key in self.output.variable_names:
                    variable_name = key
                    break

        matches = list(
            re.finditer(
                r"\nTime = (?P<time>[\d\.]+e?-?[\d]*)"
                rf"[\s\S]+?Solving for {variable_name}, "
                r"Initial residual = (?P<initial>[\d\.]+e?-?[\d]*)",
                self.text,
            )
        )

        times = np.empty(len(matches))
        residuals = np.empty_like(times)

        for index, match in enumerate(matches):
            data = match.groupdict()

            times[index] = data["time"]
            residuals[index] = data["initial"]

        fig, ax = plt.subplots()

        residuals = residuals[times > tmin]
        times = times[times > tmin]
        ax.plot(times, residuals)
        ax.set_xlabel("equation time")
        fig.suptitle(f"Initial residuals {variable_name}")
        return times, residuals
