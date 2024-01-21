"""Utilities for Fluidsimfoam

.. autosummary::
   :toctree:

   console
"""

import hashlib
from pathlib import Path
from subprocess import run


def make_hex(src):
    """Produce a hash from a string"""
    return hashlib.md5(src.encode("utf8")).hexdigest()


def read_nsubdoms_from_decomposeParDict(path_decompose_par_dict=None):
    """Read nsubdoms from a decomposeParDict file"""
    if path_decompose_par_dict is None:
        path_decompose_par_dict = "system/decomposeParDict"
    path_decompose_par_dict = Path(path_decompose_par_dict)
    if not path_decompose_par_dict.exists():
        raise ValueError(f"{path_decompose_par_dict = } does not exist")
    nsubdoms = None
    with open(path_decompose_par_dict) as file:
        for line in file:
            if "numberOfSubdomains" in line:
                line = line.strip().removesuffix(";")
                nsubdoms = int(line.split()[-1])
                break
    if nsubdoms is None:
        raise RuntimeError(f"Bad decomposeParDict {path_decompose_par_dict}")
    return nsubdoms


def get_parallel_info(path_decompose_par_dict=None):
    """Get basic parallel informations from a decomposeParDict file"""
    try:
        nsubdoms = read_nsubdoms_from_decomposeParDict(path_decompose_par_dict)
    except ValueError:
        nsubdoms = 1
        parallel = False
    else:
        parallel = nsubdoms > 1
    return parallel, nsubdoms


def get_openfoam_version():
    try:
        process = run(["icoFoam", "-help"], text=True, capture_output=True)
    except FileNotFoundError:
        return None
    try:
        version = process.stdout.split("Using: OpenFOAM-")[1].split()[0]
    except IndexError as err:
        raise RuntimeError(
            f"Cannot get OpenFOAM version from icoFoam help: '{process.stdout}'"
        ) from err
    return version.removeprefix("v").removeprefix("(").removesuffix(")")
