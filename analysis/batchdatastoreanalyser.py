import sys

from os.path import join

from base import ComputationalSpace

from config import IDMFConfig

from data import BatchDataStore

from .datastoreanalyser import DataStoreAnalyser

from config import summary

from pprint import pprint


class BatchDataStoreAnalyser:

    def __init__(self,
                 settings: IDMFConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace):
        self.settings = settings
        self.data_store = data_store
        self.space = space
        self.analysed_stores = dict()
        for setting, store in self.data_store.items():
            self.analysed_stores[setting] = DataStoreAnalyser(setting, store)
        self.output = str()
        self.max_exposure()
        self.exceeds_exposure(1.0)
    
    def max_exposure(self):
        max_value = 0.0
        max_setting = None
        max_location = None
        for setting, analysis in self.analysed_stores.items():
            location, value = analysis.max_exposure()
            if value > max_value:
                max_setting = setting
                max_value = value
                max_location = location
        rv = str()
        rv += "Maximum Exposure\n"
        rv += "================\n"
        rv += "\n"
        rv += f"The point in computational space that recorded the maximum exposure:\n\n"
        rv += f"{self.space.index(max_setting)}\n"
        rv += f"max_value: {value}\n"
        rv += f"location: {max_location}"
        rv += "\n"
        
        return rv
    
    def exceeds_exposure(self, value: float):
        exceeds = dict()
        for setting, analysis in self.analysed_stores.items():
            exceedance = analysis.exceeds_exposure(value)
            if exceedance:
                exceeds[setting] = exceedance
        fastest_value = sys.float_info.max
        fastest_setting = None
        fastest_name = None
        for setting, exceed in exceeds.items():
            name, time = exceed.min()
            if  time < fastest_value:
                fastest_name = name
                fastest_value = time
                fastest_setting = setting

        rv = str()
        rv += "\nExposure Exceedance\n"
        rv += "===================\n"
        rv += "\n"

        rv += f"Points in computational space that exceed {value} {self.settings.exposure_units}:\n\n"
        for setting, exceed in exceeds.items():
            rv += f"{self.space.index(setting)}\n"
            for name, time in exceed.points.items():
                rv += f"\t{name}: {time}{self.settings.time_units}\n"
            for name, time in exceed.lines.items():
                rv += f"\t{name}: {time}{self.settings.time_units}\n"
            for name, time in exceed.planes.items():
                rv += f"\t{name}: {time}{self.settings.time_units}\n"
            if exceed.domain:
                rv += f"\tdomain: {exceed.domain}\n"
        rv += "\n"
        rv += f"The point in computational space that exceeded {value} {self.settings.exposure_units} the fastest:\n\n"
        rv += f"{self.space.index(fastest_setting)}\n"
        rv += f"\t{fastest_name}: {fastest_value}{self.settings.time_units}\n"
        rv += "\n"
            
        return rv

    def shortest_exceeds_exposure(self, value: float):
        pass

    def write(self, outdir: str):
        if self.space.zero:
            pass
        else:
            with open(join(outdir, "analysis.txt"), 'w') as f:
                f.write(self.space.cout_summary())
                f.write("\n")
                f.write(self.max_exposure())
                f.write(self.exceeds_exposure(0.0))
