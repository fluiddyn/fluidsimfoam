from time import sleep, time

from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_fluidsimfoam/tgv"

sim = Simul(params)

# needed (strange OpenFOAM bug?)
sleep(1)

process = sim.make.exec_async("run")

sleep(2)
t_stop = time()

print(sim.output.log.text[-200:])

with open(sim.path_run / "system/controlDict") as file:
    for line in file:
        if line.startswith("stopAt"):
            print(line)
            break

print("Telling OpenFOAM to stop...")
ctr_dict = sim.input_files.control_dict.read()
ctr_dict["stopAt"] = "writeNow"
ctr_dict.overwrite()

with open(sim.path_run / "system/controlDict") as file:
    for line in file:
        if line.startswith("stopAt"):
            print(line)
            break

while process.poll() is None:
    sleep(0.05)
    print(
        "\r",
        sorted(
            path.name for path in sim.path_run.glob("*") if path.name[0].isdigit()
        ),
        end="",
    )

print(f"\nSimulation stopped {time() - t_stop:.2f} s after `stopAt = writeNow`")
