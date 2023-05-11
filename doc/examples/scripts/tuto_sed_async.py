from time import sleep

from fluidsimfoam_sed import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_fluidsimfoam/sed"
params.control_dict.write_interval = 1

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

tau = sim.output.fields.read_field("Taua", time_approx="last")

sim.stop_time_loop()

assert process.returncode == 0
