from os.path import join

from io import TextIOWrapper

from typing import Dict
from typing import List
from typing import Type 

from ridt.base import RIDTOSError
from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig
from ridt.config import Units
from ridt.config import summary

from ridt.container import Domain

from .resultcontainers import ResultContainer
from .datastoreanalyser import DataStoreAnalyser

FIRST = 0

class BatchResultsWriter:
    """Batch results writer class.

    Iterates through a :obj:`dict` of :class:`~.DataStoreAnalyser` instances
    and computes batch run analysis quantites.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    space : :class:`~.ComputationalSpace`
        The :class:`~.ComputationalSpace` instance corresponding to the
        :attr:`settings` attribute.
    
    outdir: :obj:`str`
        The path to the output directory for the run.
    
    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    analysis : :obj:`dict` [:class:`~.RIDTConfig`, :class:`~.DataStoreAnalyser`]
        A dictionary of :class:`~.DataStoreAnalyser` instances for each
        :class:`~.RIDTConfig` object in :attr:`space`.
    
    thresholds : :obj:`list` [:obj:`float`]
        The threshold values corresponding to :attr:`quantity` defined in
        :attr:`setting`.
    
    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.

    """
    def __init__(self,
                 setting: RIDTConfig,
                 space: ComputationalSpace,
                 analysis: Dict[RIDTConfig, DataStoreAnalyser],
                 outdir: str,
                 quantity: str):
        """The :class`~.BatchResultsWriter` class initialiser.

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.

        space : :class:`~.ComputationalSpace`
            The :class:`~.ComputationalSpace` instance corresponding to the
            :attr:`settings` attribute.
        
        analysis : :obj:`dict` [:class:`~.RIDTConfig`, :class:`~.DataStoreAnalyser`]
            A dictionary of :class:`~.DataStoreAnalyser` instances for each
            :class:`~.RIDTConfig` object in :attr:`space`.

        outdir : :obj:`str`
            The path to the output directory for the run.

        quantity : :obj:`str`
            The string id for the quantity stored in the data  store.

       """
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

    def get_valid(self, geometry: str, results: List[Type[ResultContainer]]):
        return [i for i in results if i.geometry == geometry and i.valid]

    def write(self):
        """Computes and writes batch results to disk.

        loops through all items in :attr:`analysis` and for each geometry type
        writes the following information to the output file:

        The maximum value.

        The fastest time to all threshold values.

        The fastest time to the defined percentage of domain to all threshold
        values.

        The largest percentage that exceeds all threshold values.
        The 

        Each item for each geometry is written indicating which settings object
        it corresponds to.

        Raises
        ------
        :class:`~.RIDTOSError`
            If unable to create the output file on disk.

        """
        try:
            fname = f"batch_{self.quantity}_extrema.txt"
            f = open(join(self.outdir, fname), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        for geometry in self.geometries:
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
                for geometry in self.geometries:
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
        """Writes the run summary to the output folder.

        Raises
        ------
        :class:`~.RIDTOSError`  
            If unable to create the output file on disk.

        """
        try:
             f = open(join(self.outdir, "batch_run_summary.txt"), 'w')
        except OSError as e:
            raise RIDTOSError(e)

        f.write(self.space.cout_summary())
        f.write("\n")
        f.write(summary(self.setting))
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
        file.write("".join("=" for i in range(len(title))) + "\n")
        file.write(title + "\n")
        file.write("".join("=" for i in range(len(title))) + "\n")

    def subtitle(self, file: TextIOWrapper, subtitle: str):
        """Writes a formatted subtitle string to a file object.

        Parameters
        ----------
        file : :obj:`TextIOWrapper` 
            The file object to write to.

        title : :obj:`str`
            The subtitle string.
        
        Returns
        -------
        None
        """
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
        file.write(subtitle + "\n")
        file.write("".join("-" for i in range(len(subtitle))) + "\n")
