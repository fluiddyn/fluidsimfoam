from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from fluidsimfoam_sed import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_fluidsimfoam/sed"
params.control_dict.write_interval = 0.5

sim = Simul(params)

print(f"Launching OpenFOAM application ({sim.params.control_dict.application})")
process = sim.make.exec_async("run")

# we need to be sure that the time loop is started before stopping it
while sim.output.log.time_last is None:
    sleep(0.5)
print(f"Time loop started (equation time = {sim.output.log.time_last})")


while sim.output.log.time_last < params.control_dict.write_interval:
    sleep(0.5)

gradp = sim.params.force_properties.grad_pmean[0]

x, y, z = sim.output.sim.oper.get_cells_coords()


def get_grad_tau():
    field = sim.output.fields.read_field("Taua", time_approx="last")
    tau = field.get_array()
    return np.gradient(tau[:, 3], y), field.time


nb_saved_times = 1

plt.ion()
fig, ax = plt.subplots()

ax.axvline(gradp)
grad_tau, t_now = get_grad_tau()
ax.plot(grad_tau, y, label=t_now)

plt.show(block=False)
plt.draw()
plt.pause(0.01)

cond = True

while cond:
    sleep(0.2)
    saved_times = sorted(
        path
        for path in sim.output.path_run.glob("*")
        if path.name[0].isdigit() and path.name != "0"
    )
    if len(saved_times) > nb_saved_times:
        nb_saved_times = len(saved_times)
        grad_tau, t_now = get_grad_tau()
        ax.plot(-0.5 * grad_tau, y, label=t_now)
        print(f"New saved time: {t_now}")
        fig.canvas.draw()
        plt.pause(0.01)

        percentage = 100 * abs(0.5 * grad_tau[y < 0.04] + gradp).max() / gradp
        print(f"{percentage = :.3f} %")
        cond = percentage > 2.0

print("Stationnary reached...")
sim.stop_time_loop()

assert process.returncode == 0
