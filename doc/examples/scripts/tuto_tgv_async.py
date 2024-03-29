from time import sleep

from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_fluidsimfoam/tgv"

sim = Simul(params)

print(f"Launching OpenFOAM application ({sim.params.control_dict.application})")
process = sim.make.exec_async("run")

# we need to be sure that the time loop is started before stopping it
while sim.output.log.time_last is None:
    sleep(0.5)
print(f"Time loop started (equation time = {sim.output.log.time_last})")

sim.stop_time_loop()

assert process.returncode == 0
