"""Class for the ``sim.output.fields`` object"""

import matplotlib.pyplot as plt

from fluidsimfoam.foam_input_files import read_field_file


class Fields:
    def __init__(self, output):
        self.output = output

    def read_field(self, name, time_approx="last"):
        if time_approx != "last":
            raise NotImplementedError

        path_times = sorted(
            (
                path
                for path in self.output.path_run.glob("*")
                if path.name[0].isdigit()
            ),
            key=lambda p: float(p.name),
        )

        path_dir = path_times[-1]
        field = read_field_file(path_dir / name)
        field.time = float(path_dir.name)
        return field

    def plot_field(self, name, time_approx="last"):
        field = self.read_field(name, time_approx)

        x, y, z = self.output.sim.oper.get_cells_coords()

        fig, ax = plt.subplots()

        ax.plot(y, field.get_array())
