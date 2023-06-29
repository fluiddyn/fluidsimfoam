"""Extended Invoke Context for OpenFOAM

"""

import os
from pathlib import Path
from shutil import copytree, rmtree
from typing import Optional

import invoke.context

from fluiddyn.util import time_as_str
from fluidsimfoam.util import get_parallel_info, make_hex


class Context(invoke.context.Context):
    """Extended Invoke Context for OpenFOAM"""

    time_as_str = time_as_str()
    """Time of Invoke call
    """

    def __init__(self, *args, **kwargs):
        self._set(path_run=Path.cwd())

        parallel, nsubdoms = get_parallel_info()
        self._set(parallel=parallel)
        self._set(nsubdoms=nsubdoms)

        if os.environ.get("FOAM_MPI", "") == "msmpi":
            mpi_command = "mpiexec"
        else:
            mpi_command = "mpirun"
        self._set(mpi_command=mpi_command)

        super().__init__(*args, **kwargs)

    def run_appl(
        self,
        command: str,
        name_command: Optional[str] = None,
        suffix_log: Optional[str] = None,
    ):
        """Run an OpenFOAM application and save the log"""
        if name_command is None:
            name_command = command.split()[0]

        name_log = f"log.{name_command}"

        if suffix_log is not None:
            name_log += "-" + suffix_log

        path_log = Path(f"logs{self.time_as_str}/{name_log}")

        path_log.parent.mkdir(exist_ok=True)
        with open(path_log, "w") as file:
            try:
                self.run(command, echo=True, out_stream=file, err_stream=file)
            except invoke.exceptions.UnexpectedExit:
                file.flush()
                print(
                    f"Error for command {command}\n"
                    f"log file content:\n{path_log.read_text()}"
                )

    def run_appl_once(
        self,
        command: str,
        suffix_log: Optional[str] = None,
        dict_file: Optional[str] = None,
        check_dict_file: bool = True,
        force: bool = False,
        parallel_if_needed: bool = False,
        path_decompose_par_dict: Optional[str] = None,
        nsubdoms: Optional[int] = None,
    ):
        """Run an OpenFOAM application only once per simulation"""
        command_name = command.split()[0]

        if check_dict_file and not force:
            if dict_file is None:
                dict_file = "system/" + command_name + "Dict"

            path_dict_file = Path(dict_file)
            if not path_dict_file.exists():
                return

        lock_name = f"{command_name}_called"
        if command_name != command:
            lock_name += make_hex(command)

        path_command_called = Path(f".data_fluidsim/{lock_name}")
        path_command_called.parent.mkdir(exist_ok=True)
        if force or not path_command_called.exists():
            path_command_called.touch()

            if not parallel_if_needed:
                parallel = False
            else:
                if path_decompose_par_dict is None:
                    parallel = self.parallel
                    nsubdoms_file = self.nsubdoms
                else:
                    parallel, nsubdoms_file = get_parallel_info(
                        path_decompose_par_dict
                    )
                    command += f" -decomposeParDict {path_decompose_par_dict}"

            name_command = command.split()[0]

            if parallel:
                if nsubdoms is None:
                    nsubdoms = nsubdoms_file
                command = f"{self.mpi_command} -n {nsubdoms} {command} -parallel"

            self.run_appl(
                command, name_command=name_command, suffix_log=suffix_log
            )

    def save_0_dir(self):
        """Save ``0`` directory in ``O.orig``"""
        print("Saving 0 to O.orig")
        copytree("0", "O.orig", dirs_exist_ok=True)

    def restore_0_dir(self):
        """Restore ``0`` directory from ``O.orig``"""
        print("Restoring 0 directory")
        paths_0 = ["0"]
        paths_0.extend(Path.cwd().glob("processor*/0"))
        for path0 in paths_0:
            rmtree(path0, ignore_errors=True)
            copytree("O.orig", path0)
