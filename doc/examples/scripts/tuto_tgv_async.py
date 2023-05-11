from time import sleep, time

from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_fluidsimfoam/tgv"

sim = Simul(params)

print("Launching simulation")
process = sim.make.exec_async("run")

while sim.output.log.time_last is None:
    sleep(0.2)

print("Time loop started")


def print_ctr_dict():
    print("In system/controlDict:")
    with open(sim.path_run / "system/controlDict") as file:
        for line in file:
            if any(
                line.startswith(var_name) for var_name in ("stopAt", "endTime")
            ):
                print("  " + line.strip())


print_ctr_dict()

print("Telling OpenFOAM to stop... (overwrite controlDict file)")
ctr_dict = sim.input_files.control_dict.read()
ctr_dict["stopAt"] = "writeNow"
t_stop = time()
ctr_dict.overwrite()

print_ctr_dict()

while process.poll() is None:
    # needed (strange OpenFOAM bug?)
    (sim.path_run / "system/controlDict").touch()
    sleep(0.05)
    saved_directories = sorted(
        path.name for path in sim.path_run.glob("*") if path.name[0].isdigit()
    )
    print(f"\rsaved times {saved_directories}", end="")

print(f"\nSimulation stopped {time() - t_stop:.2f} s after `stopAt = writeNow`")
