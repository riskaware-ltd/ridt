import csv
import sys

from os.path import basename
from os.path import dirname

from ridt.base import Error

from ridt.config import ConfigFileParser
from ridt.config import ConfigFileWriter


class CSVToConfigFile:

    """Class which parsed a csv file and adds the entries to a config file.

    The CSV file must be of the following format:

    INS,float,float,float,float,float,
    INF,float,float,float,float,float,
    FIX,float,float,float,float,float,float
    POI,float,float,float,,,
    LIN,float,float,float,x,,
    PLA,xy,float,,,,

    Where many of each type of entry can exist.

    INS - instantaneous source.
    INF - infinite duration source.
    FIX - fixed duration
    POI - monitor point
    LIN - monitor line
    PLA - monitor plane.

    Attributes
    ----------
    csv_file_path : :obj:`str`
        The path to the csv file to be parsed.

    config_file_path : :obj:`str`
        The path to the config file to be parsed.
    
    output_file_path : :obj:`str`
        The path to save the new config file.
    
    parsed_items : :obj:`dict` [:obj:`str`, :obj:`list`]
        The items parsed from the CSV file.
    
    config : :class:`~.RIDTConfig`
        The instantiated settings object.
    
    new : :obj:`dict`
        The source dictionary for the old and new settings object.

    """

    def __init__(self):
        pass

    def __call__(self,
                 config_file_path: str,
                 csv_file_path: str,
                 output_file_path: str):
        """The CSVToConfigFile initialiser

        Parameters
        ----------
        csv_file_path : :obj:`str`
            The path to the csv file to be parsed.

        config_file_path : :obj:`str`
            The path to the config file to be parsed.
        
        output_file_path : :obj:`str`
            The path to save the new config file.
        
        """
        self.csv_file_path = csv_file_path
        self.config_file_path = config_file_path
        self.output_file_path = output_file_path
        self.parsed_items = {
            "INS": [],
            "INF": [],
            "FIX": [],
            "POI": [],
            "LIN": [],
            "PLA": []
        }
        self.config = ConfigFileParser(config_file_path)
        self.new = self.config.__source__
        self.parse_csv()
        self.write_new_config_file()

    def parse_csv(self):
        """Open and parse the entries in the CSV file.

        It adds the items to :attr:`parsed_items`

        Raises
        ------
        :class:`~.CSVToConfigFileOSError`
            If the csv file cannot be opened.

        """
        try:
            with open(self.csv_file_path, 'r') as f:
                c = csv.reader(f, delimiter=",")
                for row in c:
                    if row[0]:
                        if row[0] in self.parsed_items:
                            self.parsed_items[row[0]].append(
                                [item for item in row[1:] if item != ""])
                        else:
                            print(f"Invalid spec: {row[0]}")
        except OSError as e:
            raise CSVToConfigFileOSError(self.csv_file_path, e)
        try:
            self.add_INS()
            self.add_INF()
            self.add_FIX()
            self.add_POI()
            self.add_LIN()
            self.add_PLA()
        except CSVToConfigFileValueError as e:
            sys.exit(e)
        except CSVToConfigFileIndexError as e:
            sys.exit(e)

    def add_INS(self):
        """Add the parsed INS items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.

        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["INS"]):
            try:
                self.new["modes"]\
                        ["instantaneous"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "mass": float(item[3]),
                    "time": float(item[4])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("INS", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("INS", self.ord(idx), 5)

    def add_INF(self):
        """Add the parsed INF items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.

        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["INF"]):
            try:
                self.new["modes"]\
                        ["infinite_duration"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "rate": float(item[3]),
                    "time": float(item[4])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("INF", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("INF", self.ord(idx), 5)

    def add_FIX(self):
        """Add the parsed FIX items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.

        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["FIX"]):
            try:
                self.new["modes"]\
                        ["fixed_duration"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "rate": float(item[3]),
                    "start_time": float(item[4]),
                    "end_time": float(item[5])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("FIX", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("FIX", self.ord(idx), 6)
    
    def add_POI(self):
        """Add the parsed POI items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.

        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["POI"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["points"]\
                        [f"point_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("POI", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("POI", self.ord(idx), 3)
    
    def add_LIN(self):
        """Add the parsed LIN items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.
            
        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["LIN"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["lines"]\
                        [f"line_{idx}"] = {
                    "point": {
                        "x": float(item[0]),
                        "y": float(item[1]),
                        "z": float(item[2]),
                    },
                    "axis": item[3]
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("LIN", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("LIN", self.ord(idx), 6)
    
    def add_PLA(self):
        """Add the parsed PLA items to the source dictionary :attr:`new`

        Returns
        -------
        None

        Raises
        ------
        :class:`~.CSVToConfigFileValueError`
            If the parsed data is of the incorrect type.

        :class:`~.CSVToConfigFileIndexError`    
            If an incorrect number of items were in a given row parsed from the
            CSV file.

        """
        for idx, item in enumerate(self.parsed_items["PLA"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["planes"]\
                        [f"plane_{idx}"] = {
                    "axis": str(item[0]),
                    "distance": float(item[1])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("PLA", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("PLA", self.ord(idx), 2)
    
    def write_new_config_file(self):
        if not self.output_file_path:
            path = self.append_id(self.config_file_path)
        else:
            path = self.output_file_path
        
        ConfigFileWriter(dirname(path), basename(path), self.new)

    def ord(self, n: int):
        """Returns the correct order suffix for a given integer.

        Parameters
        ----------
        n : :obj:`int`
            The integer in question.

        Returns
        -------
        :obj:`str`
            The order suffix.
            
        """
        return str(n)+("th" if 4<=n%100<=20 else {1:"st", 2:"nd", 3:"rd"}\
            .get(n%10, "th"))

    def append_id(self, filename: str):
        """Add a 'new' suffix to the file name before the file extension.

        Parameters
        ----------
        filename : :obj:`str`
            The file name to be extended.

        Returns
        -------
        :obj:`str`
            The new file name.

        """
        return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + ["new"]) 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CSVToConfigFileOSError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches an error when parsing a csv file path.

    """
    def __init__(self, path: str, error: OSError):
        """The constructor for the :class:`CSVToConfigFileOSError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}"
        super().__init__(msg)


class CSVToConfigFileValueError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches a ValueError error when parsing a csv file.

    """
    def __init__(self, geometry: str, index: int):
        """The constructor for the :class:`CSVToConfigFileValueError` class.

        """
        msg = f"While loading the {index} {geometry} item, one of the parsed "\
              f"items was of an incorrect type."
        super().__init__(msg)


class CSVToConfigFileIndexError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches an IndexError error when parsing a csv file.

    """
    def __init__(self, geometry: str, index: str, expected: int):
        """The constructor for the :class:`CSVToConfigFileIndexError` class.

        """
        msg = f"While loading the {index} {geometry} item, not enough "\
              f"values were found. Expecting {expected}"
        super().__init__(msg)
