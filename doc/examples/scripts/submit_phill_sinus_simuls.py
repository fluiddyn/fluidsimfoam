import numpy as np

from fluiddyn.clusters.legi import Calcul8 as Cluster

h_max = [40, 80]


nx = 160
ny = 1000

end_time = 86400
dt = 10

nsave = 30

nb_procs = 10
nb_nodes = 1
walltime = "00:03:00"


cluster = Cluster()

cluster.commands_setting_env = [
    "PROJET_DIR=/fsnet/project/meige/2023/23FLUIDSIMFOAM",
    "source /etc/profile",
    "export PATH=$HOME/.local/bin:$PATH",
    "module purge",
    "module load openfoam/2212plus",
    "export VENV_PATH=$(poetry env info -p)",
    "source $VENV_PATH/bin/activate",
]


for h in h_max:
    command = (
        f"tuto_phill_sinus.py -nx {nx} -ny {ny} -nsave {nsave} "
        f"-h_max {h} --end-time {end_time} -np {nb_nodes*nb_procs}"
    )

    print(command)

    name_run = f"phill_sinus_h_max{h}"

    cluster.submit_script(
        command,
        name_run=name_run,
        walltime=walltime,
        nb_nodes=nb_nodes,
        nb_cores_per_node=nb_procs,
        omp_num_threads=1,
        ask=False,
    )
