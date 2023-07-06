"""Class for the ``sim.output.fields`` object"""

import math
import shutil
from numbers import Number
from subprocess import PIPE, run

import matplotlib.pyplot as plt
import numpy as np

try:
    import pyvista
except ImportError:
    pass


from fluidsimfoam.foam_input_files import read_field_file

components = {0: "x", 1: "y", 2: "z", None: ""}
cam_positions = {"x": "yz", "y": "xz", "z": "xy"}


def check_pyvista_importable():
    try:
        import pyvista
    except ImportError:
        print(
            "pyvista is not importable so it cannot be used. "
            "You could install it (`pip install pyvista`) and retry."
        )
        return False
    else:
        return True


def is_time_name(name):
    return all(c.isdigit() or c == "." for c in name)


def find_nearest(arr, value):
    idx = np.searchsorted(arr, value, side="left")
    if idx > 0 and (
        idx == len(arr)
        or math.fabs(value - arr[idx - 1]) < math.fabs(value - arr[idx])
    ):
        return arr[idx - 1]
    else:
        return arr[idx]


def check_opacity(opacity):
    if not (0 <= opacity <= 1):
        raise ValueError("opacity should be in [0, 1[.")


if check_pyvista_importable():

    class Reader(pyvista.POpenFOAMReader):
        def __init__(self, path):
            super().__init__(path)
            self.skip_zero_time = True
            self.mesh = self.read()

        def set_active_time(self, time=None):
            if time is not None:
                time = float(time)
            if time is None:
                time = self.time_values[-1]
            elif time not in self.time_values:
                time = find_nearest(self.time_values, time)
            self.set_active_time_value(time)
            return time


