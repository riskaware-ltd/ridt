import csv

from io import TextIOWrapper

from os import mkdir

from os.path import join

from typing import Union
from typing import List
from typing import Iterable
from typing import Type

from numpy import sqrt

from ridt.base import RIDTOSError

from ridt.config import RIDTConfig
from ridt.config import Units
from ridt.config import summary

from ridt.container import Domain

from ridt.equation import EddyDiffusion

from ridt.data import DirectoryAgent

from .datastoreanalyser import DataStoreAnalyser

from .resultcontainers import Maximum
from .resultcontainers import Exceedance
from .resultcontainers import PercentExceedance
from .resultcontainers import MaxPercentExceedance
from .resultcontainers import ResultContainer

FIRST = 0


class ResultsWriter:


    def __init__(self,
                 setting: RIDTConfig,
                 analysis: DataStoreAnalyser,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        self.setting = setting
        self.units = Units(setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.analysis = analysis
        self.dir_agent = dir_agent 
        self.create_dirs()
        self.domain = Domain(setting)
        self.summary()
        self.maximum()
        self.exceedance_analysis()
        self.extrema()

    @property
    def geometries(self):
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def threshold_converter(self):
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)
    
    def create_dirs(self):
        for geometry in self.geometries:
            self.dir_agent.create_analysis_dir(geometry, self.quantity)

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

    def get_valid(self, geometry: str, results: List[Type[ResultContainer]]):
        return [i for i in results if i.geometry == geometry and i.valid]
    
    def maximum(self):
        for geometry in self.geometries:
            items = self.get_valid(geometry, self.analysis.maximum)
            items.sort(reverse=True)
            rows = [item.row for item in items]
            if rows:
                path = join(self.dir_agent.adir, items[FIRST].fname)
                self.write(path, items[FIRST].header, rows)

    def exceedance_analysis(self):
        results = [
            (self.analysis.exceedance, False),
            (self.analysis.percent_exceedance, False),
            (self.analysis.max_percent_exceedance, True)
        ]
        for r, reverse in results:
            for geometry in self.geometries:
                for t in self.thresholds:
                    valid = self.get_valid(geometry, r)
                    items = [i for i in valid if i.threshold == t]
                    items.sort(reverse=reverse)
                    rows = [item.row for item in items]
                    if rows:
                        path = join(self.dir_agent.adir, items[FIRST].fname)
                        self.write(path, items[0].header, rows)
    
    def extrema(self):
        try:
            fname = f"{self.quantity}_extrema.txt"
            f = open(join(self.dir_agent.outdir, fname), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        self.title(f, self.analysis.maximum[FIRST].title)
        for geometry in self.geometries:
            items = self.get_valid(geometry, self.analysis.maximum)
            self.subtitle(f, items[FIRST].extreme_title)
            if items:
                item = max(items)
                f.write(item.string)

        results = [
            (self.analysis.exceedance, False),
            (self.analysis.percent_exceedance, False),
            (self.analysis.max_percent_exceedance, True)
        ]

        for r, reverse in results:
            self.title(f, r[FIRST].title)
            for t in self.thresholds:
                for geometry in self.geometries:
                    valid = self.get_valid(geometry, r)
                    items = [i for i in valid if i.threshold == t]
                    if items:
                        self.subtitle(f, items[FIRST].extreme_title)
                        item = min(items) if not reverse else max(items)
                        f.write(item.string)
        f.close()

    def title(self, file: TextIOWrapper, title: str):
        file.write("".join("=" for i in range(len(title))) + "\n")
        file.write(title + "\n")
        file.write("".join("=" for i in range(len(title))) + "\n")

    def subtitle(self, file: TextIOWrapper, subtitle: str):
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
        file.write(subtitle + "\n")
        file.write("".join("-" for i in range(len(subtitle))) + "\n")

    def summary(self):
        try:
             f = open(join(self.dir_agent.outdir, "run_summary.txt"), 'w')
        except OSError as e:
            raise RIDTOSError(e)
    
        char_diff = self.characteristic_diffusion_time
        f.write("Characteristic diffusion times:\n")
        f.write(f"\tx: {char_diff['x']:.2f}{self.setting.time_units}\n")
        f.write(f"\ty: {char_diff['y']:.2f}{self.setting.time_units}\n")
        f.write(f"\tz: {char_diff['z']:.2f}{self.setting.time_units}\n")
        f.write(f"\tsqrt(V): {char_diff['v']:.2f}{self.setting.time_units}\n")
        f.write("\n")
        if self.setting.models.eddy_diffusion.monitor_locations.evaluate["domain"]:
            ttwm = self.analysis.time_to_well_mixed
            if ttwm:
                value =  f"{ttwm:.2f}{self.setting.time_units}\n"
            else:
                value = "not within lifetime of simulation\n"
        else:
            value = "domain data not available\n"
        f.write(f"Time to well mixed: {value}")
        f.write("\n")
        f.write(summary(self.setting))
        f.close()

    @property
    def characteristic_diffusion_time(self):
        solver = EddyDiffusion(self.setting)
        dim = self.setting.dimensions
        l = sqrt(dim.x * dim.y * dim.z)
        return {
            "x": dim.x * dim.x / solver.diff_coeff,
            "y": dim.y * dim.y / solver.diff_coeff,
            "z": dim.z * dim.z / solver.diff_coeff,
            "v": l * l / solver.diff_coeff
        }


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
   