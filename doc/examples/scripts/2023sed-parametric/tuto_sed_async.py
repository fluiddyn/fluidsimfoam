#!/usr/bin/env python3

import argparse
from datetime import timedelta
from time import sleep, time

import matplotlib.pyplot as plt
import numpy as np
from fluidsimfoam_sed import Simul

parser = argparse.ArgumentParser(
    prog="bed-load-1d",
    description="Run a bed load simulation with sedFoam",
)

parser.add_argument("-p", "--plot", action="store_true")
parser.add_argument("-np", "--nprocs", default=1, type=int)
parser.add_argument("--diameter", default=0.006, type=float)
parser.add_argument("--end-time", default=20.0, type=float)

args = parser.parse_args()

params = Simul.create_default_params()
params.output.sub_directory = "sedFoam/bedload1d"
params.short_name_type_run = f"diameter{args.diameter}"

params.control_dict.write_interval = 0.5
params.control_dict.end_time = args.end_time

params.parallel.nsubdoms = args.nprocs
params.parallel.method = "simple"
params.parallel.nsubdoms_xyz = [1, 1, args.nprocs]

params.constant.transport.phasea.d = args.diameter

sim = Simul(params)

print(f"Launching OpenFOAM application ({params.control_dict.application})")
time_start = time()
process = sim.make.exec_async("run")

# we need to be sure that the time loop is started before stopping it
while sim.output.log.time_last is None:
    sleep(0.5)
print(f"Time loop started (equation time = {sim.output.log.time_last})")


while sim.output.log.time_last < params.control_dict.write_interval:
    sleep(0.5)

gradp = params.constant.force.grad_pmean[0]
x, y, z = sim.output.sim.oper.get_cells_coords()
bed_height = params.init_fields.bed_height


def get_tau():
    field = sim.output.fields.read_field("Taub", time_approx="last")
    tau = field.get_array()
    return tau[:, 3], np.gradient(tau[:, 3], y), field.time


cond_height = y > 1.6 * bed_height

nb_saved_times = 1

tau, grad_tau, t_now = get_tau()
if args.plot:
    plt.ion()
    fig, (ax0, ax1) = plt.subplots(2)

    ax0.set_xlabel(r"$R_{xz}^f$")
    ax0.set_ylabel("$z$")
    ax1.set_xlabel("$t$")
    ax1.set_ylabel("residuals p_rbgh")

    ax0.plot(gradp * (y[-1] - y[cond_height]), y[cond_height], c="r")
    (line,) = ax0.plot(tau, y)
    ax0.set_title(f"t = {t_now}")

    ax1.plot(*sim.output.log.get_last_residual(), "x")
    ax1.set_yscale("log")

    plt.show(block=False)
    fig.tight_layout()
    pause = plt.pause
else:
    pause = sleep


cond_statio = False
while not cond_statio and t_now < params.control_dict.end_time:
    pause(0.5)
    saved_times = sim.output.fields.get_saved_times()
    if args.plot:
        ax1.plot(*sim.output.log.get_last_residual(), "x")

    if len(saved_times) > nb_saved_times:
        nb_saved_times = len(saved_times)
        tau, grad_tau, t_now = get_tau()

        if args.plot:
            line.set_xdata(tau)
            ax0.set_title(f"t = {t_now}")
            fig.canvas.draw()

        percentage = 100 * abs(grad_tau[cond_height] + gradp).mean() / gradp

        execution_time = timedelta(seconds=time() - time_start)
        print(
            f"New saved time: {t_now}, condition: {percentage:2.3f} %, "
            f"execution time: {execution_time}",
            flush=True,
        )
        cond_statio = percentage < 2.0

if cond_statio:
    print("Stationnary reached...")
    sim.stop_time_loop()
else:
    while process.poll() is None:
        sleep(0.2)
    print("Simulation done (end time reached)")

assert process.returncode == 0, process.returncode
