"""Create a dataframe from result directories"""

from fluidsim_core.output.dataframe_from_paths import DataframeMaker
from fluidsimfoam import load_simul


class DataframeMakerFoam(DataframeMaker):
    def get_time_start_from_path(self, path):
        """Get first time"""
        return NotImplemented

    def get_time_last_from_path(self, path):
        """Get last saved time"""
        return NotImplemented

    def load_sim(self, path):
        """Load a simulation object"""
        return load_simul(path, hide_stdout=True)


_dataframe_maker = DataframeMakerFoam()

get_mean_values_from_path = _dataframe_maker.get_mean_values_from_path
get_dataframe_from_paths = _dataframe_maker.get_dataframe_from_paths
