"""Class for the ``sim.output.fields`` object"""

import shutil
from numbers import Number
from subprocess import PIPE, run

import matplotlib.pyplot as plt
import numpy as np

try:
    import pyvista
except ImportError:
    pyvista_importable = False
else:
    pyvista_importable = True

from fluidsimfoam.foam_input_files import read_field_file


def is_time_name(name):
    return all(c.isdigit() or c == "." for c in name)


class Fields:
    def __init__(self, output):
        self.output = output
        self.sim = output.sim

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

    def _init_pyvista(self, time=None):
        path_dir = self.output.sim.path_run
        casename = f".{self.output.sim.info_solver.short_name}.foam"
        with open(casename, "w") as my_file:
            my_file.write("")
        filename = f"{path_dir}/{casename}"
        reader = pyvista.POpenFOAMReader(filename)
        if time is not None:
            if time in reader.time_values:
                reader.set_active_time_value(time)
            else:
                print(f"Time ({time}) is Not available!")

        return reader.read(), reader.time_values

    def plot_boundary(
        self,
        name="",
        show_edges=True,
        lighting=True,
        camera_position=None,
        color="w",
        whole_mesh_opacity=0,
        add_legend=False,
        **kwargs,
    ):
        """
        Parameters
        ----------

        name : str
            boundary name
        show_edges : bool
            show edges
        lighting : bool
            lighting of this boundary
        camera_position : str
            camera position, like "xy"
        color : str
            color of the boundary
        whole_mesh_opacity : float
            the opacity of the whole mesh, in range (0, 1)
        add_legend : bool
            add legend for domain and boundary
        Examples
        --------

        >>> sim.output.fields.plot_boundary("bottom", color="g", whole_mesh_opacity=0.05)

        """
        if not pyvista_importable:
            raise NotImplementedError

        mesh, times = self._init_pyvista()
        boundaries = mesh["boundary"]
        try:
            boundary = boundaries[name]
        except KeyError:
            print(
                f"Boundary name('{name}') is not correct, boundaries:\n{boundaries.keys()}"
            )
            print(
                f"try something like: sim.output.fields.plot_boundary('{boundaries.keys()[0]}')"
            )
        else:
            plotter = pyvista.Plotter()
            if 0 < whole_mesh_opacity <= 1:
                plotter.add_mesh(mesh, opacity=whole_mesh_opacity, label="domain")
            elif whole_mesh_opacity != 0:
                print("whole_mesh_opacity should be in the range of (0, 1).")

            plotter.add_mesh(
                boundary,
                show_edges=show_edges,
                color=color,
                lighting=lighting,
                label=name,
                **kwargs,
            )
            plotter.camera_position = camera_position
            if add_legend:
                plotter.add_legend(face=None)
            plotter.add_axes()
            plotter.show()

    def plot_contour(
        self,
        variable="U",
        component=None,
        time=None,
        normal="y",
        camera_position=None,
        block=0,
        whole_mesh_opacity=0,
        show=True,
        plotter=None,
        **kwargs,
    ):
        """
        Parameters
        ----------

        variable : str
            variable name
        component : int
            components of vector field (x:0, y:1, z:2)
        time : float
            simulation time
        normal : str
            normal of the plane
        camera_position : str
            camera position plane like: "xy"
        block : int
            block number
        whole_mesh_opacity : float
            the opacity of the whole mesh, in range (0, 1)

        Examples
        --------

        >>> sim.output.fields.plot_contour(normal="y", variable="U", whole_mesh_opacity=0.1, time=86400.0, component=2)

        """
        if not pyvista_importable:
            raise NotImplementedError

        mesh, times = self._init_pyvista(time)
        block = mesh[block]
        internal_mesh_slice = block.slice(normal)
        if not plotter:
            plotter = pyvista.Plotter()

        if 0 < whole_mesh_opacity <= 1:
            plotter.add_mesh(mesh, color="w", opacity=whole_mesh_opacity)
        elif whole_mesh_opacity != 0:
            print("whole_mesh_opacity should be in the range of (0, 1).")
        components = {0: "x", 1: "y", 2: "z", None: ""}
        plotter.add_mesh(
            internal_mesh_slice,
            scalars=variable,
            component=component,
            scalar_bar_args={"title": f"{variable}{components[component]}"},
            **kwargs,
        )

        cpositions = {"x": "yz", "y": "xz", "z": "xy"}
        if not camera_position:
            camera_position = cpositions[normal]
        plotter.camera_position = camera_position
        plotter.add_axes()
        if show:
            plotter.show()
        else:
            return plotter

    def plot_animation(
        self,
        filename="filename",
        variable="U",
        component=None,
        start=0,
        end=None,
        normal="y",
        camera_position="xz",
        block=0,
        whole_mesh_opacity=0,
        **kwargs,
    ):
        """
        Parameters
        ----------

        filename : str
            animation file name (without postfix)
        variable : str
            variable name
        component : int
            components of vector field (x:0, y:1, z:2)
        start : float
            start time
        end : float
            end time
        normal : str
            normal of the plane
        camera_position : str
            camera position plane
        block : int
            block number

        Examples
        --------

        >>> sim.output.fields.plot_animation(filename="my_animation", variable="U", component=0, start=360, end=3600)

        """
        if not pyvista_importable:
            raise NotImplementedError

        plotter = pyvista.Plotter()
        filename += ".mp4"
        plotter.open_movie(filename)
        mesh, time_pv = self._init_pyvista()

        if not end:
            times = time_pv
        else:
            times = np.arange(
                start, end + 1, self.sim.params.control_dict.write_interval
            )

        for time in times:
            plotter = self.plot_contour(
                variable=variable,
                block=block,
                component=component,
                time=time,
                normal=normal,
                camera_position=camera_position,
                plotter=plotter,
                show=False,
                **kwargs,
            )
            plotter.add_text(f"Simulation Time: {time}s", name="time-label")
            plotter.write_frame()

        plotter.close()

    def plot_mesh(
        self,
        color="w",
        style="wireframe",
        **kwargs,
    ):
        """
        Parameters
        ----------

        color : str
            color of mesh
        style : int
            style of mesh

        Examples
        --------

        >>> sim.output.fields.plot_mesh()

        """
        if not pyvista_importable:
            raise NotImplementedError

        mesh, times = self._init_pyvista()
        plotter = pyvista.Plotter()

        plotter.add_mesh(
            mesh,
            style=style,
            color=color,
            **kwargs,
        )

        plotter.show()
