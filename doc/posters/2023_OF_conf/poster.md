<div style="height: 90pt;"></div>
<div style="flex: 0 0 8%; margin-top: -10pt;">
<img src="http://legi.grenoble-inp.fr/people/Pierre.Augier/docs/ipynb/lmfa20170908/fig/logo_LEGI.jpg">
</div>
<div style="flex: 0 0 65%; text-align: center;">
<h2 style="margin-bottom: 10pt;">
Fluidsimfoam, a new Python framework for running and postprocessing OpenFOAM simulations
</h2>
<h3>Pierre Augier</h3>
</div>

--split--

OpenFOAM (OF) is a very popular open-source C++ CFD framework. With Fluidsimfoam, we try
to design and propose a new workflow for OpenFOAM based on Python.

### Principles

- A Python layer to help the users to interact with OF

- Description of a set of potential simulations (and not only of one "case"). Described
  in Python (with potentially Jinja templates) in a small Python package called a
  "Fluidsimfoam solver".

- Python APIs to describe and create parametrized input OF files.

- Python APIs and commands to launch, restart, reload simulations, and load/process/plot
  data. For example easy creation of figures and movies.

- All directory and file creations done automatically

- Integrated object (`sim`) to represent and interact with the simulation and the
  associated data

### Particularly suitable for

- automation of simulation launching (parametric studies, optimization, ...)

- programmatic generation of complex and parametrized input files (for example
  `blockMeshDict`) and initial conditions (computed in Python),

- programmatic control of simulations at runtime

!!! tip "Super easy to create a Fluidsimfoam solver from a case"

    ```sh
    fluidsimfoam-initiate-solver dam -c $FOAM_TUTORIALS/multiphase/interFoam/laminar/damBreak/damBreak
    ```

    Then, few modifications to parametrize the solver, for example

    ```python
    _helper_transport_properties = ConstantFileHelper(
        "transportProperties",
        {
            "phases": ["water", "air"],
            "water": {
                "transportModel": "Newtonian",
                "nu": 1e-06,
                "rho": 1000,
            },
            "air": {
                "transportModel": "Newtonian",
                "nu": 1.48e-05,
                "rho": 1,
            },
            "sigma": 0.07,
        },
    )
    ```

--split--

!!! tip "Creation and launching of a simulation"

    ```python

    from fluidsimfoam_dam import Simul

    # creation of the `params` object
    params = Simul.create_default_params()

    # modification of parameters
    params.output.sub_directory = "poster_fluidsimfoam/dam"
    params.control_dict.end_time = 1.0

    params.parallel.method = "simple"
    params.parallel.nsubdoms = 4

    params.constant.transport.water.nu = 2.e-6
    ...

    # creation of the simulation directory
    sim = Simul(params)

    # run the simulation (i.e. all necessary OpenFOAM commands)
    sim.make.exec("run")
    # or for programmatic control of the simulation
    sim.make.exec_async("run")
    ```

!!! tip "reload the simulation for simulation control / data processing / plots"

    One can recreate the `sim` object with the command `fluidsimfoam-ipy-load` or with:

    ```python
    from fluidsimfoam import load
    sim = load("/path/to/simulation/directory")
    ```

!!! note "Read and modify files"

    Change a parameter affecting just one file:

    ```python
    sim.params.control_dict.end_time = 2
    sim.output.input_files.control_dict.generate_file()
    ```

    or (even more powerfull):

    ```python
    ctrl_dict = sim.output.input_files.control_dict.read()
    ctrl_dict.set_child("endTime", 2)
    ctrl_dict.overwrite()
    ```

    Read output fields:

    ```python
    field = sim.output.fields.read_field("U", time_approx="last")
    vx, vy, vz = field.get_components()
    ```

!!! tip "Next steps"

    **Installation:** `pip install fluidsimfoam`<br>
    **Documentation:** <https://fluidsimfoam.readthedocs.io>
    **Repository:** <https://foss.heptapod.net/fluiddyn/fluidsimfoam>