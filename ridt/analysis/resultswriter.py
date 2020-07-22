import csv

from io import TextIOWrapper

from os.path import join

from typing import List
from typing import Iterable
from typing import Type

from ridt.base import RIDTOSError

from ridt.config import RIDTConfig
from ridt.config import Units
from ridt.config import summary

from ridt.container import Domain

from ridt.equation import EddyDiffusion

from ridt.data import DirectoryAgent

from .datastoreanalyser import DataStoreAnalyser

from .resultcontainers import ResultContainer


class ResultsWriter:
    """The Results Writer class.

    Iterates through all selected geometries and writes all quantities to disk.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    analysis : :class:`~.DataStoreAnalyser`
        :class:`~.DataStoreAnalyser` instance to be written.

    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    thresholds : :obj:`list` [:obj:`float`]
        The threshold values corresponding to :attr:`quantity` defined in
        :attr:`setting`.
    
    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.

    dir_agent: :class:`~.DirectoryAgent`
        The directory agent for run.

    """ 
    def __init__(self,
                 setting: RIDTConfig,
                 analysis: DataStoreAnalyser,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        """The :class`~.ResultsWriter` class initialiser.

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.

        analysis : :class:`~.DataStoreAnalyser`
            :class:`~.DataStoreAnalyser` instance to be written.

        dir_agent: :class:`~.DirectoryAgent`
            The directory agent for run.

        quantity : :obj:`str`
            The string id for the quantity stored in the data  store.

       """
        self.setting = setting
        self.units = Units(setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.analysis = analysis
        self.dir_agent = dir_agent 
        self.domain = Domain(setting)
        if quantity == "concentration":
            self.summary()
        self.maximum()
        self.exceedance_analysis()
        self.extrema()

    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`setting`.

        """
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def threshold_converter(self):
        """Converts the threshold into SI units.

        Converts the thresholds in :attr:`setting` corresponding to
        :attr:`quantity` into SI units.

        Returns
        -------
        :obj:`list` [:obj:`float`]
            The list of threshold values in SI units. 
        """
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def write(self, file_path: str, header: List[str], lines: Iterable) -> None:
        """Write array of values to csv file.

        Parameters
        ----------
        file_path : :obj:`str`
            The path to save the data to.
        header : :obj:`list` [:obj:`str`]
            The header for the csv file.
        lines : Iterable
            The array of values to be written to the csv file.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.RIDTOSError`
            If cannot create file on disk.

        """
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
        """Filter valid results for a given geometry from list of results.

        Parameters
        ----------
        geometry : :obj:`str`
            The geometry in to filter for.

        results : :obj:`list` [:class:`~.ResultContainer`]
            The list of :class:`~.ResultConainer`.

        Returns
        -------
        :obj:`list` [:class:`~.ResultContainer`]
            The filtered list of :class:`~.ResultConainer`.
        
        """
        return [i for i in results if i.geometry == geometry and i.valid]
    
    def maximum(self):
        """Write the relevant :class:`~.Maximum` results to file.
    
        Loops through all geometries and writes the Maximum results to
        a csv file.

        Returns
        -------
        None
        
        """ 
        for geometry in self.geometries:
            self.dir_agent.create_analysis_dir(geometry, self.quantity)
            items = self.get_valid(geometry, self.analysis.maximum)
            items.sort(reverse=True)
            rows = [item.row for item in items]
            if rows:
                path = join(self.dir_agent.adir, items[0].fname)
                self.write(path, items[0].header, rows)

    def exceedance_analysis(self):
        """Write the relevant exceedance results to file.
    
        Loops through all geometries and writes the :class:`~.Exceedance`,
        :class:`~.PercentExceedance`, and :class:`~.MaxPercentExceedance`
        results to a csv file.

        Returns
        -------
        None
        
        """
        results = [
            (self.analysis.exceedance, False),
            (self.analysis.percent_exceedance, False),
            (self.analysis.max_percent_exceedance, True)
        ]
        for r, reverse in results:
            for geometry in self.geometries:
                self.dir_agent.create_analysis_dir(geometry, self.quantity)
                for t in self.thresholds:
                    valid = self.get_valid(geometry, r)
                    items = [i for i in valid if i.threshold == t]
                    items.sort(reverse=reverse)
                    rows = [item.row for item in items]
                    if rows:
                        path = join(self.dir_agent.adir, items[0].fname)
                        self.write(path, items[0].header, rows)
    
    def extrema(self):
        """Computes and writes extrema results to disk.

        loops through all items in :attr:`analysis` and for each geometry type
        writes the following information to the output file:

        The maximum value.

        The fastest time to all threshold values.

        The fastest time to the defined percentage of domain to all threshold
        values.

        The largest percentage that exceeds all threshold values.
        The 

        Raises
        ------
        :class:`~.RIDTOSError`
            If unable to create the output file on disk.

        """
        try:
            fname = f"{self.quantity}_extrema.txt"
            f = open(join(self.dir_agent.outdir, fname), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        self.title(f, self.analysis.maximum[0].title)
        for geometry in self.geometries:
            items = self.get_valid(geometry, self.analysis.maximum)
            self.subtitle(f, self.analysis.maximum[0].extreme_title)
            if items:
                item = max(items)
                f.write(item.string)

        results = [
            (self.analysis.exceedance, False),
            (self.analysis.percent_exceedance, False),
            (self.analysis.max_percent_exceedance, True)
        ]

        for r, reverse in results:
            self.title(f, r[0].title)
            for t in self.thresholds:
                for geometry in self.geometries:
                    valid = self.get_valid(geometry, r)
                    items = [i for i in valid if i.threshold == t]
                    if items:
                        self.subtitle(f, items[0].extreme_title)
                        item = min(items) if not reverse else max(items)
                        f.write(item.string)
        f.close()

    def title(self, file: TextIOWrapper, title: str):
        """Writes a formatted title string to a file object.

        Parameters
        ----------
        file : :obj:`TextIOWrapper` 
            The file object to write to.

        title : :obj:`str`
            The title string.

        Returns
        -------
        None

        """
        file.write("\n")
        file.write("".join("=" for i in range(len(title))) + "\n")
        file.write(title + "\n")
        file.write("".join("=" for i in range(len(title))) + "\n")

    def subtitle(self, file: TextIOWrapper, subtitle: str):
        """Writes a formatted subtitle string to a file object.

        Parameters
        ----------
        file : :obj:`TextIOWrapper` 
            The file object to write to.

        subtitle : :obj:`str`
            The subtitle string.
        
        Returns
        -------
        None
        """
        file.write("\n")
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
        file.write(subtitle + "\n")
        file.write("".join("-" for i in range(len(subtitle))) + "\n")

    def summary(self):
        """Saves a run summary to a text file in the run output directory.

        Raises
        ------
        :class:`~.RIDTOSError`
            If unable to create the output file on disk.

        """
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
                value = f"{ttwm:.2f}{self.setting.time_units}\n"
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
        """:obj:`dict` [:obj:`str`, :obj:`float`] : the characteristic 
        diffusion times for all dimensions.

        """
        solver = EddyDiffusion(self.setting)
        dim = self.setting.dimensions
        l = pow(dim.x * dim.y * dim.z, 1.0 / 3.0)
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
   