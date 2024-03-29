# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

```{warning}

Fluidsimfoam is still in quite early development. Before version 0.1.0, the API
is still a bit unstable!

```

<!--

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

Type of changes
---------------

Added for new features.
Changed for changes in existing functionality.
Deprecated for soon-to-be removed features.
Removed for now removed features.
Fixed for any bug fixes.
Security in case of vulnerabilities.

-->

<!-- (changelog/unreleased)= -->

## [Unreleased]

## [0.0.7] - 2023-06-27

```{warning}

This release contains major improvements in terms of usability for real
projects! And also two important incompatible changes:

- The template files now have to be organized as in a standard OpenFOAM case
  (in `system`, `constant` and `0` subdirectories).

- New {mod}`fluidsimfoam.invoke` subpackage. The Invoke tasks are now defined
  in {mod}`fluidsimfoam.invoke.tasks`.

```

- Plot methods `sim.output.fields.plot_...` using [pyvista] in
  {class}`fluidsimfoam.output.fields.Fields` (contribution by
  [@Pooriadf](https://foss.heptapod.net/Pooriadf)).

- [multi-region-snappy] solver (advanced solver using `snappyHexMesh` and
  `chtMultiRegionFoam`).

- Few grammar/parser/formatter fixes and improvements ([!86], [!87], [!89])

- Much better [Invoke] related code. New {class}`fluidsimfoam.invoke.context.Context` for
  OpenFOAM. New tasks for `decomposePar`, `snappyHexMesh`, etc... (see
  {mod}`fluidsimfoam.invoke.tasks`).

- {func}`fluidsimfoam.foam_input_files.parse_header` and
  {func}`fluidsimfoam.foam_input_files.read_header`.

- First support for binary OpenFOAM files
  ([!97](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/97))

## [0.0.6] - 2023-06-09

Small release before [OpenFOAM users conference](https://www.foam-u.fr/) where
[Fluidsimfoam will be presented](http://legi.grenoble-inp.fr/people/Pierre.Augier/fluidsimfoam-at-openfoam-users-conference.html).

- Improve [phill] solver + few `blockMesh` improvements

- Few bug fixes and code improvements

## [0.0.5] - 2023-06-05

- `params.resources` to copy files and directories in the simulation directories. These
  files can be saved in the solver packages.

- Support for `setFieldsDict` files

- Command `fluidsimfoam-initiate-solver`

- [dam] solver to reproduce the [Breaking of a dam tutorial]

- `fluidsim_core==0.7.3`

- {func}`fluidsimfoam.output.get_mean_values_from_path` and
  {func}`fluidsimfoam.output.get_dataframe_from_paths`

- Merge request
  [!54](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/54): parallel
  simulations

  - {class}`fluidsimfoam.foam_input_files.decompose_par.DecomposeParDictHelper`
  - Improve `run` task to call `decomposePar` and `mpirun`

## [0.0.4] - 2023-05-22

- Helper to define fvOptions files:
  {class}`fluidsimfoam.foam_input_files.fv_options.FvOptionsHelper`

- [cbox], [phill] and [cavity] solvers

* {class}`fluidsimfoam.foam_input_files.blockmesh.BlockMeshDictRectilinear`

* Merge request
  [!44](https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/44):

  - {class}`fluidsimfoam.output.log.Log`
  - Improve run task (save OpenFOAM log and minimal logging)
    ({func}`fluidsimfoam.tasks.run`)
  - {func}`fluidsimfoam.make.MakeInvoke.exec_async`
  - {func}`fluidsimfoam.solvers.base.SimulFoam.stop_time_loop`
  - Poetry extra for Qt (`poetry install -E qt` or `pip install "fluidsimfoam[qt]"`)
  - Fix parameters ({mod}`fluidsimfoam.params`)
  - {class}`fluidsimfoam.foam_input_files.fields.VolTensorField` and fixes in AST and
    fields.

* Poetry extra for Jupyter (`poetry install -E jupyter`, `poetry install --all-extras` or
  `pip install "fluidsimfoam[jupyter]"`)

* Various bug fixes, API improvements and optimizations...

* [CONTRIBUTING.md](https://fluidsimfoam.readthedocs.io/en/latest/CONTRIBUTING.html)

* OpenFOAM simulations on ReadTheDocs servers allowing tutorials using OpenFOAM

## [0.0.3] - 2023-05-09

- Improve formatting input files

- Utilities to define solvers and input files

  - {class}`fluidsimfoam.foam_input_files.FileHelper`

  - {class}`fluidsimfoam.foam_input_files.fields.VolScalarField` and
    {class}`fluidsimfoam.foam_input_files.fields.VolVectorField` and
    {func}`fluidsimfoam.foam_input_files.fields.read_field_file`

  - {class}`fluidsimfoam.foam_input_files.fv_schemes.FvSchemesHelper`

  - {class}`fluidsimfoam.foam_input_files.constant_files.ConstantFileHelper`

  - {func}`fluidsimfoam.foam_input_files.ast.FoamInputFile.init_from_py_objects`

## 0.0.2 - 2023-04-26

- Unstable API to define solvers
- Can setup, run and reload simulations
- Parser for OpenFOAM input files ({mod}`fluidsimfoam.foam_input_files`)
- Utility to create blockMeshDict files ({mod}`fluidsimfoam.foam_input_files.blockmesh`)

[!86]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/86
[!87]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/87
[!89]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/merge_requests/89
[0.0.3]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.2...0.0.3
[0.0.4]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.3...0.0.4
[0.0.5]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.4...0.0.5
[0.0.6]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.5...0.0.6
[0.0.7]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.6...0.0.7
[breaking of a dam tutorial]: https://www.openfoam.com/documentation/tutorial-guide/4-multiphase-flow/4.1-breaking-of-a-dam
[cavity]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-cavity
[cbox]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-cbox
[dam]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-dam
[invoke]: https://docs.pyinvoke.org
[multi-region-snappy]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-multi-region-snappy
[phill]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/tree/branch/default/doc/examples/fluidsimfoam-phill
[pyvista]: https://docs.pyvista.org
[unreleased]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.7...branch%2Fdefault
