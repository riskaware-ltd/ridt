import csv

from os import mkdir

from os.path import join

from typing import Union
from typing import List
from typing import Iterable

from base import RIDTOSError

from config import IDMFConfig
from config import Units

from container import Domain

from data import DirectoryAgent

from .datastoreanalyser import DataStoreAnalyser

from .resultcontainers import Maximum
from .resultcontainers import Exceedance
from .resultcontainers import PercentExceedance
from .resultcontainers import MaxPercentExceedance

class ResultsWriter:


    def __init__(self,
                 setting: IDMFConfig,
                 analysis: DataStoreAnalyser,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        self.setting = setting
        self.units = Units(setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.analysis = analysis
        self.dir_agent = dir_agent 
        self.domain = Domain(setting)
        self.maximum()
        self.exceedance()
        self.percent_exceedance()
        self.max_percent_exceedance()
        self.extrema()

    def threshold_converter(self):
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def write(self, file_path: str, header: List[str], lines: Iterable):
        try:
            f = open(file_path, 'w', newline="")
        except OSError as e:
            raise RIDTOSError(e)

        writer = csv.writer(f, delimiter=",")
        writer.writerow(header)
        for line in lines:
            writer.writerow(line)
        f.close()
    

    def maximum(self):
        for geometry in self.analysis.data_store.geometries:
            items = [
                i for i in self.analysis.maximum
                if i.geometry == geometry
                and i.valid
            ]
            items.sort(reverse=True)
            self.dir_agent.create_analysis_dir(geometry, self.quantity)
            fname = f"{geometry}_maximums.csv"
            path = join(self.dir_agent.adir, fname)
            rows = [item.row(self.domain) for item in items]
            if rows:
                self.write(path, items[0].header(self.setting), rows)


    def exceedance(self):
        for geometry in self.analysis.data_store.geometries:
            for t in self.thresholds:
                items = [
                    i for i in self.analysis.exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                items.sort()
                fname = f"{geometry}_exceeds_{t}{self.unit}.csv"
                self.dir_agent.create_analysis_dir(geometry, self.quantity)
                path = join(self.dir_agent.adir, fname)
                rows = [item.row(self.domain) for item in items]
                if rows:
                    self.write(path, items[0].header(self.setting), rows)
            
    def percent_exceedance(self):

        for geometry in self.analysis.data_store.geometries:
            for t in self.thresholds:
                items = [
                    i for i in self.analysis.percent_exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                items.sort()
                fname = f"{geometry}_exceeds_{t}{self.unit}.csv"
                self.dir_agent.create_analysis_dir(geometry, self.quantity)
                path = join(self.dir_agent.adir, fname)
                rows = [item.row(self.domain) for item in items]
                if rows:
                    self.write(path, items[0].header(self.setting), rows)
            
    def max_percent_exceedance(self):

        for geometry in self.analysis.data_store.geometries:
            for t in self.thresholds:
                items = [
                    i for i in self.analysis.max_percent_exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                items.sort()
                fname = f"{geometry}_max%_exceeds_{t}{self.unit}.csv"
                self.dir_agent.create_analysis_dir(geometry, self.quantity)
                path = join(self.dir_agent.adir, fname)
                rows = [item.row(self.domain) for item in items]
                if rows:
                    self.write(path, items[0].header(self.setting), rows)
    
    def extrema(self):
        try:
            f = open(join(self.dir_agent.outdir, f"{self.quantity}_extrema.txt"), 'w')
        except OSError as e:
            raise RIDTOSError(e)
        for geometry in self.analysis.data_store.geometries:
            items = [
                i for i in self.analysis.maximum 
                if i.geometry == geometry
                and i.valid
            ]
            if items:
                item = max(items)
                f.write(f"Maxium value for {geometry}:\n")
                f.write(item.string(self.setting, self.domain))
        f.write("===================================\n")
        f.write("===================================\n\n")
        for t in self.thresholds:
            for geometry in self.analysis.data_store.geometries:
                items = [
                    i for i in self.analysis.exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                if items:
                    item = min(items)
                    f.write(f"Minimum time to {t}{self.unit} for {geometry}\n")
                    f.write(item.string(self.setting, self.domain))
            f.write("===================================\n")
            f.write("===================================\n\n")
        p = self.setting.models.eddy_diffusion.analysis.percentage_exceedance
        for t in self.thresholds:
            for geometry in self.analysis.data_store.geometries:
                items = [
                    i for i in self.analysis.percent_exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                if items:
                    item = min(items)
                    f.write(f"Minimum time to {t}{self.unit} for {p}% of domain for {geometry}\n")
                    f.write(item.string(self.setting, self.domain))
            f.write("===================================\n")
            f.write("===================================\n\n")
        for t in self.thresholds:
            for geometry in self.analysis.data_store.geometries:
                items = [
                    i for i in self.analysis.max_percent_exceedance
                    if i.geometry == geometry
                    and i.threshold == t
                    and i.valid
                ]
                if items:
                    item = max(items)
                    f.write(f"Maximum percentage exceeding {t}{self.unit} for {geometry}\n")
                    f.write(item.string(self.setting, self.domain))
            f.write("===================================\n")
            f.write("===================================\n\n")
        f.close()

    @property
    def unit(self):
        return getattr(self.units, f"{self.quantity}_si")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
   