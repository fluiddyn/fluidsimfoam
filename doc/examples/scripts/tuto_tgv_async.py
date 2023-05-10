from time import sleep, time

from fluidsimfoam_tgv import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_fluidsimfoam/tgv"

sim = Simul(params)

process = sim.make.exec_async("run")

sleep(2)
t_stop = time()

print("Telling OpenFOAM to stop...")
ctr_dict = sim.input_files.control_dict.read()
ctr_dict["stopAt"] = "writeNow"
ctr_dict.overwrite()

while process.poll() is None:
    sleep(0.01)

print(f"Simulation stopped {time() - t_stop:.2f} s after `stopAt = writeNow`")
