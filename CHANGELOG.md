# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

<!-- ## [Unreleased] -->

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

<!-- [Unreleased]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.3...branch%2Fdefault -->
[0.0.3]: https://foss.heptapod.net/fluiddyn/fluidsimfoam/-/compare/0.0.2...0.0.3
