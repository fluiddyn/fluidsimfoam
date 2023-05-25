"""Create a dataframe from result directories"""

from fluidsim_core.output.dataframe_from_paths import DataframeMaker
from fluidsimfoam import load_simul
from fluidsimfoam.output.log import read_time_last


class DataframeMakerFoam(DataframeMaker):
    def get_time_start_from_path(self, path):
        """Get first time"""
        logfiles = sorted(path.glob("log*.txt"))
        path_log = logfiles[0]
        with open(path_log) as file:
            for line in file:
                if line.startswith("start_time = "):
                    return float(line.split()[-1])

    def get_time_last_from_path(self, path):
        """Get last saved time"""
        logfiles = sorted(path.glob("log*.txt"))
        path_log = logfiles[-1]
        return read_time_last(path_log)

    def load_sim(self, path):
        """Load a simulation object"""
        return load_simul(path, hide_stdout=True)


_dataframe_maker = DataframeMakerFoam()

get_mean_values_from_path = _dataframe_maker.get_mean_values_from_path
get_dataframe_from_paths = _dataframe_maker.get_dataframe_from_paths
