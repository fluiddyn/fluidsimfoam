from fluidsimfoam.output import get_dataframe_from_paths, path_dir_results

path_root = path_dir_results / "sedFoam/bedload1d"

paths = sorted(path_root.glob("sed_*"))


def customize(result, sim):
    result["nz"] = sim.params.block_mesh_dict.nz
    result["radius"] = sim.params.constant.transport.phasea.d
    time, residual = sim.output.log.get_last_residual()
    result["last_time"] = time
    result["last_residual"] = residual


df = get_dataframe_from_paths(paths, customize=customize)

print(df)
# df.plot(x="radius", y="last_residual")
