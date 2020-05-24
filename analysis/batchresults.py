from os.path import join

from typing import Dict

from base import ComputationalSpace

from config import IDMFConfig
from container import Domain

from .datastoreanalyser import DataStoreAnalyser

class BatchResults:

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
        self.thresholds = getattr(self.setting.thresholds, quantity)
        self.domain = Domain(setting)
        self.space = space
        self.quantity = quantity
        self.analysis = analysis
        self.outdir = outdir
        self.write()

    def write(self):
        with open(join(self.outdir, f"batch_{self.quantity}_extrema.txt"), 'w') as f:
            for geometry in BatchResults.geometries:
                over = []
                for setting, analysis in self.analysis.items():
                    items = [
                        i for i in analysis.maximum 
                        if i.geometry == geometry
                        and i.valid
                    ]
                    if items:
                        item = max(items)
                        item.setting = setting
                        over.append(item)
                if over:
                    item = max(over)
                    f.write(f"Maxium value for {geometry}:\n")
                    f.write(f"run id: {self.space.index(item.setting)}\n")
                    f.write(item.string(self.setting, self.domain))
            f.write("===================================\n")
            f.write("===================================\n\n")
            for t in self.thresholds:
                for geometry in BatchResults.geometries:
                    over = []
                    for setting, analysis in self.analysis.items():
                        items = [
                            i for i in analysis.exceedance
                            if i.geometry == geometry
                            and i.threshold == t.value
                            and i.valid
                        ]
                        if items:
                            item = min(items)
                            item.setting = setting
                            over.append(item)
                    if over:
                        item = min(over)
                        f.write(f"Minimum time to {t.value}{self.unit} for {geometry}\n")
                        f.write(f"run id: {self.space.index(item.setting)}\n")
                        f.write(item.string(self.setting, self.domain))
                f.write("===================================\n")
                f.write("===================================\n\n")
            p = self.setting.models.eddy_diffusion.analysis.percentage_exceedance
            for t in self.thresholds:
                for geometry in BatchResults.geometries:
                    over = []
                    for setting, analysis in self.analysis.items():
                        items = [
                            i for i in analysis.percent_exceedance
                            if i.geometry == geometry
                            and i.threshold == t.value
                            and i.valid
                        ]
                        if items:
                            item = min(items)
                            item.setting = setting
                            over.append(item)
                    if over:
                        item = min(over)
                        f.write(f"Minimum time to {t.value}{self.unit} for {p}% of domain for {geometry}\n")
                        f.write(f"run id: {self.space.index(item.setting)}\n")
                        f.write(item.string(self.setting, self.domain))
                f.write("===================================\n")
                f.write("===================================\n\n")
            for t in self.thresholds:
                for geometry in BatchResults.geometries:
                    over = []
                    for setting, analysis in self.analysis.items():
                        items = [
                            i for i in analysis.max_percent_exceedance
                            if i.geometry == geometry
                            and i.threshold == t.value
                            and i.valid
                        ]
                        if items:
                            item = max(items)
                            item.setting = setting
                            over.append(item)

                    if over:
                        item = max(over)
                        f.write(f"Maximum percentage exceeding {t.value}{self.unit} for {geometry}\n")
                        f.write(f"run id: {self.space.index(item.setting)}\n")
                        f.write(item.string(self.setting, self.domain))
                f.write("===================================\n")
                f.write("===================================\n\n")

    @property
    def unit(self):
        return getattr(self.setting, f"{self.quantity}_units")