def get_dimensions(mesh):
    n_blocks = mesh.n_blocks
    if mesh.keys() != ["internalMesh", "boundary"]:
        # multiregion mesh
        data = mesh[0]["internalMesh"]
        points = data.cell_centers().points
        for index_block in range(1, n_blocks):
            data0 = mesh[index_block]["internalMesh"]
            points0 = data0.cell_centers().points
            points = np.concatenate((points, points0), axis=0)
    else:
        interior_mesh = mesh["internalMesh"]
        centers = interior_mesh.cell_centers()
        points = centers.points
    cell_coords = x, y, z = points[:, 0], points[:, 1], points[:, 2]
    dimensions = ""
    for letter, coord in zip("xyz", cell_coords):
        if coord.max() - coord.min() < 1e-15:
            continue
        dimensions += letter
    return dimensions


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

    def _init_pyvista_reader(self):
        if not check_pyvista_importable():
            import pyvista
        casename = f".{self.output.sim.info_solver.short_name}.foam"
        path = self.output.sim.path_run / casename
        if not path.exists():
            path.write_text("")
        return Reader(path)

    def plot_boundary(
        self,
        name=None,
        show_edges=True,
        lighting=True,
        camera_position=None,
        color="w",
        mesh_opacity=1,
        add_legend=False,
        show=True,
        plotter=None,
        **kwargs,
    ):
        """
        Parameters
        ----------

        name : str
            Boundary name
        show_edges : bool
            Show edges
        lighting : bool
            Lighting of this boundary
        camera_position : str
            Camera position, like "xy"
        color : str
            Color of the boundary
        mesh_opacity : float
            The opacity of the whole mesh, in range (0, 1)
        add_legend : bool
            Add legend for domain and boundary
        show : bool
            Show plot

        Examples
        --------

        >>> sim.output.fields.plot_boundary(
        ...     "bottom", color="g", mesh_opacity=0.05)
        >>> sim.output.fields.plot_boundary(
        ...     "lowerBoundary", color="b", mesh_opacity=0.05, add_legend=True)

        """
        check_opacity(mesh_opacity)

        reader = self._init_pyvista_reader()
        mesh = reader.mesh
        boundaries = mesh["boundary"]
        dimensions = get_dimensions(mesh)

        if name not in boundaries.keys():
            print(f"Boundary names: {boundaries.keys()}")
            return

        boundary = boundaries[name]

        if plotter is None:
            plotter = pyvista.Plotter()

        plotter.add_mesh(
            mesh,
            opacity=mesh_opacity,
            style="wireframe",
            color="w",
            label="domain",
        )
        plotter.add_mesh(
            boundary,
            color=color,
            lighting=lighting,
            label=name,
            show_edges=show_edges,
            **kwargs,
        )
        if len(dimensions) == 2:
            plotter.camera_position = dimensions
        else:
            plotter.camera_position = camera_position
        if add_legend:
            plotter.add_legend(face=None)
        plotter.add_axes()
        if show:
            plotter.show()
        return plotter

    def plot_contour(
        self,
        variable="U",
        component=None,
        time=None,
        equation=None,
        camera_position=None,
        mesh_opacity=0,
        show=True,
        contour=False,
        plotter=None,
        **kwargs,
    ):
        """
        Parameters
        ----------

        variable : str
            Variable name
        component : int
            Components of vector field (x:0, y:1, z:2)
        time : float
            Simulation time
        equation : str
            The equation of the plane for contour
        camera_position : str
            Camera position plane like: "xy"
        mesh_opacity : float
            The opacity of the whole mesh, in range (0, 1)
        contour : bool
            Apply a contour filter after slicing.

        Examples
        --------

        >>> sim.output.fields.plot_contour(
        ...     equation="y=0", variable="U",
        ...     mesh_opacity=0.1, time=86400.0, component=2)

        >>> sim.output.fields.plot_contour(
        ...     equation="z=0", variable="T", time=3600.0, contour=True)

        """
        check_opacity(mesh_opacity)

        reader = self._init_pyvista_reader()
        time = reader.set_active_time(time)
        data = reader.read()

        block = data["internalMesh"]
        block.set_active_scalars(variable, preference="point")
        if plotter is None:
            plotter = pyvista.Plotter()

        plotter.add_mesh(data, color="w", opacity=mesh_opacity)

        dimensions = get_dimensions(data)
        if len(dimensions) == 2:
            axis = "xyz".replace(dimensions[:], "")
            coordinate = 0
            internal_mesh_slice = block.slice_along_axis(
                n=1, axis=axis, contour=contour
            )
        elif len(dimensions) == 3:
            if equation is None:
                print(
                    f"This is the '{variable}' contour for 'y=0', specify the equation to change the plane!"
                )
                equation = "y=0"
            equation = equation.replace(" ", "")
            axis, coordinate = tuple(equation.split("="))
            x = block.center[0]
            y = block.center[1]
            z = block.center[2]
            if axis == "x":
                x = float(coordinate)
            elif axis == "y":
                y = float(coordinate)
            else:
                z = float(coordinate)

            internal_mesh_slice = block.slice(
                normal=axis, origin=[x, y, z], contour=contour
            )
        else:
            print("plot_contour is not available for 1D fields!")

        try:
            plotter.add_mesh(
                internal_mesh_slice,
                scalars=variable,
                component=component,
                scalar_bar_args={"title": f"{variable}{components[component]}"},
                **kwargs,
            )
        except ValueError:
            interior = data["internalMesh"]
            print(
                f"""Selected plane is out of domain, change the equation!
            Domain ranges:
            x:({interior.bounds[0]}, {interior.bounds[1]})
            y:({interior.bounds[2]}, {interior.bounds[3]})
            z:({interior.bounds[4]}, {interior.bounds[5]})"""
            )

        if camera_position is None:
            camera_position = cam_positions[axis]
        plotter.camera_position = camera_position
        plotter.add_axes()
        if show:
            plotter.show()
        return plotter

    def plot_profile(
        self,
        point0=[0, 0, 0],
        point1=[0, 1, 0],
        variable="U",
        component=None,
        time=None,
        line_width=2,
        color="r",
        show_line_in_domain=False,
        show=True,
        plotter=None,
        **kwargs,
    ):
        """
        Parameters
        ----------

        point0 : list
            Coordinate of first point
        point1 : list
            Coordinate of second point
        variable : str
            Variable name
        component : int
            Components of vector field (x:0, y:1, z:2)
        line_width : str
            Line width of preview plot
        color : str
            Line color of preview plot
        time : float
            Simulation time
        show_line_in_domain : bool
            Preview line in the domain

        Examples
        --------

        >>> sim.output.fields.plot_profile(
        ...     point0=[0,0,5], point1=[0,0,20], variable="T", time=3600,
        ...     ylabel="T(K)", title="Temperature")

        """
        reader = self._init_pyvista_reader()
        time = reader.set_active_time(time)
        data = reader.read()

        block = data["internalMesh"]
        block.set_active_scalars(variable)
        for index in range(3):
            if point0[index] < block.bounds[2 * index]:
                point0[index] = block.bounds[2 * index]
            if point1[index] > block.bounds[2 * index + 1]:
                point1[index] = block.bounds[2 * index + 1]

        if show_line_in_domain:
            plotter = pyvista.Plotter()
            plotter.add_mesh(data, style="wireframe", color="w")
            line = pyvista.Line(point0, point1)
            plotter.add_mesh(
                line,
                color=color,
                line_width=line_width,
            )
            plotter.add_axes()
            if show:
                plotter.show()

        block.plot_over_line(point0, point1, show=show, **kwargs)
        return plotter, plt.gcf()

    def plot_mesh(
        self,
        color="w",
        style="wireframe",
        show=True,
        plotter=None,
        **kwargs,
    ):
        """
        Parameters
        ----------

        color : str
            Color of mesh
        style : str
            Style of mesh ('wireframe', 'points', 'surface')
        show : bool
            Show plot

        Examples
        --------

        >>> sim.output.fields.plot_mesh(color="g")

        """
        reader = self._init_pyvista_reader()
        mesh = reader.read()
        if plotter is None:
            plotter = pyvista.Plotter()
        plotter.add_mesh(
            mesh,
            style=style,
            color=color,
            **kwargs,
        )
        plotter.add_axes()
        dimensions = get_dimensions(mesh)
        if len(dimensions) == 2:
            plotter.camera_position = dimensions
        if show:
            plotter.show()
        return plotter
