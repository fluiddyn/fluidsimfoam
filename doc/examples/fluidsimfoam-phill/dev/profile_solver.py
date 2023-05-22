"""

```
python profile_solver.py
pip install gprof2dot
gprof2dot -f pstats profile.pstats | dot -Tpng -o profile.png
```

Conclusions:

- creating the default parameters is a bit slow because of underscore and co
  (not too bad).

- there is a real performance issue with the method
  `foam_input_files.fields.FieldABC.from_code` when there are calculated boundaryField.

  https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/blob/branch/default/src/fluidsimfoam/foam_input_files/fields.py#L36

```
boundaryField
{
    top
    {
        type            calculated;
        value           nonuniform List<scalar>
20
(
50
150
250
350
450
550
650
750
850
950
1050
1150
1250
1350
1450
1550
1650
1750
1850
1950
)
;
...
```

The issue is actually in fluidsimfoam.operators.Operators.get_cell_coords

https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/blob/branch/default/src/fluidsimfoam/operators.py#L39

where we do

```
        def get_arr(path):
            field = VolScalarField.from_path(path)
            return field.get_array()

        path_cy = path_cx.with_name("Cy")
        path_cz = path_cx.with_name("Cz")

        return get_arr(path_cx), get_arr(path_cy), get_arr(path_cz)


We can instead read only the cell centers written in 0/C.

```

"""

import cProfile
from time import perf_counter

from fluidsimfoam_phill import Simul

t0 = perf_counter()

params = Simul.create_default_params()
cProfile.runctx(
    "params = Simul.create_default_params()",
    globals(),
    locals(),
    "profile_params.pstats",
)

print(f"params created in {perf_counter() - t0:.2f} s")

params.output.sub_directory = "examples_fluidsimfoam/phill"
params.short_name_type_run = "sin_2d"

params.init_fields.buoyancy_frequency = 0.001
params.transport_properties.nu = 0.01
params.transport_properties.pr = 10

params.control_dict.end_time = 1200000
params.control_dict.delta_t = 10

params.block_mesh_dict.lx = 2000
params.block_mesh_dict.ly = 5000
params.block_mesh_dict.nx = 20
params.block_mesh_dict.ny = 50
params.block_mesh_dict.h_max = 80

params.fv_options.momentum_source.active = True
params.fv_options.momentum_source.ubar = "(0.1 0 0)"
params.fv_options.atm_coriolis_u_source.active = True

t0 = perf_counter()
cProfile.runctx("sim = Simul(params)", globals(), locals(), "profile.pstats")
print(f"Simulation directory created in {perf_counter() - t0:.2f} s")
