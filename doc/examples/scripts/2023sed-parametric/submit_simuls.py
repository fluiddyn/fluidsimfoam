#!/usr/bin/env python3

import numpy as np

from fluiddyn.clusters.legi import Calcul8 as Cluster

cluster = Cluster()

cluster.commands_setting_env = [
    "source /etc/profile",
    "export PATH=$HOME/.local/bin:$PATH",
    "module purge",
    "module load openfoam/2212plus",
    "export VENV_PATH=$(pdm info --where)/.venv",
    "source $VENV_PATH/bin/activate",
]

for diameter in np.linspace(0.004, 0.04, 10):
    cluster.submit_command(
        f"./tuto_sed_async.py --diameter {diameter}",
        name_run=f"sedFoam_r{diameter:.3f}",
        nb_cores_per_node=1,
        walltime="4:00:00",
        nb_mpi_processes=None,
        omp_num_threads=1,
        ask=False,
        run_with_exec=True,
    )
