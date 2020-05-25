from os.path import join

from io import TextIOWrapper

from typing import Dict
from typing import List
from typing import Type 

from base import RIDTOSError
from base import ComputationalSpace

from config import IDMFConfig
from config import Units
from config import summary

from container import Domain

from .resultcontainers import ResultContainer
from .datastoreanalyser import DataStoreAnalyser

FIRST = 0

class BatchResultsWriter:

    geometries = [
        "points",
        "lines",
        "planes",
        "domain"
    ]

    def __init__(self,
                 setting: IDMFConfig,
                 space: ComputationalSpace,
                 analysis: Dict[IDMFConfig, DataStoreAnalyser],
                 outdir: str,
                 quantity: str):
        self.setting = setting
        self.domain = Domain(setting)
        self.units = Units(setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.space = space
        self.analysis = analysis
        self.outdir = outdir
        self.summary()
        self.write()

    def threshold_converter(self):
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def get_valid(self, geometry: str, results: List[Type[ResultContainer]]):
        return [i for i in results if i.geometry == geometry and i.valid]

    def write(self):
        try:
            fname = f"batch_{self.quantity}_extrema.txt"
            f = open(join(self.outdir, fname), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        for geometry in BatchResultsWriter.geometries:
            over = list()
            for setting, analysis in self.analysis.items():
                items = self.get_valid(geometry, analysis.maximum)
                if items:
                    item = max(items)
                    over.append(item)
            if over:
                item = max(over)
                self.subtitle(f, item.extreme_title)
                f.write(f"run id: {self.space.index(item.setting)}\n")
                f.write(item.string)

        results = [
            ("exceedance", False),
            ("percent_exceedance", False),
            ("max_percent_exceedance", True)
        ]

        for r, reverse in results:
            for t in self.thresholds:
                for geometry in BatchResultsWriter.geometries:
                    over = list()
                    for setting, analysis in self.analysis.items():
                        valid = self.get_valid(geometry, getattr(analysis, r))
                        items = [i for i in valid if i.threshold == t]
                        if items:
                            item = min(items) if not reverse else max(items)
                            over.append(item)
                    if over:
                        item = min(over) if not reverse else max(over)
                        self.subtitle(f, item.extreme_title)
                        f.write(f"run id: {self.space.index(item.setting)}\n")
                        f.write(item.string)
        f.close()
    
    def summary(self):
        try:
             f = open(join(self.outdir, "batch_run_summary.txt"), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        f.write(self.space.cout_summary())
        f.write("\n")
        f.write(summary(self.setting))
        f.close()

    def title(self, file: TextIOWrapper, title: str):
        file.write("".join("=" for i in range(len(title))) + "\n")
        file.write(title + "\n")
        file.write("".join("=" for i in range(len(title))) + "\n")

    def subtitle(self, file: TextIOWrapper, subtitle: str):
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
        file.write(subtitle + "\n")
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
